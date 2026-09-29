"""skill.json matches presets, the published categories hold at every edge, and bad input stops the run.

Expected values come only from printed numbers: total 4-25 and the five
categories 4-7, 8-11, 12-17, 18-21, 22-25 (quoted from Adan & Almirall 1991 by
Belfry 2020 and Gooderick 2025), and the option scores (Hwang 2024 Table 1,
Danielsson 2019). No person-level worked example is printed.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import ALLOWED, CATEGORIES, ITEMS, KEYS, TOTAL_MAX, TOTAL_MIN, category, total

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
LOWEST = {key: min(ALLOWED[key]) for key in KEYS}
HIGHEST = {key: max(ALLOWED[key]) for key in KEYS}


def _answers_for(score: int) -> dict:
    """Allowed option scores that add up to score (synthetic): raise item 5 first, then the others."""
    out = dict(LOWEST)
    left = score - total(out)
    for key in reversed(KEYS):
        options = sorted(ALLOWED[key])
        while left > 0:
            bigger = [item for item in options if item > out[key] and item - out[key] <= left]
            if not bigger:
                break
            step = min(bigger) - out[key]
            out[key] += step
            left -= step
    assert total(out) == score, (score, out)
    return out


def _csv(path: Path, answers: dict, unit: str = "") -> Path:
    path.write_text("item,value,unit\n" + "".join(f"{k},{v},{unit}\n" for k, v in answers.items()), encoding="utf-8")
    return path


def _run(tmp_path: Path, answers: dict, *flags: str, unit: str = ""):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", answers, unit)), *flags, "--out", str(out)])
    outputs = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    return code, (out / "report.md").read_text(encoding="utf-8"), outputs, out


def test_manifest_matches_presets():
    declared = [item for item in MANIFEST["inputs"] if item["from"] == "measurements"]
    assert [item["key"] for item in declared] == list(KEYS)
    for item, (key, number, meq, topic, allowed) in zip(declared, ITEMS):
        assert item["unit"] == "score" and item["required"] is True
        assert item["range"] == [min(allowed), max(allowed)]
        assert f"第{number}题" in item["label_zh"] and topic in item["label_zh"]
        assert f"meq{meq}" in item["aliases"]
    assert [meq for _k, _n, meq, _t, _a in ITEMS] == [1, 7, 10, 18, 19]
    assert MANIFEST["inputs_status"] == "verified"
    assert set(MANIFEST["related_not_same"]) == {"wearable-circadian-aging-biomarker", "circadian-frailty-older-adults"}
    assert [(o["key"], o["unit"]) for o in MANIFEST["outputs"]] == [("rmeq_score", "score"), ("rmeq_chronotype", "")]


def test_option_scores_reproduce_the_published_range():
    assert ALLOWED["rmeq_item2"] == (1, 2, 3, 4)
    assert ALLOWED["rmeq_item5"] == (0, 2, 4, 6)
    assert total(LOWEST) == TOTAL_MIN == 4
    assert total(HIGHEST) == TOTAL_MAX == 25
    assert [(low, high) for low, high, _l, _e in CATEGORIES] == [(4, 7), (8, 11), (12, 17), (18, 21), (22, 25)]
    covered = sorted(score for low, high, _l, _e in CATEGORIES for score in range(low, high + 1))
    assert covered == list(range(4, 26))
    with pytest.raises(ValueError):
        category(26)


@pytest.mark.parametrize(
    "score, label",
    [(4, "明确夜型"), (7, "明确夜型"), (8, "中度夜型"), (11, "中度夜型"), (12, "中间型"), (17, "中间型"),
     (18, "中度晨型"), (21, "中度晨型"), (22, "明确晨型"), (25, "明确晨型")],
)
def test_every_category_edge(tmp_path: Path, score, label):
    code, text, outputs, out = _run(tmp_path, _answers_for(score), "--age", "40")
    assert code == 0
    assert outputs["rmeq_score"]["value"] == score
    assert outputs["rmeq_chronotype"]["value"] == label
    assert f"得分是 **{score}**" in text and f"「{label}」" in text
    assert not (out / "problems.json").exists()


def test_meq_numbers_and_plain_lines(tmp_path: Path):
    measures = tmp_path / "m.txt"
    measures.write_text("MEQ第1题,3\nmeq7,2\nMEQ第10题,3\nmeq18,3\nMEQ第19题,2,分\n", encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(measures), "--out", str(out)]) == 0
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["rmeq_score"]["value"] == 13 and result["rmeq_chronotype"]["value"] == "中间型"


@pytest.mark.parametrize(
    "change, flags, reason",
    [
        ({"rmeq_item5": "3"}, [], "只能记 0、2、4、6 分"),
        ({"rmeq_item5": "1"}, [], "只能记 0、2、4、6 分"),
        ({"rmeq_item2": "5"}, [], "不在合理范围"),
        ({"rmeq_item1": "0"}, [], "不在合理范围"),
        ({"rmeq_item3": "2.5"}, [], "只能记 1、2、3、4、5 分"),
        ({"rmeq_item4": None}, [], "缺少"),
        ({}, ["--age", "5"], "实足年龄"),
    ],
    ids=["item5-three", "item5-one", "item2-five", "item1-zero", "half", "missing", "age"],
)
def test_bad_input_stops_the_computation(tmp_path: Path, change, flags, reason):
    answers = _answers_for(14)
    for key, value in change.items():
        if value is None:
            answers.pop(key)
        else:
            answers[key] = value
    code, text, outputs, out = _run(tmp_path, answers, *flags)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert outputs["rmeq_score"]["value"] is None and outputs["rmeq_chronotype"]["value"] is None
    assert (out / "problems.json").exists()
    assert "输入没有通过检查" in text and reason in text
    assert "## 论文卡片" in text
    assert text.rstrip().splitlines()[-1].startswith("边界: ")


def test_wrong_unit_is_refused(tmp_path: Path):
    code, text, outputs, _out = _run(tmp_path, _answers_for(14), unit="h")
    assert code == skillkit.EXIT_INPUT_PROBLEM and outputs["rmeq_score"]["value"] is None
    assert "不能换算" in text
