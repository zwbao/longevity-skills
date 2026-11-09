"""Physical activity dose and frailty index against Ji, GeroScience 2026 (CHARLS), doi:10.1007/s11357-026-02480-9.

Expected betas are the Model 3 rows of Tables 4-5 and the cells of Figures 6-7; expected hazard
ratios are Supplementary Tables 1-2 (MOESM1). The formula and cut points are from Methods,
Table 1 and Table 2. The paper prints no individual worked example, so these tests check the
formula, the cut points, the Table 2 item scores and the table lookups (validation stays draft).
All personal inputs are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import (FI_QUESTION_ITEMS, FIG6_FP_BETA, FIG7_FI_BETA, HB_NORMAL_G_DL, PA_WEIGHTS, SCORES,
                     SUPP1_FP_HR_ALL, SUPP1_FP_HR_FRAIL, SUPP2_FI_HR_ALL, SUPP2_FI_HR_FRAIL,
                     TABLE4_FP_GUIDELINE, TABLE5_FI_GUIDELINE)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
PA_OK = [("HPA", "0", "min"), ("MPA", "100", "min"), ("LPA", "300", "min")]   # total 0 + 100 + 150 = 250


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


def _all_items(code_by_kind=None):
    """All 43 questionnaire items answered with the lowest-deficit code, unless overridden."""
    best = {"adl4": "1", "yesno": "0", "cesd_neg": "1", "cesd_pos": "4", "srh5": "1", "ls5": "1"}
    best.update(code_by_kind or {})
    return [(key, best[kind], "") for _n, key, _zh, _en, _code, kind in FI_QUESTION_ITEMS]


LABS_NORMAL = [("weight", "60", "kg"), ("height", "165", "cm"), ("HbA1c", "5.4", "%"), ("血红蛋白", "140", "g/L"),
               ("CRP", "1.0", "mg/L"), ("肌酐", "70", "umol/L")]


def test_paper_constants_as_printed():
    # Methods: Total PA = (2 x HPA) + MPA + (0.5 x LPA)
    assert PA_WEIGHTS == {"hpa": 2.0, "mpa": 1.0, "lpa": 0.5}
    # Table 4 / Table 5, Model 3, Total PA "Yes" and LPA "Yes"
    assert TABLE4_FP_GUIDELINE["total"] == (-1.169, -1.252, -1.086)
    assert TABLE4_FP_GUIDELINE["lpa"] == (-0.659, -0.747, -0.571)
    assert TABLE5_FI_GUIDELINE["total"] == (-0.030, -0.039, -0.021)
    assert TABLE5_FI_GUIDELINE["lpa"] == (-0.024, -0.033, -0.016)
    # Figure 6 / Figure 7, Total PA rows
    assert [row[0] for row in FIG6_FP_BETA["total"][1:]] == [-0.11, -0.27, -0.77]
    assert [row[0] for row in FIG7_FI_BETA["total"][1:]] == [0.0, -0.02, -0.03]
    assert FIG6_FP_BETA["lpa"][3][:3] == (-1.21, -1.32, -1.11)
    # Supplementary Table 1 panel B and Supplementary Table 2 panel B (>= 300 min/week)
    assert SUPP1_FP_HR_ALL["total"][3] == (0.732, 0.568, 0.944, "0.016")
    assert SUPP2_FI_HR_ALL["total"][3] == (0.758, 0.589, 0.975, "0.031")
    # duplicated panels as printed: Supp 1 F == B, Supp 2 G == C
    assert SUPP1_FP_HR_FRAIL["total"] == SUPP1_FP_HR_ALL["total"]
    assert SUPP2_FI_HR_FRAIL["hpa"] == SUPP2_FI_HR_ALL["hpa"]
    # Table 2 item scores
    assert SCORES["adl4"] == {1: 0.0, 2: 0.33, 3: 0.67, 4: 1.0}
    assert SCORES["srh5"][3] == 0.5 and HB_NORMAL_G_DL == {"male": (13.5, 18.0), "female": (12.0, 16.0)}
    assert len(FI_QUESTION_ITEMS) == 43   # + BMI (item 12) + 4 laboratory items = 48


@pytest.mark.parametrize("minutes,cat", [(0, 0), (0.5, 1), (149, 1), (149.9, 1), (150, 2), (299, 2), (300, 3), (900, 3)])
def test_pa_cut_points(minutes, cat):
    assert pr.pa_category(minutes) == cat


@pytest.mark.parametrize("fi,cat", [(0.0, 0), (0.10, 0), (0.1001, 1), (0.21, 1), (0.2101, 2)])
def test_fi_cut_points(fi, cat):
    assert pr.fi_category(fi) == cat


def test_total_pa_lookup(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, PA_OK)
    assert code == 0
    assert result["total_pa_min_per_week"]["value"] == pytest.approx(250.0)
    assert result["total_pa_category"]["value"] == "150–299 分钟/周"
    assert result["total_pa_meets_150"]["value"] == "是"
    assert result["lpa_category"]["value"] == "≥300 分钟/周" and result["hpa_category"]["value"] == "0 分钟/周"
    assert result["fp_beta_total_pa_category"]["value"] == -0.27
    assert result["fi_beta_total_pa_category"]["value"] == -0.02
    assert result["hr_total_pa_category_fp_cohort"]["value"] == 0.875
    assert result["hr_total_pa_category_fi_cohort"]["value"] == 0.875
    assert "-1.169" in report and "-0.659" in report   # Table 4 rows for total and LPA (both >= 150)
    assert result["frailty_index"]["value"] is None and result["fi_items_answered"]["value"] == 0
    assert "## 论文卡片" in report and "边界:" in report and "10.1007/s11357-026-02480-9" in report


def test_hours_convert_and_zero_is_reference(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("HPA", "0", "h"), ("MPA", "0", "h"), ("LPA", "0", "h")])
    assert code == 0
    assert result["total_pa_category"]["value"] == "0 分钟/周"
    assert result["hr_total_pa_category_fp_cohort"]["value"] == 1.0 and "参照组" in report
    code2, result2, _, _ = _run(tmp_path, [("HPA", "2.5", "h"), ("MPA", "0", "min"), ("LPA", "0", "min")], name="hours")
    assert code2 == 0 and result2["total_pa_min_per_week"]["value"] == pytest.approx(300.0)
    assert result2["fp_beta_total_pa_category"]["value"] == -0.77


def test_full_frailty_index_no_deficits(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, PA_OK + _all_items() + LABS_NORMAL, sex="女", age="68")
    assert code == 0
    assert result["fi_items_answered"]["value"] == 48
    assert result["frailty_index"]["value"] == 0.0
    assert result["frailty_index_category"]["value"].startswith("健康")
    assert result["bmi_kg_m2"]["value"] == pytest.approx(22.04, abs=0.01)
    assert result["fp_known_points"]["value"] == 0


def test_full_frailty_index_with_deficits(tmp_path: Path):
    # Every ADL/IADL/function item "need help" (19 x 0.67), self-rated health "average" (0.5),
    # BMI 30 (1), CRP 5 mg/L (1). Sum = 12.73 + 0.5 + 1 + 1 = 15.23; FI = 15.23 / 48.
    rows = PA_OK + _all_items({"adl4": "3", "srh5": "3"}) + [
        ("weight", "81.675", "kg"), ("height", "165", "cm"), ("HbA1c", "5.4", "%"), ("血红蛋白", "14.0", "g/dL"),
        ("CRP", "5", "mg/L"), ("肌酐", "0.8", "mg/dL")]
    code, result, report, _ = _run(tmp_path, rows, sex="male")
    assert code == 0
    assert result["fi_deficit_sum"]["value"] == pytest.approx(15.23, abs=1e-6)
    assert result["frailty_index"]["value"] == pytest.approx(15.23 / 48, abs=1e-4)
    assert result["frailty_index_category"]["value"].startswith("衰弱（")
    # jog 1 km "need help" + BMI >= 25: both known FP items score, FP >= 2 > 1
    assert result["fp_known_points"]["value"] == 2 and "FP>1" in result["fp_status"]["value"]
    assert "补充表 1 的 F 组与 B 组" in report


def test_missing_items_give_bounds_only(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, PA_OK + _all_items())
    assert code == 0
    assert result["fi_items_answered"]["value"] == 43
    assert result["frailty_index"]["value"] is None
    assert result["frailty_index_max"]["value"] == pytest.approx(5 / 48, abs=1e-4)
    # 0/48 if the five missing items were all 0, 5/48 = 0.104 (> 0.10) if all 1: category undecided
    assert result["frailty_index_category"]["value"] is None
    assert "第 12 项" in report and "第 48 项" in report


def test_wrong_unit_out_of_range_is_caught(tmp_path: Path):
    # hemoglobin 140 typed as g/dL is outside 3-25 g/dL
    code, result, report, out = _run(tmp_path, PA_OK + [("血红蛋白", "140", "g/dL")], sex="女")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "hemoglobin_g_dl" and problems[0]["kind"] == "range"
    assert all(item["value"] is None for item in result.values())
    assert "边界:" in report


def test_crp_without_unit_and_bad_code_are_refused(tmp_path: Path):
    code, _, _, out = _run(tmp_path, PA_OK + [("CRP", "2", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"][0]["kind"] == "unit_missing"
    code2, _, _, out2 = _run(tmp_path, PA_OK + [("fi01_bathing", "2.5", "")], name="badcode")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM
    code3, _, _, out3 = _run(tmp_path, [("HPA", "30", "min")], name="nompa")
    assert code3 == skillkit.EXIT_INPUT_PROBLEM
    kinds = {(p["key"], p["kind"]) for p in json.loads((out3 / "problems.json").read_text(encoding="utf-8"))["problems"]}
    assert ("mpa_min_per_week", "missing") in kinds and ("lpa_min_per_week", "missing") in kinds


def test_bad_sex_is_refused(tmp_path: Path):
    code, _, _, _ = _run(tmp_path, PA_OK, sex="x")
    assert code == skillkit.EXIT_INPUT_PROBLEM


def test_manifest_matches_presets():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys[:5] == ["hpa_min_per_week", "mpa_min_per_week", "lpa_min_per_week", "weight_kg", "height_cm"]
    assert keys[5:48] == [item[1] for item in FI_QUESTION_ITEMS]
    assert keys[48:] == ["hba1c_pct", "hemoglobin_g_dl", "crp_mg_l", "creatinine_mg_dl", "sex", "age"]
    for key in ("hpa_min_per_week", "mpa_min_per_week", "lpa_min_per_week"):
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == "min" and spec["required"] is True and spec["accept"] == {"h": 60}
    for _n, key, _zh, _en, _code, kind in FI_QUESTION_ITEMS:
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["range"] == [min(SCORES[kind]), max(SCORES[kind])]
    assert MANIFEST["inputs_status"] == "verified" and MANIFEST["validation"]["status"] == "draft"
    assert MANIFEST["population"]["age_years"][0] == 60
