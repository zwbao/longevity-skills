"""skill.json matches presets; the paper's printed numbers come out for the paper's categories;
input mistakes stop the computation with exit 3.

Expected values are quoted from Temple et al., JAMA Netw Open 2026;9(9):e2635834:
Results paragraph 1 / Table 2 (depression 21.0% with 0 ACEs, 46.5% with 4 to 5, 56.9% with 6 or more)
and Table 3 (depression OR 2.13, 3.09, 4.53 for 1 to 3, 4 to 5, 6 or more ACEs versus 0).
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report  # noqa: E402
import skillkit  # noqa: E402
from presets import CATEGORY_N, DOMAINS, ITEMS, MISSING_ACE, COHORT_N, SCALES, TABLE2, TABLE3  # noqa: E402

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))

# Every item at the answer that names no adversity (eTable 1).
NONE = {
    "ea_insult": 0, "ea_afraid": 0, "pa_push": 0, "pa_marks": 0, "sa_touch": 0, "sa_intercourse": 0,
    "en_important": 4, "pn_meals": 0, "dv_beaten": 0, "dv_weapon": 0, "hh_alcohol": 0, "hh_drugs": 0,
    "hh_depressed": 0, "hh_suicidal": 0, "hh_incarcerated": 0, "wv_seen": 0, "disc_race": 0,
    "nb_safe": 3, "nb_trust": 3, "bullied": 0, "foster_care": 0,
}
# One item per domain at its printed threshold, in eTable 1 domain order.
ONE_PER_DOMAIN = [
    ("ea_insult", 2), ("pa_marks", 1), ("sa_touch", 1), ("en_important", 1), ("pn_meals", 3),
    ("dv_weapon", 1), ("hh_drugs", 1), ("hh_suicidal", 1), ("hh_incarcerated", 1), ("wv_seen", 2),
    ("disc_race", 2), ("nb_safe", 1), ("bullied", 2), ("foster_care", 1),
]


def answers(n_domains: int) -> dict:
    codes = dict(NONE)
    codes.update(dict(ONE_PER_DOMAIN[:n_domains]))
    return codes


def _csv(path: Path, codes: dict, unit: str = "score") -> Path:
    lines = ["item,value,unit"] + [f"{key},{value},{unit}" for key, value in codes.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, codes: dict, *extra):
    tmp_path.mkdir(parents=True, exist_ok=True)
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", codes)), "--out", str(out), *extra])
    text = (out / "report.md").read_text(encoding="utf-8")
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    return code, text, result


def test_paper_example_depression_by_ace_category(tmp_path: Path):
    """Results/Table 2: depression 70 [21.0%] with 0 ACEs, 165 [46.5%] with 4 to 5, 141 [56.9%] with 6 or more."""
    code, text, result = _run(tmp_path / "a", answers(6))
    assert code == 0 and result["ace_category"]["value"] == "6+"
    assert "| 抑郁（CES-D-10 ≥10） | 21.0%（70 人） | 56.9%（141 人） |" in text
    code, text, result = _run(tmp_path / "b", answers(4))
    assert code == 0 and result["ace_category"]["value"] == "4-5"
    assert "| 抑郁（CES-D-10 ≥10） | 21.0%（70 人） | 46.5%（165 人） |" in text
    assert (TABLE2["depression"]["0"], TABLE2["depression"]["4-5"], TABLE2["depression"]["6+"]) == ((70, 21.0), (165, 46.5), (141, 56.9))


def test_paper_example_table3_depression_odds_ratios(tmp_path: Path):
    """Table 3 depression row: 2.13 (1.56-2.91), 3.09 (2.16-4.41), 4.53 (3.06-6.70)."""
    for n, cat, printed in ((2, "1-3", "2.13 (1.56-2.91)"), (5, "4-5", "3.09 (2.16-4.41)"), (14, "6+", "4.53 (3.06-6.70)")):
        code, text, result = _run(tmp_path / cat, answers(n))
        assert code == 0 and result["ace_category"]["value"] == cat
        assert f"{printed}，P <.001 |" in text
    assert [TABLE3["depression"][c][0] for c in ("1-3", "4-5", "6+")] == ["2.13 (1.56-2.91)", "3.09 (2.16-4.41)", "4.53 (3.06-6.70)"]


@pytest.mark.parametrize("n, cat", [(0, "0"), (1, "1-3"), (3, "1-3"), (4, "4-5"), (5, "4-5"), (6, "6+"), (14, "6+")])
def test_category_boundaries_from_methods(tmp_path: Path, n, cat):
    code, text, result = _run(tmp_path, answers(n))
    assert code == 0
    assert result["ace_count"]["value"] == n
    assert result["ace_category"]["value"] == cat


def test_thresholds_one_step_below_do_not_count(tmp_path: Path):
    below = dict(NONE)
    for key, code in ONE_PER_DOMAIN:
        op = next(item[4] for item in ITEMS if item[0] == key)
        if key in ("sa_touch", "hh_drugs", "hh_suicidal", "hh_incarcerated", "foster_care"):
            continue  # yes/no items have no step below
        below[key] = code - 1 if op == ">=" else code + 1
    _code, _text, result = _run(tmp_path, below)
    assert result["ace_count"]["value"] == 0


def test_text_answers_and_chinese_names(tmp_path: Path):
    path = tmp_path / "m.txt"
    rows = {"大人辱骂、贬低你": "more than once", "大人打得留下伤痕或受伤": "一次", "年长者以性的方式触摸你": "是",
            "有人让你觉得自己重要": "很少符合", "在社区里觉得安全": "some of the time", "被同伴或同学欺负": "大部分时间"}
    rest = {key: value for key, value in NONE.items()
            if key not in ("ea_insult", "pa_marks", "sa_touch", "en_important", "nb_safe", "bullied")}
    path.write_text("\n".join([f"{k},{v}" for k, v in rows.items()] + [f"{k},{v}" for k, v in rest.items()]) + "\n", encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(path), "--out", str(out)]) == 0
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["ace_count"]["value"] == 6
    assert result["ace_category"]["value"] == "6+"


def test_any_item_reading_and_stricter_reading_are_both_shown(tmp_path: Path):
    codes = answers(0)
    codes.update({"ea_insult": 2, "pa_push": 2, "sa_touch": 1, "hh_alcohol": 1})  # one of two items each
    code, text, result = _run(tmp_path, codes)
    assert code == 0 and result["ace_count"]["value"] == 4 and result["ace_category"]["value"] == "4-5"
    assert "若改成两题都要满足，条数是 0" in text and "0 条" in text


def test_missing_items_that_do_not_change_the_category(tmp_path: Path):
    codes = answers(14)
    del codes["ea_afraid"], codes["nb_trust"]  # domains already met by the other item
    del codes["foster_care"]  # foster care unknown: 13 or 14, both 6+
    code, text, result = _run(tmp_path, codes)
    assert code == 0
    assert result["ace_category"]["value"] == "6+"
    assert result["ace_count"]["value"] is None
    assert "13 到 14" in text and "进过寄养家庭" in text


def test_missing_items_that_cross_a_category_stop_with_exit_3(tmp_path: Path):
    codes = answers(3)
    del codes["foster_care"], codes["bullied"]
    code, text, result = _run(tmp_path, codes)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert (tmp_path / "out" / "problems.json").exists()
    assert "3 到 5" in text and "进过寄养家庭" in text
    assert result == {k: {**v, "value": None} for k, v in result.items()}
    assert "## 论文卡片" in text and text.rstrip().splitlines()[-1].startswith("边界: ")


@pytest.mark.parametrize(
    "change, unit, reason",
    [
        ({"bullied": 5}, "score", "不在合理范围"),
        ({"pn_meals": 2.5}, "score", "只收整数"),
        ({"ea_insult": "maybe"}, "score", "不是一个可以计算的数"),
        ({}, "mg/dl", "不能换算"),
    ],
    ids=["out-of-range", "fraction", "text", "wrong-unit"],
)
def test_wrong_input_stops_the_computation(tmp_path: Path, change, unit, reason):
    codes = answers(6)
    codes.update(change)
    code, text, result = _run(tmp_path, codes) if unit == "score" else (None, None, None)
    if unit != "score":
        out = tmp_path / "out"
        code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", codes, unit)), "--out", str(out)])
        text = (out / "report.md").read_text(encoding="utf-8")
        result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "输入没有通过检查" in text and reason in text
    assert "56.9%" not in text and "符合 6 类" not in text
    assert result["ace_count"]["value"] is None and result["ace_category"]["value"] is None


def test_age_out_of_range_stops(tmp_path: Path):
    code, text, _result = _run(tmp_path, answers(2), "--age", "190")
    assert code == skillkit.EXIT_INPUT_PROBLEM and "实足年龄" in text


def test_manifest_matches_presets():
    declared = [item for item in MANIFEST["inputs"] if item["from"] == "measurements"]
    assert [item["key"] for item in declared] == [item[0] for item in ITEMS]
    for spec, item in zip(declared, ITEMS):
        assert spec["unit"] == "score"
        assert spec["range"] == [0, max(SCALES[item[3]]["codes"])]
        assert spec["group"] == item[1]
        assert spec["label_zh"] == item[2]
    assert len({item[1] for item in ITEMS}) == len(DOMAINS) == 14
    assert len(ITEMS) == 21  # "the 21-item Philadelphia ACEs survey"
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"]) == ("profile", "--age", "a")
    assert MANIFEST["inputs_status"] == "verified" and MANIFEST["entry"]["result_json"] is True
    assert [o["key"] for o in MANIFEST["outputs"]] == ["ace_count", "ace_category"]


def test_table2_column_sizes_add_up():
    """Table 2 columns 337 + 878 + 355 + 253 = 1823 = 1850 minus the 27 missing the ACE measure."""
    assert sum(CATEGORY_N.values()) == COHORT_N - MISSING_ACE == 1823
    assert len(TABLE2) == len(TABLE3) == 20
