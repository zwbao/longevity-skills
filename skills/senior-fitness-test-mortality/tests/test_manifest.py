"""Senior Fitness Test quintiles and hazard ratios against Wu et al., JAMA Netw Open 2026.

Expected quintile ranges are the "Range" columns of Supplement 1 eTable 3 (Male is the
first Range column, Female the second). Expected hazard ratios are printed in the
article's Figure 3 (2-minute step, chair stand, one-leg stance, 8-foot up-and-go; both
sexes), Supplement 1 eFigure 4 (arm curl, back scratch, chair sit-and-reach; both
sexes), eFigure 5 (men) and eFigure 6 (women). The paper prints no individual worked
example, so these tests check the grouping and the table lookup (validation stays
draft). All personal inputs are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import AHR_ALL, AHR_SEX, COHORT, DEATHS_SEX, MEDIAN_IQR, QUINTILE_N, QUINTILE_RANGES, TESTS

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, sex="male", age=None, name="out", targets=None):
    m = _csv(tmp_path / f"{name}.csv", rows)
    out = tmp_path / name
    args = ["--measurements", str(m), "--out", str(out)]
    if sex is not None:
        args += ["--sex", sex]
    if age is not None:
        args += ["--age", age]
    if targets is not None:
        args += ["--targets", str(_csv(tmp_path / f"{name}_targets.csv", targets))]
    code = pr.main(args)
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


def test_etable3_ranges_as_printed():
    # eTable 3: "2-minute step test (count) Q1 2,677 (19.9) 0–69 976 (19.4) 0–65 1,701 (20.3)"
    assert QUINTILE_RANGES["male"]["step_2min"][0] == (0, 69) and QUINTILE_RANGES["female"]["step_2min"][0] == (0, 65)
    assert QUINTILE_RANGES["male"]["step_2min"][4] == (109, 190) and QUINTILE_RANGES["female"]["step_2min"][4] == (107, 190)
    # "30-second chair stand (count) Q5 (best) 2,864 (21.3) 20–33 1,103 (21.9) 19–33 1,761 (21.0)"
    assert QUINTILE_RANGES["male"]["chair_stand"][4] == (20, 33) and QUINTILE_RANGES["female"]["chair_stand"][4] == (19, 33)
    # "Back scratch (cm) Q3 2,748 (20.5) -15.0 – -7.1 1,011 (20.1) -5.0–1.0 1,737 (20.7)"
    assert QUINTILE_RANGES["male"]["back_scratch"][2] == (-15.0, -7.1) and QUINTILE_RANGES["female"]["back_scratch"][2] == (-5.0, 1.0)
    # "One-leg stance (second) Q2 2,672 (19.9) 4.12–9.50 999 (19.9) 3.61–7.51 1,673 (19.9)"
    assert QUINTILE_RANGES["male"]["one_leg"][1] == (4.12, 9.50) and QUINTILE_RANGES["female"]["one_leg"][1] == (3.61, 7.51)
    # "8-ft up-and-go (second) Q5 (best) 2,701 (20.1) 3.70–5.29 1,003 (19.9) 3.70–5.70 1,698 (20.2)"
    assert QUINTILE_RANGES["male"]["up_and_go"][4] == (3.70, 5.29) and QUINTILE_RANGES["female"]["up_and_go"][4] == (3.70, 5.70)
    assert sum(QUINTILE_N["male"]["step_2min"]) == COHORT["n_male"] == 5029
    assert sum(QUINTILE_N["female"]["chair_stand"]) == COHORT["n_female"] == 8394


def test_ranges_are_ordered_and_medians_fall_in_q2_to_q4():
    for sex in ("male", "female"):
        for test, _key, _label, _unit, direction in TESTS:
            ranges = QUINTILE_RANGES[sex][test]
            for low, high in ranges:
                assert low <= high
            for a, b in zip(ranges, ranges[1:]):
                if direction == "higher":
                    assert a[1] < b[0]
                else:
                    assert b[1] < a[0]
            median = MEDIAN_IQR[sex][test][0]
            assert any(pr.quintile(test, sex, median)["q"] == q for q in (2, 3, 4)) or test == "one_leg"


def test_deaths_over_etable3_n_reproduce_printed_percent():
    """eFigures 5-6 print deaths and % per quintile; % = deaths / eTable 3 n for that sex.

    Tolerance 0.06 points: three cells were rounded twice in the paper (men arm curl Q3
    164/1055 = 15.545 -> 15.6; men chair stand Q2 173/818 = 21.149 -> 21.2; women step Q2
    182/1709 = 10.650 -> 10.7); the other 67 match to one decimal.
    """
    for sex in ("male", "female"):
        for test, *_ in TESTS:
            for (deaths, pct), n in zip(DEATHS_SEX[sex][test], QUINTILE_N[sex][test]):
                assert 100 * deaths / n == pytest.approx(pct, abs=0.06), (sex, test, deaths, n, pct)
        assert sum(d for d, _ in DEATHS_SEX[sex]["step_2min"]) == (848 if sex == "male" else 783)


def test_hazard_ratios_as_printed():
    # Abstract: 8-foot up-and-go (AHR, 0.41 [95% CI, 0.33-0.51]), 1-leg stance (AHR, 0.50 [95% CI, 0.42-0.59]),
    # 30-second chair stand (AHR, 0.55 [95% CI, 0.46-0.65]), 2-minute step test (AHR, 0.58 [95% CI, 0.49-0.68])
    assert AHR_ALL["up_and_go"][4] == (0.41, 0.33, 0.51)
    assert AHR_ALL["one_leg"][4] == (0.50, 0.42, 0.59)
    assert AHR_ALL["chair_stand"][4] == (0.55, 0.46, 0.65)
    assert AHR_ALL["step_2min"][4] == (0.58, 0.49, 0.68)
    # Results: 30-second arm curl AHR, 0.63 [95% CI, 0.53-0.75]; chair sit-and-reach AHR, 0.79 [95% CI, 0.67-0.93]
    assert AHR_ALL["arm_curl"][4] == (0.63, 0.53, 0.75) and AHR_ALL["sit_reach"][4] == (0.79, 0.67, 0.93)
    # Figure 3: 8-Foot up-and-go Q4 0.46 (0.38-0.55); 1-Leg stance Q4 0.53 (0.43-0.66)
    assert AHR_ALL["up_and_go"][3] == (0.46, 0.38, 0.55) and AHR_ALL["one_leg"][3] == (0.53, 0.43, 0.66)
    # eFigure 4: back scratch Q2 0.87 (0.76–1.00)
    assert AHR_ALL["back_scratch"][1] == (0.87, 0.76, 1.00)
    # eFigure 5 (men): 30-s chair stand Q5 0.59 (0.47–0.75); eFigure 6 (women): 0.50 (0.39–0.64)
    assert AHR_SEX["male"]["chair_stand"][4] == (0.59, 0.47, 0.75)
    assert AHR_SEX["female"]["chair_stand"][4] == (0.50, 0.39, 0.64)
    assert AHR_SEX["male"]["up_and_go"][4] == (0.42, 0.31, 0.55) and AHR_SEX["female"]["up_and_go"][4] == (0.41, 0.31, 0.54)
    for table in (AHR_ALL, AHR_SEX["male"], AHR_SEX["female"]):
        for rows in table.values():
            assert rows[0] == (1.0, None, None) and len(rows) == 5
            for est, low, high in rows[1:]:
                assert low <= est <= high


@pytest.mark.parametrize("sex,test,value,q,flag", [
    ("male", "chair_stand", 11, 1, None), ("male", "chair_stand", 12, 2, None), ("male", "chair_stand", 20, 5, None),
    ("female", "chair_stand", 10, 1, None), ("female", "chair_stand", 11, 2, None), ("female", "chair_stand", 19, 5, None),
    ("male", "step_2min", 69, 1, None), ("male", "step_2min", 70, 2, None), ("female", "step_2min", 66, 2, None),
    ("male", "one_leg", 4.11, 1, "gap"), ("male", "one_leg", 29.9, 4, "gap"), ("male", "one_leg", 30, 5, None),
    ("male", "up_and_go", 5.29, 5, None), ("male", "up_and_go", 5.30, 4, None), ("male", "up_and_go", 8.81, 1, None),
    ("male", "up_and_go", 3.5, 5, "below"), ("female", "up_and_go", 25, 1, "above"), ("female", "up_and_go", 9.005, 1, "gap"),
    ("male", "back_scratch", 2.1, 4, "gap"), ("male", "back_scratch", -55, 1, "below"),
    ("female", "sit_reach", -0.05, 1, "gap"), ("female", "sit_reach", 0.0, 2, None), ("male", "step_2min", 200, 5, "above"),
])
def test_quintile_boundaries(sex, test, value, q, flag):
    place = pr.quintile(test, sex, value)
    assert place == {"q": q, "flag": flag}


def test_paper_lookup_men_full_battery(tmp_path: Path):
    rows = [("2分钟原地踏步", "100", "次"), ("30秒手臂弯举", "15", ""), ("30秒椅子坐立", "20", "次"),
            ("抓背", "-10", "cm"), ("椅子坐姿体前弯", "5", "cm"), ("单脚站立", "8", "秒"), ("8英尺起身绕行", "5.0", "s")]
    code, result, report, out = _run(tmp_path, rows, sex="男", age="72")
    assert code == 0
    got = {test: result[f"{test}_quintile"]["value"] for test, *_ in TESTS}
    assert got == {"step_2min": 4, "arm_curl": 2, "chair_stand": 5, "back_scratch": 3, "sit_reach": 4, "one_leg": 2, "up_and_go": 5}
    # eFigure 5 men: chair stand Q5 0.59; 8-ft up-and-go Q5 0.42; one-leg stance Q2 0.77
    assert result["chair_stand_ahr_sex"]["value"] == 0.59
    assert result["up_and_go_ahr_sex"]["value"] == 0.42
    assert result["one_leg_ahr_sex"]["value"] == 0.77
    # Figure 3 both sexes: 8-ft up-and-go Q5 0.41; 2-min step Q4 0.59
    assert result["up_and_go_ahr"]["value"] == 0.41
    assert result["step_2min_ahr"]["value"] == 0.59
    assert result["tests_done"]["value"] == 7 and result["tests_in_q1"]["value"] == 0
    assert "0.59（95% 置信区间 0.47–0.75）" in report and "0.41（95% 置信区间 0.33–0.51）" in report
    assert "## 论文卡片" in report and "边界:" in report and "10.1001/jamanetworkopen.2026.28227" in report
    assert "好的信号" in report and "综合" in report
    levers = json.loads((out / "levers.json").read_text(encoding="utf-8"))
    assert levers["schema"] == "longevity-levers/1" and levers["levers"] == []


def test_women_partial_with_q1_and_targets(tmp_path: Path):
    rows = [("30-second chair stand", "9", ""), ("8-foot up-and-go", "10.2", "s")]
    targets = [("30-second chair stand", "16", ""), ("8-foot up-and-go", "7.4", "s")]
    code, result, report, out = _run(tmp_path, rows, sex="female", age="78", targets=targets)
    assert code == 0
    assert result["chair_stand_quintile"]["value"] == 1 and result["chair_stand_ahr_sex"]["value"] == 1.0
    assert result["up_and_go_quintile"]["value"] == 1
    assert result["step_2min_quintile"]["value"] is None and result["tests_in_q1"]["value"] == 2
    assert "最低的五分之一" in report and "没有交的项目" in report
    assert "达到 11" in report and "缩短到 9" in report
    levers = json.loads((out / "levers.json").read_text(encoding="utf-8"))
    by_key = {item["key"]: item for item in levers["levers"]}
    # eFigure 6 women: chair stand Q4 0.56 (0.45–0.70); 8-ft up-and-go Q3 0.53 (0.42–0.65)
    assert by_key["chair_stand_30s_count"]["quintile_to"] == 4 and by_key["chair_stand_30s_count"]["ahr_sex_to"] == 0.56
    assert by_key["up_and_go_8ft_s"]["quintile_to"] == 3 and by_key["up_and_go_8ft_s"]["ahr_sex_to"] == 0.53


def test_one_leg_over_30_is_capped(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("one-leg stance", "45", "s")], sex="female")
    assert code == 0 and result["one_leg_quintile"]["value"] == 5 and "按 30 秒归档" in report


def test_inch_conversion_and_age_note(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("back scratch", "-2", "in")], sex="female", age="60")
    # -2 in = -5.08 cm: women Q2 is -14.0 to -5.1, Q3 -5.0 to 1.0 -> gap, poorer quintile Q2
    assert code == 0 and result["back_scratch_quintile"]["value"] == 2
    assert "不在论文人群" in report


def test_wrong_unit_is_caught(tmp_path: Path):
    # back scratch without a unit must state cm or in (inches land inside the cm range)
    code, result, _, out = _run(tmp_path, [("抓背", "-4", "")], sex="male")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "back_scratch_cm" and problems[0]["kind"] == "unit_missing"
    assert all(item["value"] is None for item in result.values())


def test_out_of_range_is_refused(tmp_path: Path):
    # 8-ft up-and-go typed in minutes-as-seconds confusion: 0.1 s is below 2 s
    code, result, report, out = _run(tmp_path, [("8-foot up-and-go", "0.1", "s")], sex="male")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "up_and_go_8ft_s" and problems[0]["kind"] == "range"
    assert result["up_and_go_quintile"]["value"] is None and "Q5" not in report


def test_missing_sex_or_no_tests_is_refused(tmp_path: Path):
    code, _, _, out = _run(tmp_path, [("30-second chair stand", "14", "")], sex=None, name="nosex")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"][0]["key"] == "sex"
    code2, _, _, _ = _run(tmp_path, [("30-second chair stand", "14", "")], sex="x", name="badsex")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM
    code3, _, report3, _ = _run(tmp_path, [("grip", "30", "kg")], sex="male", name="none")
    assert code3 == skillkit.EXIT_INPUT_PROBLEM and "至少交一项" in report3


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == [key for _t, key, *_ in TESTS] + ["sex", "age"]
    units = {"step_2min_count": "1", "arm_curl_30s_count": "1", "chair_stand_30s_count": "1", "back_scratch_cm": "cm",
             "chair_sit_reach_cm": "cm", "one_leg_stance_s": "s", "up_and_go_8ft_s": "s"}
    for key, unit in units.items():
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == unit
    for test, key, *_ in TESTS:
        spec = skillkit.spec_by_key(MANIFEST, key)
        low, high = spec["range"]
        for sex in ("male", "female"):
            for r_low, r_high in QUINTILE_RANGES[sex][test]:
                assert low <= r_low and r_high <= high
    assert MANIFEST["population"]["age_years"] == list(COHORT["age_range"])
    assert MANIFEST["inputs_status"] == "verified" and MANIFEST["validation"]["status"] == "draft"
    expected = []
    for test, *_ in TESTS:
        expected += [f"{test}_quintile", f"{test}_ahr_sex", f"{test}_ahr"]
    assert [o["key"] for o in MANIFEST["outputs"]] == expected + ["tests_done", "tests_in_q1"]
    assert MANIFEST["entry"]["targets_flag"] == "--targets" and MANIFEST["entry"]["levers_json"] is True
