"""skill.json inputs match presets, and unit mistakes stop the computation.

The four cases below were run by hand against the old script: CRP in mg/L and
albumin in g/dL produced a normal-looking report with the wrong age, and
RDW-SD crashed with a traceback.
"""

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import (
    GAMMA,
    MORTALITY_NUMERATOR,
    PHENOAGE_BIOMARKERS,
    PHENOAGE_LOG_DENOMINATOR,
    PHENOAGE_LOG_NUMERATOR,
    PHENOAGE_OFFSET,
)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
CANONICAL = {
    "albumin_gL": 45, "creat_umol": 80, "glucose_mmol": 5.0, "crp_mg_dl": 0.1, "lymph_pct": 30,
    "mcv_fl": 90, "rdw_pct": 13, "alp_u_l": 70, "wbc_10e3": 6,
}
CHINESE_WITH_UNITS = [
    ("白蛋白", "45", "g/L"), ("肌酐", "80", "μmol/L"), ("葡萄糖", "5.0", "mmol/L"), ("超敏C反应蛋白", "1.0", "mg/L"),
    ("淋巴细胞百分比", "30", "%"), ("平均红细胞体积", "90", "fL"), ("RDW-CV", "13", "%"), ("碱性磷酸酶", "70", "U/L"),
    ("白细胞计数", "6", "×10⁹/L"),
]


