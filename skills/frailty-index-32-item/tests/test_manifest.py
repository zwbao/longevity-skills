"""32-item frailty index against Zhang et al., GeroScience 2026 (CHARLS, CKM stages 0-3).

Expected constants are as printed: Supplementary Table 2 (ESM 1) item coding and notes
("The frailty index is calculated as the total sum of scores divided by 32"; robust
FI <=0.12, pre-frail 0.12 < FI <=0.25, frail FI >0.25; item 31 "CESD-10 >10 = 1, <=10 = 0")
and the Model 2 hazard ratios in Results / Table 3. The paper prints no individual worked
example, so these tests check the coding rules, the formula and the cut points only
(validation stays draft). All personal inputs are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import (ALL_KEYS, BINARY_ITEMS, CESD10_CUT, CESD_ITEM, COGNITION_ITEM, COHORT, HR_MODEL2, N_ITEMS,
                     PREFRAIL_MAX, ROBUST_MAX)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
BINARY_KEYS = [item[1] for item in BINARY_ITEMS]


def _rows(yes=(), cesd="5", cognition=None, extra=()):
    rows = [(key, "1" if key in yes else "0", "") for key in BINARY_KEYS]
    rows.append(("cesd10_score", cesd, ""))
    if cognition is not None:
        rows.append(("cognition_deficit_0_1", cognition, ""))
    return rows + list(extra)


def _run(tmp_path: Path, rows, age=None, name="out"):
    m = tmp_path / f"{name}.csv"
    m.write_text("\n".join(["item,value,unit"] + [",".join(r) for r in rows]) + "\n", encoding="utf-8")
    out = tmp_path / name
    args = ["--measurements", str(m), "--out", str(out)]
    if age is not None:
        args += ["--age", age]
    code = pr.main(args)
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


def test_constants_are_as_printed():
    # Supplementary Table 2 notes and Methods.
    assert N_ITEMS == 32 and ROBUST_MAX == 0.12 and PREFRAIL_MAX == 0.25 and CESD10_CUT == 10
    assert len(BINARY_ITEMS) == 30 and [i[0] for i in BINARY_ITEMS] == list(range(1, 31))
    assert CESD_ITEM[0] == 31 and COGNITION_ITEM[0] == 32 and len(ALL_KEYS) == 32
    # Results, Table 3, Model 2 (reference robust).
    assert HR_MODEL2["prefrail"]["total_cvd"] == (1.61, 1.33, 1.95)
    assert HR_MODEL2["frail"]["total_cvd"] == (1.63, 1.23, 2.17)
    assert HR_MODEL2["prefrail"]["heart_disease"] == (1.61, 1.29, 2.02)
    assert HR_MODEL2["frail"]["heart_disease"] == (1.49, 1.06, 2.09)
    assert HR_MODEL2["prefrail"]["stroke"] == (1.75, 1.24, 2.48)
    assert HR_MODEL2["frail"]["stroke"] == (2.09, 1.28, 3.42)
    assert (COHORT["n"], COHORT["cvd_events"], COHORT["min_age"]) == (4219, 541, 45)


@pytest.mark.parametrize("fi,status", [
    (0.0, "robust"), (0.12, "robust"), (0.1201, "prefrail"), (4 / 32, "prefrail"),
    (0.25, "prefrail"), (8 / 32, "prefrail"), (0.2501, "frail"), (9 / 32, "frail"), (1.0, "frail"),
])
def test_cut_points(fi, status):
    assert pr.status_of(fi) == status


@pytest.mark.parametrize("score,deficit", [(0, 0), (10, 0), (10.5, 1), (11, 1), (30, 1)])
def test_cesd_coding(score, deficit):
    assert pr.cesd_deficit(score) == deficit


def test_full_32_items(tmp_path: Path):
    yes = ("hypertension_dx_yn", "arthritis_dx_yn", "difficulty_stairs_yn")
    code, result, report, _ = _run(tmp_path, _rows(yes=yes, cesd="12", cognition="0.5"), age="62")
    assert code == 0
    # (3 binary + 1 CES-D + 0.5 cognition) / 32 = 0.140625
    assert result["frailty_index"]["value"] == pytest.approx(4.5 / 32, abs=1e-4)
    assert result["frailty_status"]["value"] == "衰弱前期"
    assert result["deficit_sum_31_items"]["value"] == 4
    assert "1.61（95% 置信区间 1.33–1.95）" in report
    assert "## 论文卡片" in report and "边界:" in report and "10.1007/s11357-026-02559-3" in report


def test_missing_cognition_gives_interval(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, _rows(yes=BINARY_KEYS[:4]))
    assert code == 0
    assert result["frailty_index"]["value"] is None
    assert result["frailty_index_low"]["value"] == pytest.approx(4 / 32, abs=1e-4)
    assert result["frailty_index_high"]["value"] == pytest.approx(5 / 32, abs=1e-4)
    assert result["frailty_status"]["value"] == "衰弱前期"


def test_missing_cognition_across_cut_point_is_undetermined(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, _rows(yes=("vision_problem_yn", "hearing_problem_yn", "arthritis_dx_yn")))
    assert code == 0
    assert result["frailty_status"]["value"].startswith("不能确定")
    assert "风险比（表 3" not in report


def test_text_answers_and_aliases(tmp_path: Path):
    rows = [(key, "否", "") for key in BINARY_KEYS if key not in ("hypertension_dx_yn", "self_rated_health_poor_yn")]
    rows += [("高血压", "是", ""), ("自评健康", "一般", ""), ("CES-D-10", "8", ""), ("认知缺损分", "0", "")]
    code, result, _, _ = _run(tmp_path, rows)
    assert code == 0
    assert result["frailty_index"]["value"] == pytest.approx(2 / 32, abs=1e-4)
    assert result["frailty_status"]["value"] == "强健"


def test_frail_with_heart_disease_is_outside_population(tmp_path: Path):
    yes = BINARY_KEYS[:10]  # includes heart disease and stroke
    code, result, report, _ = _run(tmp_path, _rows(yes=yes, cognition="0.2"))
    assert code == 0 and result["frailty_status"]["value"] == "衰弱"
    assert "不完全符合论文人群" in report and "2.09" not in report


def test_frail_in_population_lists_hrs(tmp_path: Path):
    yes = ("hypertension_dx_yn", "diabetes_dx_yn", "arthritis_dx_yn", "vision_problem_yn", "hearing_problem_yn",
           "self_rated_health_poor_yn", "difficulty_stairs_yn", "difficulty_stoop_yn", "difficulty_lift_10jin_yn")
    code, result, report, _ = _run(tmp_path, _rows(yes=yes, cesd="14", cognition="0.3"), age="70")
    assert code == 0 and result["frailty_status"]["value"] == "衰弱"
    assert "2.09（95% 置信区间 1.28–3.42）" in report and "1.63（95% 置信区间 1.23–2.17）" in report


def test_value_not_zero_or_one_is_refused(tmp_path: Path):
    rows = [r if r[0] != "asthma_dx_yn" else ("asthma_dx_yn", "0.5", "") for r in _rows()]
    code, result, report, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "asthma_dx_yn"
    assert all(item["value"] is None for item in result.values())
    assert "衰弱指数（32 项" not in report


def test_out_of_range_and_unparsable_are_refused(tmp_path: Path):
    # CES-D-10 maximum is 30; 45 looks like a CES-D-20 total.
    code, _, _, out = _run(tmp_path, _rows(cesd="45"))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"][0]["key"] == "cesd10_score"
    rows = [r if r[0] != "stroke_dx_yn" else ("stroke_dx_yn", "不知道", "") for r in _rows()]
    code2, _, _, _ = _run(tmp_path, rows, name="bad")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM
    code3, _, _, _ = _run(tmp_path, _rows(cognition="12"), name="cog")
    assert code3 == skillkit.EXIT_INPUT_PROBLEM


def test_wrong_unit_is_refused(tmp_path: Path):
    rows = [r if r[0] != "cesd10_score" else ("cesd10_score", "8", "mg/dl") for r in _rows()]
    code, _, _, _ = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM


def test_missing_item_is_refused(tmp_path: Path):
    rows = [r for r in _rows() if r[0] != "difficulty_coin_yn" and r[0] != "difficulty_pick_coin_yn"]
    code, _, _, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("difficulty_pick_coin_yn", "missing") in {(p["key"], p["kind"]) for p in problems}


def test_under_45_is_noted(tmp_path: Path):
    code, _, report, _ = _run(tmp_path, _rows(yes=BINARY_KEYS[10:16], cognition="0"), age="40")
    assert code == 0 and "不在论文人群" in report and "1.61" not in report


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == list(ALL_KEYS) + ["age"]
    for _, key, domain, label, *_ in BINARY_ITEMS:
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == "1" and spec["range"] == [0, 1] and spec["required"] is True
        assert spec["label_zh"] == label and spec["group"] == domain
    cesd = skillkit.spec_by_key(MANIFEST, "cesd10_score")
    assert cesd["unit"] == "score" and cesd["range"] == [0, 30] and cesd["required"] is True
    cog = skillkit.spec_by_key(MANIFEST, "cognition_deficit_0_1")
    assert cog["range"] == [0, 1] and cog["required"] is False
    assert MANIFEST["population"]["age_years"][0] == COHORT["min_age"]
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "draft"
    assert [o["key"] for o in MANIFEST["outputs"]] == ["frailty_index", "frailty_index_low", "frailty_index_high",
                                                      "frailty_status", "deficit_sum_31_items"]
