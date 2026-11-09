"""Manifest, constants and input handling; reproduction of the authors' published demo output.

The paper's Code availability names github.com/oliversion/epg-aging. Its demo/output.csv
(commit 6a3cb44) prints the DVP_DMP_450K score for each sample of demo/demo_data.csv, and
README.md prints the same score for the first sample rounded to 4 decimals. The fixture
tests/fixtures/epg_aging_demo_450k.csv holds those samples' beta values at the 598 CpGs
of the 450K model, copied unchanged from demo/demo_data.csv.
"""

import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import (DISTINCT_CPGS_EPIC, S14_N_CPGS_450K, S14_N_CPGS_EPIC, load_model, model_cpgs)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
FIXTURE = ROOT / "tests" / "fixtures" / "epg_aging_demo_450k.csv"


def _demo(sample: str) -> dict[str, str]:
    with FIXTURE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["sample"] == sample:
                return {k: v for k, v in row.items() if k != "sample"}
    raise KeyError(sample)


def _run(tmp_path: Path, rows, *extra):
    tmp_path.mkdir(parents=True, exist_ok=True)
    table = tmp_path / "m.csv"
    table.write_text("item,value,unit\n" + "".join(f"{k},{v},{u}\n" for k, v, u in rows), encoding="utf-8")
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(table), "--out", str(out), *extra])
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    return code, (out / "report.md").read_text(encoding="utf-8"), result, out


def test_reproduces_author_demo_output_450k(tmp_path: Path):
    printed = {"2025": 69.7652073414805, "2090": 60.9704121365349}   # demo/output.csv, DVP_DMP_450K
    for sample, expected in printed.items():
        rows = [(cpg, beta, "") for cpg, beta in _demo(sample).items()]
        code, _text, result, _ = _run(tmp_path / sample, rows)
        assert code == 0
        assert result["dmp_dvp_450k_score"]["value"] == pytest.approx(expected, abs=1e-9)
        assert result["dmp_dvp_score"]["value"] is None          # 450K data lacks EPIC-only CpGs
    rows = [(cpg, beta, "") for cpg, beta in _demo("2013").items()]
    code, _text, result, _ = _run(tmp_path / "2013", rows)
    assert code == 0
    assert result["dmp_dvp_450k_score"]["value"] == pytest.approx(55.6395, abs=5e-5)   # README.md, ID001


def test_cpg_counts_match_table_s14_and_note_2():
    epic, k450 = load_model("epic"), load_model("450k")
    assert {k: len(v) for k, v in epic["weights"].items()} == S14_N_CPGS_EPIC
    assert {k: len(v) for k, v in k450["weights"].items()} == S14_N_CPGS_450K
    assert len(model_cpgs(epic)) == DISTINCT_CPGS_EPIC == 789


def test_constants_are_table_s15():
    epic = load_model("epic")
    assert epic["intercept"] == {"FI": -0.15806234736347, "CF": -1.75372181587638, "PF": -1.31664096495889}
    assert epic["cox"] == {"FI": 16.9441039026331, "CF": 1.24810702185552, "PF": 2.92511985505784}
    assert epic["transform"] == {"mean_bio": 3.53670610992843, "sd_bio": 0.937730597715799,
                                 "mean_age": 63.243813015582, "sd_age": 10.214001261888}
    assert epic["weights"]["FI"]["cg00303773"] == -0.00362015478067811


def test_manifest_keys_match_the_models():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    epic, k450 = model_cpgs(load_model("epic")), model_cpgs(load_model("450k"))
    assert keys[:-1] == epic + [c for c in k450 if c not in set(epic)]
    assert keys[-1] == "age"
    for spec in MANIFEST["inputs"][:-1]:
        assert spec["from"] == "measurements" and spec["required"] is False
        assert skillkit.normalize_unit(spec["unit"]) == "1" and spec["range"] == [0, 1]
    assert [o["key"] for o in MANIFEST["outputs"]] == ["dmp_dvp_score", "dmp_dvp_450k_score"]


def test_epic_model_all_half(tmp_path: Path):
    # beta 0.5 -> M 0, so each health score is its intercept.
    epic = load_model("epic")
    rows = [(cpg, 0.5, "") for cpg in model_cpgs(epic)]
    code, text, result, _ = _run(tmp_path, rows, "--age", "60")
    assert code == 0
    raw = sum(epic["cox"][k] * epic["intercept"][k] for k in ("FI", "CF", "PF"))
    t = epic["transform"]
    expected = (raw - t["mean_bio"]) / t["sd_bio"] * t["sd_age"] + t["mean_age"]
    assert result["dmp_dvp_score"]["value"] == pytest.approx(expected)
    assert f"{expected:.1f}" in text
    assert result["dmp_dvp_450k_score"]["value"] is None


def test_percent_unit_exits_3(tmp_path: Path):
    rows = [(cpg, 50, "%") for cpg in _demo("2025")]
    code, text, result, out = _run(tmp_path, rows)
    assert code == 3 and (out / "problems.json").exists()
    assert result["dmp_dvp_450k_score"]["value"] is None
    assert "69.7" not in text


def test_m_value_out_of_range_exits_3(tmp_path: Path):
    rows = [(cpg, beta, "") for cpg, beta in _demo("2025").items()]
    rows[0] = (rows[0][0], -2.3, "")
    code, _text, result, _ = _run(tmp_path, rows)
    assert code == 3
    assert result["dmp_dvp_450k_score"]["value"] is None


def test_beta_of_one_exits_3(tmp_path: Path):
    rows = [(cpg, beta, "") for cpg, beta in _demo("2025").items()]
    rows[0] = (rows[0][0], 1, "")
    code, text, _result, _ = _run(tmp_path, rows)
    assert code == 3
    assert rows[0][0] in text


def test_missing_site_exits_3_without_imputing(tmp_path: Path):
    rows = [(cpg, beta, "") for cpg, beta in _demo("2025").items()][1:]
    code, text, result, out = _run(tmp_path, rows)
    assert code == 3
    assert result["dmp_dvp_450k_score"]["value"] is None
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert [p["key"] for p in problems] == [list(_demo("2025"))[0]]
    assert "缺 1 个" in text
