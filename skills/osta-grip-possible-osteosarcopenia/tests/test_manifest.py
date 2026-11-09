"""Possible osteosarcopenia (OSTA + AWGS 2019 handgrip) against Koh et al., J Gerontol A 2026 (TARGET).

Constants are checked against the printed Methods text: OSTA = 0.2 x [weight (kg) - age],
high < -4, moderate -4 to -1, low > -1, possible osteoporosis at <= -1; handgrip
< 18 kg (women) and < 28 kg (men). The paper and its supplement print no individual
example (no weight, age and grip with a resulting OSTA or class), so these tests check
the formula and the cut points only (validation stays draft). All inputs are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import (COGNITION_OR, COHORT, GRIP_CUT_KG, IC_BETA, MINIMOCA_INTERACTION, MINIMOCA_JOINT, OSTA_FACTOR,
                     OSTA_HIGH_BELOW, OSTA_POSSIBLE_OSTEOPOROSIS_MAX, SCREENING, TABLE_S12)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, sex="女", age="75", name="out"):
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
    # Methods "Possible osteoporosis" and "Possible sarcopenia".
    assert OSTA_FACTOR == 0.2 and OSTA_HIGH_BELOW == -4.0 and OSTA_POSSIBLE_OSTEOPOROSIS_MAX == -1.0
    assert GRIP_CUT_KG == {"female": 18.0, "male": 28.0}
    # Cohort numbers, report context only.
    assert (COHORT["n"], COHORT["prevalence_pct"], COHORT["n_possible"]) == (2291, 50.3, 1153)
    assert IC_BETA == (-0.21, -0.29, -0.14) and COGNITION_OR == (0.45, 0.34, 0.60)
    assert MINIMOCA_INTERACTION == (-0.59, -1.16, -0.03) and MINIMOCA_JOINT == -1.74
    assert TABLE_S12[("loss", "possible")] == (11.08, 10.79, 11.36)
    assert (SCREENING["sensitivity"], SCREENING["specificity"], SCREENING["ppv"], SCREENING["n"]) == (92.3, 71.4, 48.6, 515)


@pytest.mark.parametrize("weight,age,index,risk", [
    (55.0, 60, -1.0, "moderate"),   # exactly -1 is moderate (possible osteoporosis)
    (55.5, 60, -0.9, "low"),
    (40.0, 60, -4.0, "moderate"),   # exactly -4 is moderate, not high
    (39.5, 60, -4.1, "high"),
    (70.0, 65, 1.0, "low"),
    (45.0, 80, -7.0, "high"),
])
def test_osta_formula_and_groups(weight, age, index, risk):
    value = pr.osta_index(weight, age)
    assert value == pytest.approx(index)
    assert pr.osta_risk(value) == risk
    assert pr.possible_osteoporosis(value) is (risk != "low")


@pytest.mark.parametrize("grip,sex,low", [
    (17.5, "female", True), (18.0, "female", False), (27.5, "male", True), (28.0, "male", False), (20.0, "male", True),
])
def test_awgs_grip_cut_points(grip, sex, low):
    assert pr.possible_sarcopenia(grip, sex) is low


def test_both_criteria_give_possible_osteosarcopenia(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("体重", "48", "kg"), ("握力", "15.5", "kg")], sex="女", age="78")
    assert code == 0
    assert result["osta_index"]["value"] == pytest.approx(-6.0)
    assert result["possible_osteoporosis"]["value"] == "是"
    assert result["possible_sarcopenia"]["value"] == "是"
    assert result["possible_osteosarcopenia"]["value"] == "是"
    assert "高风险" in result["osta_risk_category"]["value"]
    assert "## 论文卡片" in report and "边界:" in report and "10.1093/gerona/glag211" in report
    assert "筛查阳性，不是诊断" in report


def test_one_criterion_only(tmp_path: Path):
    # Man, 70 y, 62 kg -> OSTA -1.6 (possible osteoporosis); grip 30 kg is not low.
    code, result, report, _ = _run(tmp_path, [("weight", "62", "kg"), ("grip strength", "30", "kg")], sex="男", age="70")
    assert code == 0
    assert result["osta_index"]["value"] == pytest.approx(-1.6)
    assert result["possible_osteoporosis"]["value"] == "是" and result["possible_sarcopenia"]["value"] == "否"
    assert result["possible_osteosarcopenia"]["value"] == "否"
    assert "只符合“可能骨质疏松”一条" in report


def test_neither(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("weight_kg", "75", ""), ("grip_strength_kg", "35", "")], sex="male", age="66")
    assert code == 0
    assert result["possible_osteosarcopenia"]["value"] == "否" and "两条都不符合" in report


def test_pounds_convert(tmp_path: Path):
    code, result, _, _ = _run(tmp_path, [("体重", "110", "lb"), ("握力", "30", "lb")], sex="女", age="72")
    assert code == 0
    assert result["osta_index"]["value"] == pytest.approx(0.2 * (110 * 0.45359237 - 72), abs=0.01)
    assert result["possible_sarcopenia"]["value"] == "是"   # 30 lb = 13.6 kg < 18 kg


def test_under_60_is_noted(tmp_path: Path):
    _, _, report, _ = _run(tmp_path, [("体重", "60", "kg"), ("握力", "25", "kg")], age="50")
    assert "不在论文人群" in report


def test_unit_missing_is_refused(tmp_path: Path):
    # 150 without a unit could be lb or kg: refused, nothing computed.
    code, result, report, out = _run(tmp_path, [("体重", "150", ""), ("握力", "20", "kg")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "weight_kg" and problems[0]["kind"] == "unit_missing"
    assert all(item["value"] is None for item in result.values())
    assert "## 结果" not in report and "可能骨肌减少症（两项都是）" not in report


def test_out_of_range_is_refused(tmp_path: Path):
    # A grip of 150 kg is outside the 1-100 kg range.
    code, result, _, out = _run(tmp_path, [("体重", "60", "kg"), ("握力", "150", "kg")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert (problems[0]["key"], problems[0]["kind"]) == ("grip_strength_kg", "range")
    assert all(item["value"] is None for item in result.values())


def test_missing_sex_age_or_grip_is_refused(tmp_path: Path):
    code, _, report, _ = _run(tmp_path, [("体重", "60", "kg"), ("握力", "20", "kg")], sex=None, name="nosex")
    assert code == skillkit.EXIT_INPUT_PROBLEM and "握力切点男女不同" in report
    code, _, _, _ = _run(tmp_path, [("体重", "60", "kg"), ("握力", "20", "kg")], age=None, name="noage")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    code, _, _, out = _run(tmp_path, [("体重", "60", "kg")], name="nogrip")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("grip_strength_kg", "missing") in {(p["key"], p["kind"]) for p in problems}
    code, _, _, _ = _run(tmp_path, [("体重", "60", "kg"), ("握力", "20", "kg")], sex="x", name="badsex")
    assert code == skillkit.EXIT_INPUT_PROBLEM


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == ["weight_kg", "grip_strength_kg", "age", "sex"]
    assert skillkit.spec_by_key(MANIFEST, "weight_kg")["unit"] == "kg"
    assert skillkit.spec_by_key(MANIFEST, "grip_strength_kg")["unit"] == "kg"
    assert skillkit.spec_by_key(MANIFEST, "sex")["required"] is True
    assert MANIFEST["population"]["age_years"][0] == COHORT["min_age"]
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "draft"
    assert [o["key"] for o in MANIFEST["outputs"]] == ["osta_index", "osta_risk_category", "possible_osteoporosis",
                                                      "possible_sarcopenia", "possible_osteosarcopenia"]
