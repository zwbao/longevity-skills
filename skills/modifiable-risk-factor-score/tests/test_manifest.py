"""Modifiable risk factor score against the numbers Chen et al. 2026 print.

Expected values come only from the paper: the cutoffs of Supplementary Method S1,
the per-point hazard ratios of Supplementary Table S11 and the Results text.
The paper prints no per-person worked example, so validation stays draft.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import presets
import skillkit

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))

NONE_FLAGS = {"education_junior_middle": True, "depressive_symptoms": False, "ever_smoked": False, "ever_drank": False,
              "diabetes_diagnosed": False, "glucose_lowering_medication": False, "hypertension_diagnosed": False,
              "antihypertensive_medication": False, "hyperlipidemia_diagnosed": False, "lipid_lowering_medication": False}
NONE_VALUES = {"pa_met_h_week": 20, "diet_score": 8, "sleep_hours": 7, "bmi_kg_m2": 22, "sbp_mmhg": 120, "dbp_mmhg": 75,
               "fasting_glucose_mmol_l": 5.0, "tc_mmol_l": 4.5, "ldl_c_mmol_l": 2.6, "hdl_c_mmol_l": 1.4, "tg_mmol_l": 1.2}
ROWS = [("体力活动", "20", "MET-h/week"), ("健康饮食得分", "8", ""), ("睡眠时长", "7", "h"), ("BMI", "22", "kg/m2"),
        ("收缩压", "120", "mmHg"), ("舒张压", "75", "mmHg"), ("空腹血糖", "5.0", "mmol/L"), ("总胆固醇", "4.5", "mmol/L"),
        ("LDL-C", "2.6", "mmol/L"), ("HDL-C", "1.4", "mmol/L"), ("甘油三酯", "1.2", "mmol/L")]
ARGS_NONE = ["--education-junior-middle", "yes", "--depressive-symptoms", "no", "--ever-smoked", "no", "--ever-drank", "no",
             "--diabetes-diagnosed", "no", "--glucose-lowering-medication", "no", "--hypertension-diagnosed", "no",
             "--antihypertensive-medication", "no", "--hyperlipidemia-diagnosed", "no", "--lipid-lowering-medication", "no"]


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _state(**changes):
    values = dict(NONE_VALUES)
    flags = dict(NONE_FLAGS)
    for key, value in changes.items():
        (flags if key in flags else values)[key] = value
    return personal_report.classify(values, flags)


# Supplementary Table S11, "Modifiable risk score" column, printed:
# Middle age 1.231(1.102,1.374); Presenium 1.235(1.185,1.288); Younger old 1.236(1.214,1.259);
# Oldest old 1.106(1.010,1.211); Centenarian 1.118(1.069,1.170).
@pytest.mark.parametrize("age,group,hr", [(40, "middle_age", 1.231), (55, "presenium", 1.235), (70, "younger_old", 1.236),
                                          (90, "oldest_old", 1.106), (102, "centenarian", 1.118)])
def test_table_s11_per_point_hr_by_age_group(age, group, hr):
    result = personal_report.compute(NONE_VALUES, NONE_FLAGS, age)
    assert result["age_group"] == group
    assert result["hr_per_point"] == hr


def test_age_group_edges_follow_the_paper():
    # Methods: 30-49, 50-59, 60-79, 80-99, >= 100 years.
    assert [personal_report.age_group(a)[0] for a in (30, 49, 50, 59, 60, 79, 80, 99, 100)] == [
        "middle_age", "middle_age", "presenium", "presenium", "younger_old", "younger_old", "oldest_old", "oldest_old", "centenarian"]


def test_table_s11_matches_the_results_text():
    # Results: "1.43 (1.14-1.80) in middle-aged individuals to 1.07 (0.99-1.17) in centenarians" (metabolic score)
    # and the modifiable score range starting "1.11 (1.01-1.21)" (oldest-old).
    metabolic_mid = presets.TABLE_S11["middle_age"]["metabolic"]
    assert metabolic_mid == (1.430, 1.138, 1.797)
    assert [round(x, 2) for x in metabolic_mid] == [1.43, 1.14, 1.80]
    assert [round(x, 2) for x in presets.TABLE_S11["centenarian"]["metabolic"]] == [1.07, 0.99, 1.17]
    assert [round(x, 2) for x in presets.TABLE_S11["oldest_old"]["modifiable"]] == [1.11, 1.01, 1.21]


def test_method_s1_cutoffs():
    assert sum(_state().values()) == 0
    assert _state(pa_met_h_week=10)["physical_inactivity"] == 0
    assert _state(pa_met_h_week=9.9)["physical_inactivity"] == 1
    assert _state(diet_score=6)["unhealthy_diet"] == 1
    assert _state(diet_score=7)["unhealthy_diet"] == 0
    assert _state(sleep_hours=6)["abnormal_sleep"] == 0 and _state(sleep_hours=8)["abnormal_sleep"] == 0
    assert _state(sleep_hours=5.5)["abnormal_sleep"] == 1 and _state(sleep_hours=9)["abnormal_sleep"] == 1
    assert _state(bmi_kg_m2=18.5)["abnormal_bmi"] == 0 and _state(bmi_kg_m2=28)["abnormal_bmi"] == 0
    assert _state(bmi_kg_m2=18.4)["abnormal_bmi"] == 1 and _state(bmi_kg_m2=28.1)["abnormal_bmi"] == 1
    assert _state(fasting_glucose_mmol_l=7.0)["diabetes"] == 1
    assert _state(fasting_glucose_mmol_l=6.9)["diabetes"] == 0
    assert _state(glucose_lowering_medication=True)["diabetes"] == 1
    assert _state(sbp_mmhg=140)["hypertension"] == 1 and _state(dbp_mmhg=90)["hypertension"] == 1
    assert _state(sbp_mmhg=139, dbp_mmhg=89)["hypertension"] == 0
    assert _state(antihypertensive_medication=True)["hypertension"] == 1
    assert _state(ldl_c_mmol_l=4.14)["dyslipidemia"] == 1 and _state(hdl_c_mmol_l=1.03)["dyslipidemia"] == 1
    assert _state(hdl_c_mmol_l=1.04)["dyslipidemia"] == 0
    assert _state(tg_mmol_l=2.26)["dyslipidemia"] == 1 and _state(tc_mmol_l=6.22)["dyslipidemia"] == 1
    assert _state(education_junior_middle=False)["low_education"] == 1
    assert _state(ever_smoked=True)["smoking"] == 1 and _state(ever_drank=True)["alcohol"] == 1
    assert _state(depressive_symptoms=True)["depression"] == 1


def test_gds15_cutoff_and_either_instrument():
    values = dict(NONE_VALUES, gds15_score=6)
    flags = dict(NONE_FLAGS, depressive_symptoms=None)
    assert personal_report.classify(values, flags)["depression"] == 1
    assert personal_report.classify(dict(values, gds15_score=5), flags)["depression"] == 0
    assert personal_report.classify(NONE_VALUES, flags)["depression"] is None


def test_positive_criterion_decides_without_the_rest():
    values = {k: v for k, v in NONE_VALUES.items() if k not in ("fasting_glucose_mmol_l",)}
    flags = dict(NONE_FLAGS, diabetes_diagnosed=True)
    assert personal_report.classify(values, flags)["diabetes"] == 1
    assert personal_report.classify(values, NONE_FLAGS)["diabetes"] is None


def test_report_result_and_levers(tmp_path: Path):
    rows = [r for r in ROWS if r[0] != "BMI"] + [("体重", "85", "kg"), ("身高", "170", "cm")]  # BMI 29.4
    m = _csv(tmp_path / "m.csv", rows)
    t = _csv(tmp_path / "t.csv", [("体重", "75", "kg"), ("睡眠时长", "7", "h")])
    args = ["--measurements", str(m), "--age", "55", *ARGS_NONE, "--targets", str(t), "--out", str(tmp_path / "out")]
    args[args.index("--ever-smoked") + 1] = "yes"
    assert personal_report.main(args) == 0
    out = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert out["modifiable_risk_score"]["value"] == 2
    assert out["behavior_risk_score"]["value"] == 1 and out["metabolic_risk_score"]["value"] == 1
    assert out["age_group"]["value"] == "presenium"
    assert out["hr_per_point"]["value"] == 1.235
    assert out["relative_hazard_vs_zero"]["value"] == pytest.approx(1.235 ** 2)
    levers = json.loads((tmp_path / "out" / "levers.json").read_text(encoding="utf-8"))
    weight = next(item for item in levers["levers"] if item["key"] == "weight_kg")
    assert weight["score_delta"] == -1 and weight["relative_hazard_factor"] == pytest.approx(1 / 1.235)
    assert levers["targets"]["modifiable_risk_score"] == 1
    report = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "边界" in report and "补充表 S11" in report and "1.235（1.185–1.288）" in report
    assert "停药" in report


def test_wrong_unit_and_out_of_range_stop(tmp_path: Path):
    rows = [r for r in ROWS if r[0] not in ("空腹血糖", "睡眠时长")] + [("空腹血糖", "95", "mmol/L"), ("睡眠时长", "7", "kg")]
    m = _csv(tmp_path / "m.csv", rows)
    code = personal_report.main(["--measurements", str(m), "--age", "55", *ARGS_NONE, "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    kinds = {(p["key"], p["kind"]) for p in json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))["problems"]}
    assert ("fasting_glucose_mmol_l", "range") in kinds and ("sleep_hours", "unit") in kinds
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["modifiable_risk_score"]["value"] is None
    assert "项（满分 11）" not in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


def test_mg_dl_glucose_converts(tmp_path: Path):
    rows = [r for r in ROWS if r[0] != "空腹血糖"] + [("空腹血糖", "130", "mg/dL")]
    m = _csv(tmp_path / "m.csv", rows)
    assert personal_report.main(["--measurements", str(m), "--age", "40", *ARGS_NONE, "--out", str(tmp_path / "out")]) == 0
    out = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert out["metabolic_risk_score"]["value"] == 1  # 130 mg/dL = 7.2 mmol/L >= 7.0


def test_missing_factor_and_age_below_30_stop(tmp_path: Path):
    m = _csv(tmp_path / "m.csv", [r for r in ROWS if r[0] != "健康饮食得分"])
    code = personal_report.main(["--measurements", str(m), "--age", "55", *ARGS_NONE, "--out", str(tmp_path / "a")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((tmp_path / "a" / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert [(p["key"], p["kind"]) for p in problems] == [("unhealthy_diet", "missing")]
    m = _csv(tmp_path / "m2.csv", ROWS)
    code = personal_report.main(["--measurements", str(m), "--age", "25", *ARGS_NONE, "--out", str(tmp_path / "b")])
    assert code == skillkit.EXIT_INPUT_PROBLEM


def test_manifest_matches_presets():
    keys = {item["key"] for item in MANIFEST["inputs"]}
    assert set(personal_report.FLAGS) <= keys
    assert set(personal_report.TARGETABLE) <= keys
    assert {key for key, _l, _c in presets.FACTORS} == set(personal_report.MISSING_ZH)
    units = {item["key"]: item.get("unit") for item in MANIFEST["inputs"]}
    assert units["sbp_mmhg"] == "mmHg" and units["fasting_glucose_mmol_l"] == "mmol/L" and units["sleep_hours"] == "h"
    assert {o["key"] for o in MANIFEST["outputs"]} == {
        "modifiable_risk_score", "sep_risk_score", "behavior_risk_score", "metabolic_risk_score", "age_group",
        "hr_per_point", "relative_hazard_vs_zero"}
    assert MANIFEST["validation"]["status"] == "draft"
    assert len(presets.FACTORS) == 11


def test_weight_target_overrides_a_given_bmi():
    values = dict(NONE_VALUES, bmi_kg_m2=29.4, height_cm=170, weight_kg=85)
    out = personal_report.levers(values, NONE_FLAGS, 55, {"weight_kg": 75})
    assert out["levers"][0]["score_delta"] == -1
    no_height = personal_report.levers(dict(NONE_VALUES, bmi_kg_m2=29.4), NONE_FLAGS, 55, {"weight_kg": 75})
    assert no_height["levers"] == [] and "身高" in no_height["skipped_zh"]


def test_ever_smoked_is_not_offered_as_a_lever():
    out = personal_report.levers(NONE_VALUES, dict(NONE_FLAGS, ever_smoked=True), 55, {})
    smoking = next(item for item in out["sensitivity"] if item["key"] == "smoking")
    assert smoking["not_a_target"] is True and "已戒烟" in smoking["reason_zh"]
