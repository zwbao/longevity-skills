"""skill.json matches presets, printed numbers are honoured, and bad input stops the run.

The paper prints no person's inputs with a phenotypic age or hazard ratio, so
nothing here reproduces a printed personal example (validation is draft).
What is checked against printed numbers:

- the BioAge code weights round to the weights printed in the Supplementary
  Methods (the log numerator is the one documented mismatch);
- path 1 beta (Results) times ln of the path 2 hazard ratio (Results) gives
  the indirect effects printed in Supplementary Table S2, which fixes how the
  hazard ratio is applied: per one year, on the log-hazard scale.
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
    BOUNDARY,
    GAMMA,
    HR_CVD_DEATH,
    HR_INCIDENT_CVD,
    MORTALITY_NUMERATOR,
    PAPER_PRINTED,
    PATH1_BETA_PHENOAGEACCEL,
    PHENOAGE_BIOMARKERS,
    PHENOAGE_LOG_DENOMINATOR,
    PHENOAGE_LOG_NUMERATOR,
    PHENOAGE_OFFSET,
    PHENOTYPE_INTERCEPT,
    PHENOTYPE_WEIGHTS,
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
    path.write_text("\n".join(["marker,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, age="50", targets=None):
    args = ["--biomarkers", str(_csv(tmp_path / "bio.csv", rows)), "--age", age, "--out", str(tmp_path / "out")]
    if targets is not None:
        args += ["--targets", str(_csv(tmp_path / "targets.csv", targets))]
    code = personal_report.main(args)
    out = tmp_path / "out"
    return code, (out / "report.md").read_text(encoding="utf-8"), json.loads((out / "result.json").read_text(encoding="utf-8"))


def test_manifest_matches_presets():
    declared = {item["key"]: item for item in MANIFEST["inputs"] if item["from"] == "measurements"}
    assert list(declared) == [key for key, _label, _unit in PHENOAGE_BIOMARKERS]
    for key, label, unit in PHENOAGE_BIOMARKERS:
        assert declared[key]["label_zh"] == label
        assert skillkit.normalize_unit(declared[key]["unit"]) == skillkit.normalize_unit(unit)
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["paper"]["doi"] == "10.1007/s11357-026-02543-x"
    assert MANIFEST["validation"]["status"] == "draft"
    assert {item["key"] for item in MANIFEST["outputs"]} == set(personal_report.OUTPUT_KEYS)


def test_code_weights_round_to_supplementary_methods():
    # Supplementary Methods: xb= -19.907 - 0.0336*albumin + 0.0095*creatinine + 0.1953*glucose
    # + 0.0954*ln(C reactive protein) - 0.0120*lymphocyte percentage + 0.0268*mean corpuscular volume
    # + 0.3306*red blood cell distribution width + 0.00188*alkaline phosphatase
    # + 0.0554*white blood cell count + 0.0804*chronological age; γ = 0.0076927;
    # PhenoAge = 141.50225 + ln{-0.0053*ln(1-mortality risk)} / 0.090165
    assert round(PHENOTYPE_INTERCEPT, 3) == PAPER_PRINTED["intercept"] == -19.907
    for key, weight in PHENOTYPE_WEIGHTS.items():
        if key == "alp_u_l":
            continue
        printed = PAPER_PRINTED[key]
        digits = len(repr(abs(printed)).split(".")[1])
        assert round(weight, digits) == pytest.approx(printed, abs=1e-12), key
    assert round(GAMMA, 7) == PAPER_PRINTED["gamma"] == 0.0076927
    assert PHENOAGE_OFFSET == PAPER_PRINTED["offset"] == 141.50225
    assert PHENOAGE_LOG_DENOMINATOR == PAPER_PRINTED["log_denominator"] == 0.090165
    assert -MORTALITY_NUMERATOR == pytest.approx(math.exp(120 * GAMMA) - 1, rel=1e-5)
    # The one mismatch: printed -0.0053, code -0.0055305. It is a constant shift of every age.
    assert PAPER_PRINTED["log_numerator"] == -0.0053
    shift = math.log(0.0053 / 0.0055305) / PHENOAGE_LOG_DENOMINATOR
    assert shift == pytest.approx(-0.472, abs=0.001)
    # Second mismatch: ALP printed 0.00188, code 0.001868778 (rounds to 0.00187).
    # At ALP 300 U/L the xb difference is 0.0034, under 0.04 years of phenotypic age.
    assert PAPER_PRINTED["alp_u_l"] == 0.00188
    assert round(PHENOTYPE_WEIGHTS["alp_u_l"], 5) == 0.00187
    values = {"albumin_gL": 45, "creat_umol": 80, "glucose_mmol": 5.0, "crp_mg_dl": 0.1, "lymph_pct": 30,
              "mcv_fl": 90, "rdw_pct": 13, "alp_u_l": 300, "wbc_10e3": 6, "age": 50}
    xb_gap = (0.00188 - PHENOTYPE_WEIGHTS["alp_u_l"]) * 300
    bumped = dict(values, alp_u_l=300 + xb_gap / PHENOTYPE_WEIGHTS["alp_u_l"])
    assert abs(personal_report.phenotypic_age(bumped) - personal_report.phenotypic_age(values)) < 0.04


def _interval_product(beta: float, hr: float) -> tuple[float, float]:
    """beta and HR are printed to three decimals; the product to four."""
    corners = [b * math.log(h) for b in (beta - 0.0005, beta + 0.0005) for h in (hr - 0.0005, hr + 0.0005)]
    return min(corners) - 0.00005, max(corners) + 0.00005


@pytest.mark.parametrize(
    "score, printed",
    [("HEI", -0.0012), ("AHEI", -0.0013), ("DASH", -0.0058), ("MDS", -0.0083)],
)
def test_indirect_effect_incident_cvd_matches_table_s2(score, printed):
    # Table S2, PhenoAgeAccel — Incident CVD indirect effect β: -0.0012, -0.0013, -0.0058, -0.0083
    low, high = _interval_product(PATH1_BETA_PHENOAGEACCEL[score], HR_INCIDENT_CVD[0])
    assert low <= printed <= high


@pytest.mark.parametrize(
    "score, printed",
    [("HEI", -0.0024), ("AHEI", -0.0027), ("DASH", -0.0121), ("MDS", -0.0172)],
)
def test_indirect_effect_cvd_death_matches_table_s2(score, printed):
    # Table S2, PhenoAgeAccel — CVD death indirect effect β: -0.0024, -0.0027, -0.0121, -0.0172
    low, high = _interval_product(PATH1_BETA_PHENOAGEACCEL[score], HR_CVD_DEATH[0])
    assert low <= printed <= high


# BioAge (dayoonkwon/BioAge b1f9fc0) phenoage0 on NHANES III rows, as stored in data/NHANES3.rda.
# BioAge feeds log(1 + crp) to the ln(CRP) weight, so 1 + crp is passed here to get the same term.
# age, albumin, creatinine, glucose, CRP mg/dL, lymph %, MCV, RDW, ALP, WBC, phenoage0
BIOAGE_ROWS = [
    (48, 40, 51.62659381, 6.0495, 0.2099999934, 32.34999847, 92.40000153, 12.05000019, 59, 4.949999809, 39.8804215),
    (81, 41.99999809, 68.5997192, 6.0495, 0.2099999934, 28.70000076, 95.65000153, 12.5, 77, 7.900000095, 75.62082723),
    (52, 39.00000095, 60.11315398, 5.0505, 1.700000048, 30.64999962, 82.90000153, 14.44999981, 97, 10.60000038, 53.86461496),
]


@pytest.mark.parametrize("row", BIOAGE_ROWS)
def test_formula_matches_bioage_phenoage0(row):
    keys = ("age", "albumin_gL", "creat_umol", "glucose_mmol", "crp_mg_dl", "lymph_pct", "mcv_fl", "rdw_pct", "alp_u_l", "wbc_10e3")
    values = dict(zip(keys, row[:10]))
    values["crp_mg_dl"] = 1 + values["crp_mg_dl"]
    assert personal_report.phenotypic_age(values) == pytest.approx(row[10], abs=0.01)


def test_hazard_ratio_contrast_is_per_year_on_log_scale():
    assert personal_report.hazard_ratio(1, HR_INCIDENT_CVD)["hr"] == pytest.approx(1.033)
    assert personal_report.hazard_ratio(1, HR_CVD_DEATH)["hr"] == pytest.approx(1.070)
    two_down = personal_report.hazard_ratio(-2, HR_INCIDENT_CVD)
    assert two_down["hr"] == pytest.approx(1.033 ** -2)
    assert two_down["low"] == pytest.approx(1.038 ** -2) and two_down["high"] == pytest.approx(1.028 ** -2)


def test_chinese_report_gives_phenoage_and_no_personal_hr_without_targets(tmp_path: Path):
    code, text, result = _run(tmp_path, CHINESE_WITH_UNITS)
    assert code == 0
    expected = personal_report.phenotypic_age({**CANONICAL, "age": 50})
    assert result["outputs"]["phenoage"]["value"] == pytest.approx(expected)
    assert result["outputs"]["phenoage_advance"]["value"] == pytest.approx(expected - 50)
    assert result["outputs"]["target_hr_incident_cvd"]["value"] is None
    assert f"表型年龄 {expected:.2f} 岁" in text
    assert text.index("## 论文卡片") < text.index("## 你的结果")
    assert "10.1007/s11357-026-02543-x" in text
    assert "没有给目标值" in text
    # Results, path 2: 1.033 [1.028, 1.038] incident CVD; 1.070 [1.058, 1.083] CVD mortality
    assert "1.033（1.028–1.038）" in text and "1.070（1.058–1.083）" in text
    assert f"边界: {BOUNDARY}" in text
    assert not (tmp_path / "out" / "problems.json").exists()


def test_targets_give_hazard_ratio_of_the_phenoage_change(tmp_path: Path):
    targets = [("空腹血糖", "4.5", "mmol/L"), ("超敏C反应蛋白", "0.5", "mg/L")]
    code, text, result = _run(tmp_path, CHINESE_WITH_UNITS, targets=targets)
    assert code == 0
    current = personal_report.phenotypic_age({**CANONICAL, "age": 50})
    together = personal_report.phenotypic_age({**CANONICAL, "age": 50, "glucose_mmol": 4.5, "crp_mg_dl": 0.05})
    delta = together - current
    assert delta < 0
    assert result["outputs"]["target_phenoage_delta"]["value"] == pytest.approx(delta)
    assert result["outputs"]["target_hr_incident_cvd"]["value"] == pytest.approx(1.033 ** delta)
    assert result["outputs"]["target_hr_cvd_death"]["value"] == pytest.approx(1.070 ** delta)
    levers = json.loads((tmp_path / "out" / "levers.json").read_text(encoding="utf-8"))
    assert levers["schema"] == "longevity-levers/1"
    by_key = {item["key"]: item for item in levers["levers"]}
    assert by_key["crp_mg_dl"]["to"] == pytest.approx(0.05)
    alone = personal_report.phenotypic_age({**CANONICAL, "age": 50, "glucose_mmol": 4.5})
    assert by_key["glucose_mmol"]["phenoage_delta"] == pytest.approx(alone - current)
    slopes = {item["key"]: item for item in levers["sensitivity"]}
    assert slopes["glucose_mmol"]["years_per_unit"] > 0 and slopes["albumin_gL"]["years_per_unit"] < 0
    assert slopes["glucose_mmol"]["log_hr_incident_cvd_per_unit"] == pytest.approx(
        math.log(1.033) * slopes["glucose_mmol"]["years_per_unit"])
    assert "模型换算" in text and "不是改变化验后一定会发生" in text


def test_crp_without_unit_is_refused(tmp_path: Path):
    rows = [row if row[0] != "超敏C反应蛋白" else ("C反应蛋白", "1.0", "") for row in CHINESE_WITH_UNITS]
    code, text, result = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "没有表型年龄" in text and "mg/L" in text
    assert "## 论文卡片" in text and f"边界: {BOUNDARY}" in text
    assert result["outputs"]["phenoage"]["value"] is None
    assert (tmp_path / "out" / "problems.json").exists()
    assert not (tmp_path / "out" / "levers.json").exists()


def test_albumin_out_of_range_is_refused(tmp_path: Path):
    rows = [row if row[0] != "白蛋白" else ("白蛋白", "4.5", "") for row in CHINESE_WITH_UNITS]
    code, text, result = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "不在合理范围" in text
    assert result["outputs"]["phenoage"]["value"] is None
    assert "岁，实足年龄" not in text


def test_albumin_in_g_dl_with_unit_is_converted(tmp_path: Path):
    rows = [row if row[0] != "白蛋白" else ("白蛋白", "4.5", "g/dL") for row in CHINESE_WITH_UNITS]
    code, _text, result = _run(tmp_path, rows)
    assert code == 0
    assert result["outputs"]["phenoage"]["value"] == pytest.approx(personal_report.phenotypic_age({**CANONICAL, "age": 50}))


def test_bad_target_unit_is_refused(tmp_path: Path):
    code, text, _result = _run(tmp_path, CHINESE_WITH_UNITS, targets=[("白蛋白", "4.8", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "不在合理范围" in text


def test_age_out_of_range_is_refused(tmp_path: Path):
    code, text, _result = _run(tmp_path, CHINESE_WITH_UNITS, age="400")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "实足年龄" in text


def test_missing_marker_gives_no_phenoage(tmp_path: Path):
    rows = [row for row in CHINESE_WITH_UNITS if row[0] != "白蛋白"]
    code, text, result = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "没有表型年龄" in text and "白蛋白" in text
    problems = json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert any(item["kind"] == "missing" and item["key"] == "albumin_gL" for item in problems)
    assert result["outputs"]["phenoage"]["value"] is None
    assert not (tmp_path / "out" / "levers.json").exists()
