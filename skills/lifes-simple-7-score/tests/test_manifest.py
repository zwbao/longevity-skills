"""LS7 (HANDLS scoring) against the paper's own numbers.

The printed example: Table S4 (ESM 1) prints the mean score of each of the
seven components for women and men, and the Results print the mean LS7 totals
(7.38 vs. 7.78). Because the total is the sum of the seven 0-2 point
components, the printed component means must add up to the printed totals.
The component cutoffs are checked at the boundaries printed in Table S1A and
Supplementary Methods 2.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report  # noqa: E402
import presets  # noqa: E402
import skillkit  # noqa: E402

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
UNTREATED = ["--bp-treated", "no", "--chol-treated", "no", "--glucose-treated", "no"]
ALL_IDEAL = [("BMI", "22", "kg/m^2"), ("收缩压", "115", "mmHg"), ("舒张压", "75", "mmHg"), ("总胆固醇", "4.5", "mmol/L"),
             ("空腹血糖", "5.0", "mmol/L"), ("中等强度运动", "180", "min"), ("高强度运动", "0", "min"), ("饮食目标数", "4", "")]


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, smoking="never", flags=UNTREATED, targets=None):
    args = ["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(tmp_path / "out"), *flags]
    if smoking is not None:
        args += ["--smoking", smoking]
    if targets is not None:
        args += ["--targets", str(_csv(tmp_path / "t.csv", targets))]
    code = personal_report.main(args)
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    return code, result


def test_component_means_add_up_to_printed_total():
    # Table S4 means (two decimals) summed with the script's total rule; printed totals 7.38 (women) and 7.78 (men).
    assert presets.PRINTED_MEAN_TOTAL == {"women": 7.38, "men": 7.78}
    women = personal_report.total_score(presets.TABLE_S4_SUBSCORES["women"])
    men = personal_report.total_score(presets.TABLE_S4_SUBSCORES["men"])
    assert women == pytest.approx(7.38, abs=0.035)
    assert men == pytest.approx(7.78, abs=0.035)


def test_total_needs_all_seven_components():
    partial = dict(presets.TABLE_S4_SUBSCORES["women"])
    partial.pop("diet")
    with pytest.raises(KeyError):
        personal_report.total_score(partial)


def test_manifest_keys_units_match_presets():
    keys = {spec["key"]: spec for spec in MANIFEST["inputs"]}
    assert set(personal_report.MEASUREMENT_KEYS) <= set(keys)
    assert keys["tc_mg_dl"]["unit"] == "mg/dL" and keys["glucose_mg_dl"]["unit"] == "mg/dL"
    assert keys["bmi_kg_m2"]["unit"] == "kg/m^2" and keys["sbp_mmhg"]["unit"] == "mmHg"
    assert {f"{name}_points" for name in presets.COMPONENTS} | {"ls7_total", "ls7_band"} == {o["key"] for o in MANIFEST["outputs"]}
    assert set(presets.SMOKING_LEVEL) == {"never", "quit_over_1y", "quit_within_1y", "current"}


@pytest.mark.parametrize("bmi,level", [(24.9, "ideal"), (25, "intermediate"), (29.9, "intermediate"), (30, "poor")])
def test_bmi_cutoffs_table_s1a(bmi, level):
    assert personal_report.level_bmi(bmi) == level


@pytest.mark.parametrize("sbp,dbp,treated,level", [
    (119, 79, False, "ideal"), (119, 79, True, "intermediate"), (120, 70, False, "intermediate"),
    (110, 80, False, "intermediate"), (139, 89, False, "intermediate"), (140, 70, False, "poor"), (110, 90, True, "poor")])
def test_blood_pressure_cutoffs_table_s1a(sbp, dbp, treated, level):
    assert personal_report.level_bp(sbp, dbp, treated) == level


@pytest.mark.parametrize("tc,treated,level", [(199, False, "ideal"), (199, True, "intermediate"), (200, False, "intermediate"),
                                              (239, False, "intermediate"), (240, False, "poor")])
def test_cholesterol_cutoffs_table_s1a(tc, treated, level):
    assert personal_report.level_lab(tc, presets.TC_IDEAL_BELOW, presets.TC_POOR_AT, treated) == level


@pytest.mark.parametrize("glu,treated,level", [(99, False, "ideal"), (99, True, "intermediate"), (100, False, "intermediate"),
                                               (125, False, "intermediate"), (126, False, "poor")])
def test_glucose_cutoffs_table_s1a(glu, treated, level):
    assert personal_report.level_lab(glu, presets.GLUCOSE_IDEAL_BELOW, presets.GLUCOSE_POOR_AT, treated) == level


@pytest.mark.parametrize("goals,level", [(5, "ideal"), (4, "ideal"), (3, "intermediate"), (2, "intermediate"), (1, "poor"), (0, "poor")])
def test_diet_cutoffs_table_s1a(goals, level):
    assert personal_report.level_diet(goals) == level


@pytest.mark.parametrize("mod,vig,level,mixed", [(150, 0, "ideal", False), (0, 75, "ideal", False), (149, 0, "intermediate", False),
                                                 (0, 0, "poor", False), (100, 40, "intermediate", True)])
def test_activity_cutoffs_methods_1_4(mod, vig, level, mixed):
    assert personal_report.level_activity(mod, vig) == (level, mixed)


def test_all_ideal_scores_14_with_unit_conversion(tmp_path: Path):
    code, result = _run(tmp_path, ALL_IDEAL)
    assert code == 0
    assert result["outputs"]["ls7_total"]["value"] == 14
    assert result["outputs"]["ls7_band"]["value"].startswith("较好")
    report = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "边界" in report and presets.BOUNDARY in report and "DOI" in report.upper()


def test_mixed_person_and_levers(tmp_path: Path):
    rows = [("BMI", "31", "kg/m^2"), ("SBP", "145", "mmHg"), ("DBP", "85", "mmHg"), ("TC", "220", "mg/dL"),
            ("FPG", "105", "mg/dL"), ("中等强度运动", "60", "min"), ("高强度运动", "0", "min"), ("饮食目标数", "1", "")]
    code, result = _run(tmp_path, rows, smoking="quit_over_1y", targets=[("SBP", "118", "mmHg"), ("DBP", "75", "mmHg"),
                                                                         ("中等强度运动", "150", "min")])
    assert code == 0
    out = result["outputs"]
    # smoking 2, diet 0, activity 1, BMI 0, BP 0, TC 1, glucose 1
    assert [out[f"{n}_points"]["value"] for n in presets.COMPONENTS] == [2, 0, 1, 0, 0, 1, 1]
    assert out["ls7_total"]["value"] == 5
    report = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "总分会低 1 分" in report
    levers = json.loads((tmp_path / "out" / "levers.json").read_text(encoding="utf-8"))
    assert levers["current"]["ls7_total"] == 5
    assert levers["targets"]["ls7_total"] == 8
    deltas = {item["key"]: item["score_delta"] for item in levers["levers"]}
    assert deltas["pa_moderate_min_wk"] == 1


def test_glucose_without_unit_out_of_range_exits_3(tmp_path: Path):
    rows = [row if row[0] != "空腹血糖" else ("空腹血糖", "5.0", "") for row in ALL_IDEAL]
    code, result = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("glucose_mg_dl", "range") in {(p["key"], p["kind"]) for p in problems}
    assert result["outputs"]["ls7_total"]["value"] is None
    assert "LS7 总分 **" not in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


def test_wrong_unit_and_missing_smoking_exit_3(tmp_path: Path):
    rows = [row if row[0] != "BMI" else ("BMI", "22", "kg") for row in ALL_IDEAL]
    code, result = _run(tmp_path, rows, smoking=None)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    kinds = {(p["key"], p["kind"]) for p in json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))["problems"]}
    assert ("bmi_kg_m2", "unit") in kinds and ("smoking", "missing") in kinds
    assert result["outputs"]["ls7_total"]["value"] is None


def test_non_integer_diet_goals_and_bad_flag_exit_3(tmp_path: Path):
    rows = [row if row[0] != "饮食目标数" else ("饮食目标数", "2.5", "") for row in ALL_IDEAL]
    code, _ = _run(tmp_path, rows, flags=["--bp-treated", "maybe", "--chol-treated", "no", "--glucose-treated", "no"])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    kinds = {(p["key"], p["kind"]) for p in json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))["problems"]}
    assert ("diet_goals_met", "parse") in kinds and ("bp_treated", "parse") in kinds
