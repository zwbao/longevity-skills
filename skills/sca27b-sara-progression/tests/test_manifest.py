"""SCA27B SARA readout against Traschütz et al., eBioMedicine 2026 (doi:10.1016/j.ebiom.2026.106437).

Paper examples reproduced (expected values are the numbers printed in the main text):
- +0.48 SARA points/year per 100 short-allele repeats [0.19-0.77], computed from the
  Table S4 interaction 0.004802 [0.001941-0.007663] per repeat.
- 0.54 SARA points/year [0.37-0.71], Table S4 time term 0.5412 [0.3678-0.7145].
- Item accelerations 78%, 47%, 147%, 174% per 100 repeats, Table S5 ratios.
- Gait and stance = 35% of the SARA total range (Methods item ranges).
- Age-decade SCA27B medians and healthy-control 90th percentiles (Results text).
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
from presets import (AMBULATORY_GAIT_MAX, CONTROL_P90, PROGRESSION_AMBULATORY, PROGRESSION_OVERALL, S4_TIME,
                     S4_TIME_X_SHORT, SARA_ITEMS, SARA_MAX, SCA27B_DECADE_MEDIAN, SHORT_ALLELE_GE250,
                     SHORT_ALLELE_GT180, SHORT_ALLELE_MEDIAN)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))

ITEMS_MILD = [("gait", "2"), ("stance", "2"), ("sitting", "0"), ("speech", "1"), ("finger chase", "0.5"),
              ("nose-finger", "0.5"), ("diadochokinesia", "0"), ("heel-shin", "1")]  # total 7


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _rows(items, extra=()):
    return [(name, value, "") for name, value in items] + list(extra)


def _run(tmp_path: Path, rows, age=None, name="out"):
    m = _csv(tmp_path / f"{name}.csv", rows)
    out = tmp_path / name
    args = ["--measurements", str(m), "--out", str(out)]
    if age is not None:
        args += ["--age", age]
    code = pr.main(args)
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


def test_paper_short_allele_per_100_repeats():
    # Results: "+0.48 SARA points/year per 100 repeats, [95% CI: 0.19–0.77]".
    est, low, high = pr.short_allele_contrast(SHORT_ALLELE_MEDIAN + 100)
    assert round(est, 2) == 0.48
    assert round(low, 2) == 0.19
    assert round(high, 2) == 0.77


def test_paper_overall_progression_from_table_s4():
    # Results: "0.54 SARA points/year [95% CI: 0.37–0.71] in the overall cohort".
    assert tuple(round(x, 2) for x in S4_TIME) == (0.54, 0.37, 0.71)
    assert PROGRESSION_OVERALL == (0.54, 0.37, 0.71)


def test_paper_item_relative_acceleration():
    # Results: gait and stance "by 78% and 47% per 100 repeats", sitting or speech "by 147% and 174%".
    got = {key: round(pr.item_relative_acceleration_pct(key)) for key in
           ("sara_gait_score", "sara_stance_score", "sara_sitting_score", "sara_speech_score")}
    assert got == {"sara_gait_score": 78, "sara_stance_score": 47, "sara_sitting_score": 147, "sara_speech_score": 174}


def test_paper_gait_stance_share():
    # Discussion: gait and stance "make up only 35% of the SARA total score".
    assert pr.gait_stance_share_pct() == 35
    assert sum(top for _, _, top in SARA_ITEMS) == SARA_MAX == 40


def test_paper_age_decade_lookup(tmp_path: Path):
    # Results: "50–60 years: 6 [3.5–12] vs. 1 point; 60–70 years: 6 [4–10] vs. 2.5 points;
    # 70–80 years: 8.5 [5–12.5] vs. 5 points".
    printed = {55: ((6, 3.5, 12), 1), 65: ((6, 4, 10), 2.5), 75: ((8.5, 5, 12.5), 5)}
    for age, (median, p90) in printed.items():
        code, result, report, _ = _run(tmp_path, _rows(ITEMS_MILD), age=str(age), name=f"age{age}")
        assert code == 0
        assert result["control_p90_for_age_decade"]["value"] == p90
        assert result["margin_over_control_p90"]["value"] == pytest.approx(7 - p90)
        assert SCA27B_DECADE_MEDIAN[age // 10 * 10] == median
        assert f"中位数 {median[0]:g}（四分位 {median[1]:g}–{median[2]:g}）" in report
    assert CONTROL_P90 == {50: 1, 60: 2.5, 70: 5}


def test_full_report_with_short_allele(tmp_path: Path):
    rows = _rows(ITEMS_MILD, [("FGF14 long allele", "300", ""), ("FGF14 short allele", "216", "")])
    code, result, report, _ = _run(tmp_path, rows, age="66")
    assert code == 0
    assert result["sara_total_score"]["value"] == 7
    assert result["ambulatory_subgroup"]["value"] == "是"
    assert result["cohort_progression_points_per_year"]["value"] == PROGRESSION_AMBULATORY[0]
    # 216 - 16 = 200 repeats above the median -> 2 x 0.4802 per 100.
    assert result["short_allele_progression_difference"]["value"] == pytest.approx(0.960, abs=1e-3)
    assert "181–249" not in report and "中间范围" in result["short_allele_group"]["value"]
    assert "## 论文卡片" in report and "边界:" in report and "10.1016/j.ebiom.2026.106437" in report
    assert f"{SHORT_ALLELE_GT180[0]:.1f}" in report and f"{SHORT_ALLELE_GE250[0]:.1f}" in report
    for word in ("剂量", "停药", "开始服用"):
        assert word not in report


def test_non_ambulatory_uses_overall_rate(tmp_path: Path):
    items = [("步态", "5"), ("站姿", "4"), ("坐姿", "1"), ("言语", "1"), ("手指追踪", "1"),
             ("指鼻试验", "1"), ("快速轮替动作", "1"), ("跟膝胫试验", "2")]
    code, result, report, _ = _run(tmp_path, _rows(items), age="82")
    assert code == 0 and AMBULATORY_GAIT_MAX == 3
    assert result["sara_total_score"]["value"] == 16 and result["ambulatory_subgroup"]["value"] == "否"
    assert result["cohort_progression_points_per_year"]["value"] == PROGRESSION_OVERALL[0]
    assert result["control_p90_for_age_decade"]["value"] is None
    assert "没有可对照的数" in report


def test_long_allele_below_threshold_and_swapped_alleles_are_noted(tmp_path: Path):
    rows = _rows(ITEMS_MILD, [("较长等位", "220", ""), ("较短等位", "230", "")])
    code, _, report, _ = _run(tmp_path, rows)
    assert code == 0
    assert "低于论文入组标准" in report and "填反" in report


def test_item_above_maximum_is_refused(tmp_path: Path):
    items = [("gait", "9")] + ITEMS_MILD[1:]
    code, result, _, out = _run(tmp_path, _rows(items))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "sara_gait_score" and problems[0]["kind"] == "range"
    assert all(item["value"] is None for item in result.values())


def test_wrong_unit_and_missing_item_are_refused(tmp_path: Path):
    rows = _rows(ITEMS_MILD[:-1], [("heel-shin", "1", "mg/dl")])
    code, result, _, _ = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert result["sara_total_score"]["value"] is None
    code2, _, _, out2 = _run(tmp_path, _rows(ITEMS_MILD[:-1]), name="missing")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out2 / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("sara_heel_shin_score", "missing") in {(p["key"], p["kind"]) for p in problems}


def test_age_out_of_range_is_refused(tmp_path: Path):
    code, _, _, _ = _run(tmp_path, _rows(ITEMS_MILD), age="5")
    assert code == skillkit.EXIT_INPUT_PROBLEM


def test_manifest_matches_presets():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == [key for key, _, _ in SARA_ITEMS] + ["gaa_long_allele_repeats", "gaa_short_allele_repeats", "age"]
    for key, _, top in SARA_ITEMS:
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == "score" and spec["range"] == [0, top] and spec["required"] is True
    assert S4_TIME_X_SHORT == (0.004802, 0.001941, 0.007663)
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "reproduced"
    assert [o["key"] for o in MANIFEST["outputs"]] == [
        "sara_total_score", "ambulatory_subgroup", "cohort_progression_points_per_year",
        "control_p90_for_age_decade", "margin_over_control_p90", "short_allele_group",
        "short_allele_progression_difference"]