def _csv(path: Path, rows) -> Path:
    lines = ["marker,value,unit"] + [",".join(row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _expected(age: float) -> float:
    return personal_report.phenotypic_age({**CANONICAL, "age": age}, "ln")


def test_manifest_matches_presets():
    declared = {item["key"]: item for item in MANIFEST["inputs"] if item["from"] == "measurements"}
    assert list(declared) == [key for key, _label, _unit in PHENOAGE_BIOMARKERS]
    for key, label, unit in PHENOAGE_BIOMARKERS:
        assert declared[key]["label_zh"] == label
        assert skillkit.normalize_unit(declared[key]["unit"]) == skillkit.normalize_unit(unit)
    assert MANIFEST["inputs_status"] == "verified"
    assert {item["key"] for item in MANIFEST["outputs"]} == {"phenoage", "phenoage_advance", "mortality_10y_pct"}


def test_chinese_report_with_units_matches_canonical(tmp_path: Path):
    bio = _csv(tmp_path / "bio.csv", CHINESE_WITH_UNITS)
    report = personal_report.write_report(tmp_path / "out", bio, 40, "男", None, None, None)
    text = report.read_text(encoding="utf-8")
    expected = _expected(40)
    assert f"是 {expected:.2f} 岁" in text
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    assert result["outputs"]["phenoage"]["value"] == pytest.approx(expected)
    assert result["outputs"]["phenoage_advance"]["value"] == pytest.approx(expected - 40)
    assert not (tmp_path / "out" / "problems.json").exists()


def test_crp_by_name_without_unit_is_refused(tmp_path: Path):
    rows = [row if row[0] != "超敏C反应蛋白" else ("C反应蛋白", "1.0", "") for row in CHINESE_WITH_UNITS]
    bio = _csv(tmp_path / "bio.csv", rows)
    code = personal_report.main(["--biomarkers", str(bio), "--age", "40", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "没有表型年龄" in text
    assert "没有写单位" in text and "mg/L" in text
    assert "岁。表型年龄减去" not in text
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    assert result["outputs"]["phenoage"]["value"] is None


def test_albumin_in_g_dl_without_unit_is_out_of_range(tmp_path: Path):
    rows = [row if row[0] != "白蛋白" else ("白蛋白", "4.5", "") for row in CHINESE_WITH_UNITS]
    report = personal_report.write_report(tmp_path / "out", _csv(tmp_path / "bio.csv", rows), 40, None, None, None, None)
    text = report.read_text(encoding="utf-8")
    assert "不在合理范围" in text
    assert "g/dL" in text
    assert "48.0" not in text


def test_albumin_in_g_dl_with_unit_is_converted(tmp_path: Path):
    rows = [row if row[0] != "白蛋白" else ("白蛋白", "4.5", "g/dL") for row in CHINESE_WITH_UNITS]
    report = personal_report.write_report(tmp_path / "out", _csv(tmp_path / "bio.csv", rows), 40, None, None, None, None)
    assert f"是 {_expected(40):.2f} 岁" in report.read_text(encoding="utf-8")


def test_rdw_sd_is_refused_with_a_reason(tmp_path: Path):
    rows = [row if row[0] != "RDW-CV" else ("红细胞分布宽度", "42", "") for row in CHINESE_WITH_UNITS]
    code = personal_report.main(["--biomarkers", str(_csv(tmp_path / "bio.csv", rows)), "--age", "40", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "RDW-CV" in text and "RDW-SD" in text
    rows = [row if row[0] != "RDW-CV" else ("红细胞分布宽度", "42", "fL") for row in CHINESE_WITH_UNITS]
    code = personal_report.main(["--biomarkers", str(_csv(tmp_path / "bio2.csv", rows)), "--age", "40", "--out", str(tmp_path / "out2")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "不能换算" in (tmp_path / "out2" / "report.md").read_text(encoding="utf-8")


def test_absolute_lymphocyte_count_is_not_read_as_percent(tmp_path: Path):
    rows = [row if row[0] != "淋巴细胞百分比" else ("淋巴细胞计数", "1.8", "×10⁹/L") for row in CHINESE_WITH_UNITS]
    report = personal_report.write_report(tmp_path / "out", _csv(tmp_path / "bio.csv", rows), 40, None, None, None, None)
    text = report.read_text(encoding="utf-8")
    assert "九项血液指标没有齐，所以没有表型年龄" in text


def test_age_out_of_range_is_refused(tmp_path: Path):
    bio = _csv(tmp_path / "bio.csv", CHINESE_WITH_UNITS)
    code = personal_report.main(["--biomarkers", str(bio), "--age", "400", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "实足年龄" in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


def test_mortality_output_is_the_ten_year_score_behind_phenoage(tmp_path: Path):
    # The Gompertz numerator is the cumulative hazard over 120 months.
    assert -MORTALITY_NUMERATOR == pytest.approx(math.exp(120 * GAMMA) - 1, rel=1e-4)
    bio = _csv(tmp_path / "bio.csv", CHINESE_WITH_UNITS)
    report = personal_report.write_report(tmp_path / "out", bio, 40, "男", None, None, None)
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    pct = result["outputs"]["mortality_10y_pct"]["value"]
    assert 0 < pct < 100
    back = PHENOAGE_OFFSET + math.log(PHENOAGE_LOG_NUMERATOR * math.log(1 - pct / 100)) / PHENOAGE_LOG_DENOMINATOR
    assert back == pytest.approx(result["outputs"]["phenoage"]["value"])
    text = report.read_text(encoding="utf-8")
    assert "10 年死亡风险" in text and "不是这个人的风险" in text


def test_levers_move_each_target_alone_and_together(tmp_path: Path):
    bio = _csv(tmp_path / "bio.csv", CHINESE_WITH_UNITS)
    targets = _csv(tmp_path / "targets.csv", [("空腹血糖", "4.5", "mmol/L"), ("超敏C反应蛋白", "0.5", "mg/L")])
    code = personal_report.main(["--biomarkers", str(bio), "--age", "40", "--targets", str(targets), "--out", str(tmp_path / "out")])
    assert code == 0
    levers = json.loads((tmp_path / "out" / "levers.json").read_text(encoding="utf-8"))
    assert levers["schema"] == "longevity-levers/1"
    current = _expected(40)
    assert levers["current"]["phenoage"] == pytest.approx(current)
    by_key = {item["key"]: item for item in levers["levers"]}
    alone = personal_report.phenotypic_age({**CANONICAL, "age": 40, "glucose_mmol": 4.5}, "ln")
    assert by_key["glucose_mmol"]["phenoage_delta"] == pytest.approx(alone - current)
    assert by_key["crp_mg_dl"]["to"] == pytest.approx(0.05)
    together = personal_report.phenotypic_age({**CANONICAL, "age": 40, "glucose_mmol": 4.5, "crp_mg_dl": 0.05}, "ln")
    assert levers["targets"]["phenoage"] == pytest.approx(together)
    slopes = {item["key"]: item["years_per_unit"] for item in levers["sensitivity"]}
    # glucose raises phenotypic age, albumin lowers it
    assert slopes["glucose_mmol"] > 0 and slopes["albumin_gL"] < 0
    bumped = personal_report.phenotypic_age({**CANONICAL, "age": 40, "glucose_mmol": 5.01}, "ln")
    assert slopes["glucose_mmol"] == pytest.approx((bumped - current) / 0.01, rel=1e-3)


def test_no_levers_without_complete_inputs(tmp_path: Path):
    rows = [row for row in CHINESE_WITH_UNITS if row[0] != "白蛋白"]
    bio = _csv(tmp_path / "bio.csv", rows)
    personal_report.main(["--biomarkers", str(bio), "--age", "40", "--out", str(tmp_path / "out")])
    assert not (tmp_path / "out" / "levers.json").exists()
