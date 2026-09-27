"""epiage end to end: personal_report.py -> vendored compute_clocks.py -> report.md and result.json.

Anchors come from references/model-audit.md (synthetic inputs, all model CpGs
at beta 0.5, so nothing is imputed). compute_clocks.py rounds every value it
prints to 2 decimals (`round(v, 2)`), so values read back from result.json are
checked to 0.005; the unrounded model is checked to 1e-6 by calling the
vendored predict_linear directly, as upstream's own tests do.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")
pytest.importorskip("numpy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report  # noqa: E402
import skillkit  # noqa: E402

_spec = importlib.util.spec_from_file_location("epiage_clocks_under_test", ROOT / "scripts" / "compute_clocks.py")
clocks = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clocks)

ROUNDED = 0.005 + 1e-9  # compute_clocks.py prints round(value, 2)
DNAMTL = {0.0: 7.924780053, 0.5: 8.417606178, 1.0: 8.910432303}  # model-audit.md, DNAmTL table (kb)
MCCARTNEY_HALF = {  # model-audit.md, "Original-table score at beta = 0.5"
    "bmi": -0.7326852944,
    "smoking": 2.0069389860,
    "alcohol": -5.5593637390,
    "education": -2.4688491745,
    "totalchol": -1.0609031930,
    "hdl": 2.5504501939,
    "ldl": -2.7555480414,
    "bodyfat": -15.3519314083,
}


def _cpgs(*keys):
    return sorted({cpg for key in keys for cpg in clocks.model_cpgs(clocks.CLOCKS[key])})


def _long_file(path: Path, cpgs, beta=0.5, column="beta") -> Path:
    pd.DataFrame({column: beta}, index=pd.Index(cpgs, name="CpG")).to_csv(path)
    return path


def _run(tmp_path, betas: Path, *args, out="out"):
    out_dir = tmp_path / out
    code = personal_report.main(["--betas", str(betas), *args, "--out", str(out_dir)])
    report = (out_dir / "report.md").read_text(encoding="utf-8")
    result = json.loads((out_dir / "result.json").read_text(encoding="utf-8"))["outputs"]
    return code, report, result


def _row(report: str, key: str) -> str:
    rows = [line for line in report.splitlines() if line.startswith("| ") and f"（`{key}`）" in line]
    assert len(rows) == 1, (key, rows)
    return rows[0]


def test_dnamtl_anchor_unrounded():
    cpgs = _cpgs("dnamtl")
    assert len(cpgs) == 140
    for beta, expected in DNAMTL.items():
        frame = pd.DataFrame({"s": beta}, index=cpgs)
        assert clocks.predict_linear(frame, clocks.CLOCKS["dnamtl"])["s"] == pytest.approx(expected, abs=1e-6)


def test_dnamtl_anchor_end_to_end_in_kb(tmp_path):
    betas = _long_file(tmp_path / "tl.csv", _cpgs("dnamtl"))
    code, report, result = _run(tmp_path, betas, "--clocks", "dnamtl", "--age", "50")
    assert code == 0
    assert result["dnam_dnamtl"]["value"] == pytest.approx(DNAMTL[0.5], abs=ROUNDED)
    assert result["dnam_dnamtl"]["unit"] == "kb"
    row = _row(report, "dnamtl")
    assert "8.42 kb" in row and "岁" not in row
    assert "100%（缺 0/140）" in row
    assert "不是实测端粒长度" in report
    assert report.splitlines()[-1].startswith("边界: ")
    assert "Clock Foundation" in report


def test_mccartney_anchors_unrounded_and_end_to_end(tmp_path):
    keys = list(MCCARTNEY_HALF)
    cpgs = _cpgs(*keys)
    frame = pd.DataFrame({"s": 0.5}, index=cpgs)
    for key, expected in MCCARTNEY_HALF.items():
        # model-audit.md: bundled weights differ from the source table by < 5e-8 each.
        assert clocks.predict_linear(frame, clocks.CLOCKS[key])["s"] == pytest.approx(expected, abs=1e-6), key
    code, report, result = _run(tmp_path, _long_file(tmp_path / "m.csv", cpgs), "--clocks", ",".join(keys))
    assert code == 0
    for key, expected in MCCARTNEY_HALF.items():
        assert result[f"dnam_{key}"]["value"] == pytest.approx(expected, abs=ROUNDED), key
        assert result[f"dnam_{key}"]["unit"] == "score"
        row = _row(report, key)
        assert "（分值）" in row and "岁" not in row
        assert row.split("|")[5].strip() == "0", "every model CpG was supplied, nothing may be imputed"
    assert "不能换算成 BMI" in report


def test_cvd_and_depression_are_unavailable_never_a_number(tmp_path):
    betas = _long_file(tmp_path / "b.csv", _cpgs("cvd", "depression", "dnamtl"))
    code, report, result = _run(tmp_path, betas, "--clocks", "cvd", "depression", "dnamtl")
    assert code == 0
    assert result["dnam_cvd"]["value"] is None
    assert result["dnam_depression"]["value"] is None
    assert result["dnam_dnamtl"]["value"] == pytest.approx(DNAMTL[0.5], abs=ROUNDED)
    for key in ("cvd", "depression"):
        cell = _row(report, key).split("|")[2]
        assert cell.strip().startswith("不可用（") and not any(ch.isdigit() for ch in cell), cell


def test_grimage_without_age_or_sex_is_refused(tmp_path):
    betas = _long_file(tmp_path / "b.csv", _cpgs("dnamtl"))
    out = tmp_path / "o1"
    assert personal_report.main(["--betas", str(betas), "--clocks", "grimagev2", "--age", "50", "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert [item["key"] for item in problems] == ["sex"]
    assert "GrimAge" in problems[0]["message_zh"]
    out = tmp_path / "o2"
    assert personal_report.main(["--betas", str(betas), "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert [item["key"] for item in problems] == ["age", "sex"]
    assert "core" in problems[0]["message_zh"]


def test_unknown_clock_and_duplicate_cpg_are_refused(tmp_path):
    betas = _long_file(tmp_path / "b.csv", _cpgs("dnamtl"))
    assert personal_report.main(["--betas", str(betas), "--clocks", "altumage", "--out", str(tmp_path / "a")]) == skillkit.EXIT_INPUT_PROBLEM
    dup = tmp_path / "dup.csv"
    dup.write_text("CpG,me\ncg00000029,0.4\ncg00000029,0.5\n", encoding="utf-8")
    assert personal_report.main(["--betas", str(dup), "--clocks", "horvath", "--out", str(tmp_path / "b")]) == skillkit.EXIT_INPUT_PROBLEM
    assert "duplicate CpG" in (tmp_path / "b" / "report.md").read_text(encoding="utf-8")


def test_bmi_reed_runs_by_name_and_extra_group_rows_are_dropped(tmp_path):
    cpgs = _cpgs("bmi_reed")
    expected = clocks.predict_linear(pd.DataFrame({"s": 0.5}, index=cpgs), clocks.CLOCKS["bmi_reed"])["s"]
    assert personal_report.upstream_tokens(["bmi_reed", "dnamtl"], clocks) == ["exposome", "dnamtl"]
    code, report, result = _run(tmp_path, _long_file(tmp_path / "r.csv", cpgs), "--clocks", "bmi_reed")
    assert code == 0
    assert result["dnam_bmi_reed"]["value"] == pytest.approx(expected, abs=ROUNDED)
    assert result["dnam_smoking"]["value"] is None
    assert "`smoking`" not in report


def test_year_models_get_acceleration_only_with_age(tmp_path):
    cpgs = _cpgs("horvath", "dunedinpoam")
    betas = _long_file(tmp_path / "h.csv", cpgs)
    code, report, result = _run(tmp_path, betas, "--clocks", "horvath,dunedinpoam", "--age", "40", out="with")
    assert code == 0
    horvath = result["dnam_horvath"]["value"]
    assert f"{horvath - 40:+.2f} 岁" in _row(report, "horvath")
    assert _row(report, "dunedinpoam").split("|")[3].strip() == "—"
    assert "年/年" in _row(report, "dunedinpoam")
    code, report, _ = _run(tmp_path, betas, "--clocks", "horvath", out="without")
    assert code == 0
    assert _row(report, "horvath").split("|")[3].strip() == "—"


def test_matrix_writes_first_sample_and_says_age_applies_to_all(tmp_path):
    cpgs = _cpgs("dnamtl")
    path = tmp_path / "matrix.tsv"
    pd.DataFrame({"first": 0.5, "second": 1.0}, index=pd.Index(cpgs, name="CpG")).to_csv(path, sep="\t")
    code, report, result = _run(tmp_path, path, "--clocks", "dnamtl")
    assert code == 0
    assert result["dnam_dnamtl"]["value"] == pytest.approx(DNAMTL[0.5], abs=ROUNDED)
    assert "### 样本 first" in report and "### 样本 second" in report
    assert "8.91 kb" in report
    assert "每一列都一样套用" in report


def test_grimage_sensitivity_is_reported(tmp_path):
    betas = _long_file(tmp_path / "g.csv", _cpgs("grimagev2"))
    code, report, result = _run(tmp_path, betas, "--clocks", "grimagev2", "--age", "50", "--sex", "女",
                                "--sensitivity", "45,55")
    assert code == 0
    assert result["dnam_grimagev2"]["value"] is not None
    assert "## GrimAgeV2 对实足年龄的敏感性" in report
    for age in ("45", "50", "55"):
        assert f"实足年龄 {age}：GrimAgeV2" in report


def test_upstream_failure_is_surfaced_not_guessed(tmp_path, monkeypatch):
    def broken(*args, **kwargs):
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="ERROR: missing local clock/imputation resources:\n  - blood_panel.npz\n")

    monkeypatch.setattr(personal_report, "run_upstream", broken)
    betas = _long_file(tmp_path / "b.csv", _cpgs("dnamtl"))
    code, report, result = _run(tmp_path, betas, "--clocks", "dnamtl")
    assert code == personal_report.EXIT_UPSTREAM_FAILED
    assert "blood_panel.npz" in report and "退出码 1" in report
    assert all(item["value"] is None for item in result.values())
