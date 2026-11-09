"""Two-wave handgrip patterns and hazard ratios against Xu, Lin & Ran, GeroScience 2026 (CHARLS).

Expected hazard ratios are the Table 2 values as printed in the Results text, which equal the
"Unweighted HR (95% CI)" column of Supplementary Table S14; the comorbidity strata are
Supplementary Table S12 and the continuous metrics Supplementary Table S11. Cut points come from
Methods "Assessment of muscle phenotypes and two-wave status patterns". The paper prints no
individual worked example, so these tests check the classification and the table lookup only
(validation stays draft). All inputs are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import (COHORT, DELTA_AAI_HR, DELTA_AAI_KNOTS, HGSA_HR, HGSA_RATIO_HIGH, HGSA_RATIO_LOW, JOINT_HR,
                     LHGS_HR, LHGS_KG, LOSS_RGS_HR, LOSS_RGS_KNOTS, PATTERN_ZH, S10_HGSA, S10_LHGS, S12_HGSA,
                     S12_JOINT, S12_LHGS)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
GRIP_KEYS = ["grip_left_w1_kg", "grip_right_w1_kg", "grip_left_w2_kg", "grip_right_w2_kg"]


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _grips(l1, r1, l2, r2, unit="kg"):
    return [("第一次左手握力", str(l1), unit), ("第一次右手握力", str(r1), unit),
            ("第二次左手握力", str(l2), unit), ("第二次右手握力", str(r2), unit)]


def _run(tmp_path: Path, rows, age="68", sex="男", hand="右手", chronic=None, name="out"):
    m = _csv(tmp_path / f"{name}.csv", rows)
    out = tmp_path / name
    args = ["--measurements", str(m), "--out", str(out)]
    for flag, val in (("--age", age), ("--sex", sex), ("--dominant-hand", hand), ("--chronic-conditions", chronic)):
        if val is not None:
            args += [flag, val]
    code = pr.main(args)
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


def test_constants_are_as_printed():
    assert (HGSA_RATIO_LOW, HGSA_RATIO_HIGH) == (0.90, 1.10)
    assert LHGS_KG == {("male", "under65"): 34.0, ("female", "under65"): 20.0,
                       ("male", "65plus"): 28.0, ("female", "65plus"): 18.0}
    # Table 2 (Results text) = Supplementary Table S14 unweighted column.
    assert HGSA_HR[1:] == ((1.07, 0.86, 1.33), (0.97, 0.78, 1.22), (1.32, 1.07, 1.61))
    assert LHGS_HR[1:] == ((1.91, 1.54, 2.37), (1.54, 1.21, 1.97), (2.35, 1.88, 2.94))
    assert JOINT_HR[1:] == ((1.22, 1.02, 1.46), (2.30, 1.84, 2.87))
    # Supplementary Table S11.
    assert DELTA_AAI_HR == (1.66, 1.14, 2.42) and DELTA_AAI_KNOTS == (-0.133949, 0.000734, 0.142560)
    assert LOSS_RGS_HR == (2.39, 1.86, 3.08) and LOSS_RGS_KNOTS == (-0.398013, 0.049102, 0.476531)
    # Supplementary Table S12 (spot checks across all three panels).
    assert S12_HGSA[2][3] == (1.62, 1.19, 2.23) and S12_HGSA[0][3] == (0.88, 0.56, 1.39)
    assert S12_LHGS[1][3] == (2.76, 1.91, 3.98) and S12_LHGS[0][2] == (1.10, 0.62, 1.97)
    assert S12_JOINT[0][2] == (1.98, 1.21, 3.24) and S12_JOINT[2][1] == (1.26, 0.96, 1.66)
    # Supplementary Table S10 group sizes add up to the analytic sample.
    assert sum(n for _, n, _ in S10_HGSA) == COHORT["n"] == sum(n for _, n, _ in S10_LHGS)
    assert sum(d for d, _, _ in S10_HGSA) == COHORT["deaths"] == sum(d for d, _, _ in S10_LHGS)


@pytest.mark.parametrize("ratio,flag", [(0.90, False), (0.8999, True), (1.10, False), (1.1001, True), (1.0, False)])
def test_hgsa_cut_points(ratio, flag):
    assert pr.is_hgsa(ratio) is flag


@pytest.mark.parametrize("sex,age,kg,flag", [
    ("male", 64, 33.9, True), ("male", 64, 34.0, False), ("male", 65, 33.9, False), ("male", 65, 27.9, True),
    ("female", 64, 19.9, True), ("female", 64, 20.0, False), ("female", 65, 18.0, False), ("female", 70, 17.9, True),
])
def test_lhgs_cut_points(sex, age, kg, flag):
    assert pr.is_lhgs(kg, sex, age) is flag


def test_exact_boundary_ratios_are_not_asymmetric():
    for left, right in ((27.0, 30.0), (33.0, 30.0), (22.5, 25.0), (19.8, 18.0)):
        assert pr.is_hgsa(pr.grip_ratio(left, right, "right")) is False


def test_ratio_uses_dominant_hand():
    assert pr.grip_ratio(27.0, 30.0, "right") == pytest.approx(0.9)
    assert pr.grip_ratio(27.0, 30.0, "left") == pytest.approx(30.0 / 27.0)
    assert pr.grip_ratio(33.0, 30.0, "both") == pytest.approx(30.0 / 33.0)


@pytest.mark.parametrize("w1,w2,idx", [(False, False, 0), (False, True, 1), (True, False, 2), (True, True, 3)])
def test_pattern_index(w1, w2, idx):
    assert pr.pattern(w1, w2) == idx


def test_paper_table2_lookup_new_abnormal(tmp_path: Path):
    # Man, 66 then 68: W1 30/32 kg (ratio 0.938, max 32 >= 28); W2 22/27 kg (ratio 0.815, max 27 < 28).
    rows = _grips(30, 32, 22, 27) + [("第一次测量时年龄", "66", "a")]
    code, result, report, _ = _run(tmp_path, rows)
    assert code == 0
    assert result["hgsa_pattern"]["value"] == PATTERN_ZH[1] and result["hgsa_pattern_hr"]["value"] == 1.07
    assert result["lhgs_pattern"]["value"] == PATTERN_ZH[1] and result["lhgs_pattern_hr"]["value"] == 1.91
    assert result["joint_score_w2"]["value"] == 2 and result["joint_score_hr"]["value"] == 2.30
    assert "1.54–2.37" in report and "1.84–2.87" in report and "0.86–1.33" in report
    assert result["delta_aai"]["value"] == pytest.approx(abs(22 / 27 - 1) - abs(30 / 32 - 1), abs=1e-4)
    assert result["loss_rgs"]["value"] is None and "需要两次测量时的体质指数" in report
    assert "## 论文卡片" in report and "边界:" in report and "10.1007/s11357-026-02558-4" in report


def test_paper_table2_lookup_abnormal_both(tmp_path: Path):
    # Woman, 60: W1 15/19 kg (ratio 0.789, max 19 < 20); W2 14/18 kg (ratio 0.778, max 18 < 20).
    rows = _grips(15, 19, 14, 18) + [("第一次体质指数", "24", "kg/m^2"), ("第二次体质指数", "23", "kg/m^2")]
    code, result, report, _ = _run(tmp_path, rows, age="60", sex="女", chronic="3")
    assert code == 0
    assert result["hgsa_pattern_hr"]["value"] == 1.32 and result["lhgs_pattern_hr"]["value"] == 2.35
    assert result["joint_score_hr"]["value"] == 2.30
    assert result["loss_rgs"]["value"] == pytest.approx(19 / 24 - 18 / 23, abs=1e-4)
    assert "2 种及以上慢病" in report and "1.62（95% 置信区间 1.19–2.23）" in report and "2.00（95% 置信区间 1.42–2.80）" in report


def test_normalized_lhgs_and_reference(tmp_path: Path):
    # Man 70 (both waves >= 65): W1 max 26 < 28, W2 max 30 >= 28 -> normalized; ratios inside 0.90-1.10.
    code, result, report, _ = _run(tmp_path, _grips(25, 26, 29, 30), age="70")
    assert code == 0
    assert result["lhgs_pattern"]["value"] == PATTERN_ZH[2] and result["lhgs_pattern_hr"]["value"] == 1.54
    assert result["hgsa_pattern"]["value"] == PATTERN_ZH[0] and result["hgsa_pattern_hr"]["value"] == 1.0
    assert result["joint_score_w2"]["value"] == 0 and "恢复" in report
    assert "没有给第一次测量时的年龄" in report


def test_all_normal_is_reference(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, _grips(38, 40, 37, 39), age="55")
    assert code == 0
    assert result["hgsa_pattern_hr"]["value"] == 1.0 and result["lhgs_pattern_hr"]["value"] == 1.0
    assert "好的信号" in report and "参照组" in report


def test_lb_input_converts(tmp_path: Path):
    code, result, _, _ = _run(tmp_path, _grips(66, 70, 66, 70, unit="lb"), age="55")
    assert code == 0 and result["max_grip_w1_kg"]["value"] == pytest.approx(70 * 0.45359237)


def test_unitless_alias_row_is_refused(tmp_path: Path):
    # Grip typed without a unit could be lb or kg: refused.
    code, result, _, out = _run(tmp_path, _grips(66, 70, 66, 70, unit=""))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert {p["kind"] for p in problems} == {"unit_missing"}
    assert all(item["value"] is None for item in result.values())


def test_out_of_range_and_missing_are_refused(tmp_path: Path):
    code, _, _, out = _run(tmp_path, _grips(300, 32, 22, 27))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("grip_left_w1_kg", "range") in {(p["key"], p["kind"]) for p in problems}
    code2, _, report2, out2 = _run(tmp_path, _grips(30, 32, 22, 27)[:3], name="missing")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM and "1.91" not in report2.split("## 输入没有通过检查")[1]
    keys = {(p["key"], p["kind"]) for p in json.loads((out2 / "problems.json").read_text(encoding="utf-8"))["problems"]}
    assert ("grip_right_w2_kg", "missing") in keys


@pytest.mark.parametrize("kw,key", [({"sex": "x"}, "sex"), ({"sex": None}, "sex"), ({"hand": "脚"}, "dominant_hand"),
                                    ({"hand": None}, "dominant_hand"), ({"age": None}, "age")])
def test_bad_profile_is_refused(tmp_path: Path, kw, key):
    code, _, _, out = _run(tmp_path, _grips(30, 32, 22, 27), **kw)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert key in {p["key"] for p in json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]}


def test_first_age_after_second_is_refused(tmp_path: Path):
    code, _, _, _ = _run(tmp_path, _grips(30, 32, 22, 27) + [("第一次测量时年龄", "70", "a")], age="68")
    assert code == skillkit.EXIT_INPUT_PROBLEM


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == GRIP_KEYS + ["age_w1_years", "bmi_w1_kg_m2", "bmi_w2_kg_m2", "age", "sex", "dominant_hand",
                                "chronic_conditions"]
    for key in GRIP_KEYS:
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == "kg" and spec["required"] is True and spec["unit_required"] is True
        assert spec["accept"]["lb"] == 0.45359237
    assert MANIFEST["population"]["age_years"][0] == COHORT["min_age"]
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "draft"
    assert [o["key"] for o in MANIFEST["outputs"]] == [
        "grip_ratio_w1", "grip_ratio_w2", "hgsa_pattern", "hgsa_pattern_hr", "max_grip_w1_kg", "max_grip_w2_kg",
        "lhgs_pattern", "lhgs_pattern_hr", "joint_score_w2", "joint_score_hr", "delta_aai", "loss_rgs"]
