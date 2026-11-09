"""Cumulative BMI / waist exposure against Yu et al., GeroScience 2026 (RLAS).

Cut points come from Methods "Measurement of obesity indicators"; cohort numbers from
Results "Baseline characteristics"; regression rows from Supplementary Tables 2, 4 and 12.
The paper prints no individual worked example and no tertile cut points, so these tests
check the constants, the formula on hand-computed synthetic inputs, and input handling
(validation stays draft).
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import (BMI_LABELS, BMI_OBESITY_FROM, BMI_REF, BMI_UNDERWEIGHT_BELOW, COHORT, TABLE_S2,
                     TABLE_S4_BMI_KDM, WC_REF_CM, WC_REF_FEMALE_CHINESE_CM)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))

FULL = [("BMI 1", "25.0", "kg/m2"), ("BMI 2", "26.0", "kg/m2"), ("BMI 3", "24.5", "kg/m2"),
        ("腰围1", "88", "cm"), ("腰围2", "90", "cm"), ("腰围3", "86", "cm"),
        ("间隔1", "3", "年"), ("间隔2", "2", "年")]


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, sex=None, age=None, name="out"):
    m = _csv(tmp_path / f"{name}.csv", rows)
    out = tmp_path / name
    args = ["--measurements", str(m), "--out", str(out)]
    if sex is not None:
        args += ["--sex", sex]
    if age is not None:
        args += ["--age", age]
    code = pr.main(args)
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


def test_constants_are_as_printed():
    # Methods: "BMI threshold of 24 kg/m2", "≥ 90 cm for males and ≥ 80 cm for females".
    assert BMI_REF == 24.0 and WC_REF_CM == {"male": 90.0, "female": 80.0}
    # Supplementary Table 12: "adjusting WC cutoff for female ≥85 cm".
    assert WC_REF_FEMALE_CHINESE_CM == 85.0
    # Methods: underweight < 18.5, overweight ≥ 24 and < 28, obesity ≥ 28.
    assert BMI_UNDERWEIGHT_BELOW == 18.5 and BMI_OBESITY_FROM == 28.0
    # Results: "1.3 (0.0, 11.0) kg/m2 × years and 20.5 (0.5, 50.5) cm × years"; 687 adults, 79.6 ± 3.5.
    assert COHORT["cbmi_median"] == 1.3 and COHORT["cbmi_iqr"] == (0.0, 11.0)
    assert COHORT["cwc_median"] == 20.5 and COHORT["cwc_iqr"] == (0.5, 50.5)
    assert (COHORT["n"], COHORT["mean_age"], COHORT["female_n"]) == (687, 79.6, 370)
    # Supplementary Table 2.
    assert TABLE_S2["cbmi"]["kdm_ba"]["T3"] == (1.22, 0.80, 1.63)
    assert TABLE_S2["cbmi"]["pd"]["T3"] == (0.18, 0.05, 0.31)
    assert TABLE_S2["cwc"]["kdm_ba"]["T3"] == (1.65, 1.19, 2.12)
    assert TABLE_S2["cbmi"]["kdm_ba"]["per_unit"] == (0.034, 0.021, 0.048)
    assert TABLE_S2["cwc"]["kdm_ba"]["per_unit"] == (0.015, 0.01, 0.02)
    # Supplementary Table 4.
    assert TABLE_S4_BMI_KDM[2] == (0.78, 0.45, 1.11) and TABLE_S4_BMI_KDM[3] == (1.02, 0.52, 1.53)
    assert TABLE_S4_BMI_KDM[0] == (-0.51, -1.25, 0.22)


@pytest.mark.parametrize("bmi,group", [(18.4, 0), (18.5, 1), (23.9, 1), (24.0, 2), (27.9, 2), (28.0, 3), (35.0, 3)])
def test_bmi_groups(bmi, group):
    assert pr.bmi_group(bmi) == group


def test_formula_hand_computed():
    # excess 1, 2, 0.5 over 24; intervals 3 and 2 years: (1+2)/2*3 + (2+0.5)/2*2 = 4.5 + 2.5 = 7.0
    assert pr.cumulative_exposure([25.0, 26.0, 24.5], 24.0, [3, 2]) == pytest.approx(7.0)
    # below the reference counts as zero: excess 0, 0, 3 -> (0+0)/2*3 + (0+3)/2*2 = 3.0
    assert pr.cumulative_exposure([20.0, 23.0, 27.0], 24.0, [3, 2]) == pytest.approx(3.0)
    assert pr.cumulative_exposure([20.0, 22.0, 23.9], 24.0, [3, 2]) == 0.0


def test_full_report_female(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, FULL, sex="女", age="80")
    assert code == 0
    assert result["cbmi_kg_m2_years"]["value"] == pytest.approx(7.0)
    # waist excess over 80: 8, 10, 6 -> (8+10)/2*3 + (10+6)/2*2 = 27 + 16 = 43
    assert result["cwc_cm_years"]["value"] == pytest.approx(43.0)
    # over 85: 3, 5, 1 -> (3+5)/2*3 + (5+1)/2*2 = 12 + 6 = 18
    assert result["cwc_cm_years_female_85cm"]["value"] == pytest.approx(18.0)
    assert result["baseline_bmi_group"]["value"] == BMI_LABELS[2]
    assert "## 论文卡片" in report and "边界:" in report and "10.1007/s11357-026-02437-y" in report
    assert "三分位的界值论文没有印出" in report
    assert "1.22" in report and "1.65" in report
    assert "+0.034 岁（95% 置信区间 0.021 到 0.048）" in report and "PD +0.18（" in report


def test_male_waist_cut_point(tmp_path: Path):
    rows = [("腰围1", "92", "cm"), ("腰围2", "88", "cm"), ("腰围3", "95", "cm"), ("间隔1", "3", "年"), ("间隔2", "2", "年")]
    code, result, report, _ = _run(tmp_path, rows, sex="male")
    assert code == 0
    # excess over 90: 2, 0, 5 -> (2+0)/2*3 + (0+5)/2*2 = 3 + 5 = 8
    assert result["cwc_cm_years"]["value"] == pytest.approx(8.0)
    assert result["cwc_cm_years_female_85cm"]["value"] is None
    assert result["cbmi_kg_m2_years"]["value"] is None


def test_zero_exposure_is_reference(tmp_path: Path):
    rows = [("BMI 1", "22", "kg/m2"), ("BMI 2", "23", "kg/m2"), ("BMI 3", "22.5", "kg/m2"), ("间隔1", "3", "年"), ("间隔2", "24", "mo")]
    code, result, report, _ = _run(tmp_path, rows)
    assert code == 0 and result["cbmi_kg_m2_years"]["value"] == 0.0
    assert "参照组" in report


def test_wrong_unit_is_caught(tmp_path: Path):
    # Waist in inches typed without a unit falls below the 50 cm floor.
    rows = [("腰围1", "34", ""), ("腰围2", "35", ""), ("腰围3", "36", ""), ("间隔1", "3", "年"), ("间隔2", "2", "年")]
    code, result, _, out = _run(tmp_path, rows, sex="男")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert {p["key"] for p in problems if p["kind"] == "range"} == {"waist_wave1_cm", "waist_wave2_cm", "waist_wave3_cm"}
    assert all(item["value"] is None for item in result.values())


def test_out_of_range_bmi_and_unknown_unit(tmp_path: Path):
    rows = [("BMI 1", "250", "kg/m2"), ("BMI 2", "26", "kg/m2"), ("BMI 3", "26", "kg/m2"), ("间隔1", "3", "年"), ("间隔2", "2", "年")]
    code, _, _, _ = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    rows2 = [("腰围1", "90", "ft"), ("腰围2", "90", "cm"), ("腰围3", "90", "cm"), ("间隔1", "3", "年"), ("间隔2", "2", "年")]
    code2, _, _, _ = _run(tmp_path, rows2, sex="女", name="ft")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM


def test_incomplete_series_and_missing_sex(tmp_path: Path):
    rows = [("BMI 1", "25", "kg/m2"), ("BMI 3", "26", "kg/m2"), ("间隔1", "3", "年"), ("间隔2", "2", "年")]
    code, _, _, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("bmi_wave2_kg_m2", "missing") in {(p["key"], p["kind"]) for p in problems}
    rows2 = [("腰围1", "90", "cm"), ("腰围2", "90", "cm"), ("腰围3", "90", "cm"), ("间隔1", "3", "年"), ("间隔2", "2", "年")]
    code2, _, _, out2 = _run(tmp_path, rows2, name="nosex")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM
    problems2 = json.loads((out2 / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("sex", "missing") in {(p["key"], p["kind"]) for p in problems2}
    code3, _, _, out3 = _run(tmp_path, [("BMI 1", "25", "kg/m2"), ("BMI 2", "25", "kg/m2"), ("BMI 3", "25", "kg/m2")], name="noint")
    assert code3 == skillkit.EXIT_INPUT_PROBLEM
    keys3 = {p["key"] for p in json.loads((out3 / "problems.json").read_text(encoding="utf-8"))["problems"]}
    assert {"interval_1_2_years", "interval_2_3_years"} <= keys3


def test_under_70_is_noted(tmp_path: Path):
    code, _, report, _ = _run(tmp_path, FULL, sex="女", age="55")
    assert code == 0 and "70 岁以上" in report


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == list(pr.BMI_KEYS) + list(pr.WC_KEYS) + list(pr.INTERVAL_KEYS) + ["sex", "age"]
    for key in pr.BMI_KEYS:
        assert skillkit.spec_by_key(MANIFEST, key)["unit"] == "kg/m^2"
    for key in pr.WC_KEYS:
        assert skillkit.spec_by_key(MANIFEST, key)["unit"] == "cm"
    for key in pr.INTERVAL_KEYS:
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == "a" and spec["required"] is True
    assert MANIFEST["population"]["age_years"][0] == 70
    assert MANIFEST["validation"]["status"] == "draft"
    assert [o["key"] for o in MANIFEST["outputs"]] == ["cbmi_kg_m2_years", "cwc_cm_years",
                                                      "cwc_cm_years_female_85cm", "baseline_bmi_group"]
