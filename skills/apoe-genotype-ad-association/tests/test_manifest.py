"""Expectations transcribed from Belloy et al. 2023 before implementation.

Table = main article; supplementary PDF pages 36, 43, 46. These are lookup
reproductions, not a re-estimation of regression coefficients or absolute risk.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as report
import presets


def run(tmp_path, genotype="34", group="nhw", sex="female", analysis="case-control",
        age="65", ancestry=None, value=None, unit="%"):
    out = tmp_path / "out"
    args = ["--out", str(out), "--analysis", analysis]
    for flag, val in (("--genotype", genotype), ("--group", group), ("--sex", sex),
                      ("--age", age), ("--ancestry", ancestry)):
        if val is not None:
            args += [flag, val]
    if value is not None:
        path = tmp_path / "measurements.csv"
        path.write_text(f"marker,value,unit\n全基因组祖源比例,{value},{unit}\n", encoding="utf-8")
        args += ["--measurements", str(path)]
    process = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"), *args],
                             capture_output=True, text=True)
    payload = json.loads((out / "result.json").read_text())
    result = {k: v["value"] for k, v in payload["outputs"].items()}
    return process.returncode, result, out


def triple(result):
    return tuple(result[k] for k in ("effect", "ci_low", "ci_high"))


def test_main_table_printed_sex_strata(tmp_path):
    # Main Table: APOE*34, female; NHW / NHB / Hispanic OR (95% CI).
    for group, expected in [("nhw", (3.54, 3.29, 3.80)),
                            ("nhb", (2.17, 1.85, 2.54)),
                            ("hispanic", (1.97, 1.67, 2.33))]:
        code, result, out = run(tmp_path, group=group)
        assert code == 0
        assert triple(result) == expected
        assert result["effect_type"] == "OR"
        text = (out / "report.md").read_text()
        assert text.index("10.1001/jamaneurol.2023.3599") < text.index("## 你的输入")
        assert presets.BOUNDARY in text
        assert "年龄未分层" in text and "绝对概率" in text


def test_etable6_printed_east_asian(tmp_path):
    # eTable 6: APOE *34 4,164 4.54 [3.99, 5.17].
    code, result, _ = run(tmp_path, group="east_asian", sex="pooled")
    assert code == 0
    assert triple(result) == (4.54, 3.99, 5.17)
    # eTable 6: APOE *22+23 1,230 0.97 [0.77, 1.23].
    for genotype in ("22", "23"):
        code, result, _ = run(tmp_path, group="east_asian", sex="pooled", genotype=genotype)
        assert code == 0 and triple(result) == (0.97, 0.77, 1.23)
        assert result["genotype_stratum"] == "22+23"


def test_etable13_printed_survival(tmp_path):
    # eTable 13, APOE *44, females: NHW 5.53 [5.13, 5.96];
    # NHB 6.01 [5.00, 7.22]; Hispanic 3.70 [2.92, 4.68].
    for group, expected in [("nhw", (5.53, 5.13, 5.96)),
                            ("nhb", (6.01, 5.00, 7.22)),
                            ("hispanic", (3.70, 2.92, 4.68))]:
        code, result, _ = run(tmp_path, genotype="44", group=group, analysis="survival")
        assert code == 0 and triple(result) == expected
        assert result["effect_type"] == "HR"


def test_etable16_printed_ancestry(tmp_path):
    # eTable 16: Global Population Ancestry Proportion >75%, APOE *34:
    # EUR 3.43 [3.25, 3.63]; AFR 2.10 [1.80, 2.45]; AMR 2.15 [1.31, 3.51].
    for ancestry, expected in [("european", (3.43, 3.25, 3.63)),
                               ("african", (2.10, 1.80, 2.45)),
                               ("amerindian", (2.15, 1.31, 3.51))]:
        code, result, _ = run(tmp_path, group=None, sex="pooled", analysis="ancestry",
                              ancestry=ancestry, value="80")
        assert code == 0 and triple(result) == expected


def test_reference_has_no_invented_ci(tmp_path):
    code, result, out = run(tmp_path, genotype="ε3/ε3")
    assert code == 0 and triple(result) == (1, None, None)
    assert "不表示不会患病" in (out / "report.md").read_text()


@pytest.mark.parametrize("changes", [
    {"age": None}, {"age": "55"}, {"age": "-5"}, {"age": "nan"},
    {"genotype": None}, {"genotype": "4"}, {"genotype": "35"},
    {"group": None}, {"group": "chinese"}, {"sex": None}, {"sex": "unknown"},
    {"group": "east_asian", "sex": "female"},
    {"group": "east_asian", "sex": "pooled", "analysis": "survival"},
    {"analysis": "survival", "age": "90"},
])
def test_missing_wrong_or_unpublished_inputs(tmp_path, changes):
    code, result, out = run(tmp_path, **changes)
    assert code == 3 and all(v is None for v in result.values())
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert presets.BOUNDARY in (out / "report.md").read_text()


@pytest.mark.parametrize("value,unit", [("80", "mg/dL"), ("101", "%"),
                                       ("75", "%"), ("0.8", "1"), (None, "%")])
def test_ancestry_units_ranges_and_exact_cutoff(tmp_path, value, unit):
    code, result, out = run(tmp_path, analysis="ancestry", group=None, sex="pooled",
                           ancestry="european", value=value, unit=unit)
    assert code == 3 and result["effect"] is None
    assert (out / "problems.json").exists()


def test_ancestry_unestimable_and_no_mixing(tmp_path):
    # eTable16 prints 0.00 [0.00, Inf] for AMR APOE*22 and *24, not a usable zero risk.
    for genotype in ("22", "24"):
        code, result, _ = run(tmp_path, analysis="ancestry", group=None, sex="pooled",
                              ancestry="amerindian", value="80", genotype=genotype)
        assert code == 3 and result["effect"] is None
    code, _, _ = run(tmp_path, analysis="ancestry", group="nhw", sex="pooled",
                     ancestry="european", value="80")
    assert code == 3


def test_age_does_not_interpolate_and_genotype_normalizes(tmp_path):
    code, a, _ = run(tmp_path, age="60", genotype="APOE ε4/ε3")
    code2, b, _ = run(tmp_path, age="80", genotype="3/4")
    assert code == code2 == 0 and triple(a) == triple(b) == (3.54, 3.29, 3.80)


def test_manifest_and_frozen_rows():
    manifest = json.loads((ROOT / "skill.json").read_text())
    units = {x["key"]: x["unit"] for x in manifest["inputs"] if "unit" in x}
    assert units == presets.INPUT_UNITS
    assert manifest["entry"].get("targets_flag") is None
    assert manifest["validation"]["status"] == "reproduced"
    rows = report.load_rows()
    keys = [(r["analysis"], r["group"], r["sex"], r["genotype"]) for r in rows]
    assert len(keys) == len(set(keys))
    for r in rows:
        if r["status"] == "estimate":
            assert 0 < r["ci_low"] <= r["effect"] <= r["ci_high"]
            assert r["source"] and r["printed_cells"]
