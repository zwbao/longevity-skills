"""skill.json matches presets, the published scoring rules hold, and bad answers stop the run.

The only printed numbers are the scoring rules (Xu et al. 2018, quoting Hays and
DiMatteo 1987): items scored 1-4, items 3 and 6 reverse-scored, total 8-32.
No person-level worked example is printed, so the expected values below are
those rules applied to synthetic answers.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import ITEMS, KEYS, REVERSED, TOTAL_MAX, TOTAL_MIN, total

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
# Least lonely end: 1 on the six loneliness items, 4 on the two reversed items.
LEAST = {key: (4 if key in REVERSED else 1) for key in KEYS}
MOST = {key: (1 if key in REVERSED else 4) for key in KEYS}


def _csv(path: Path, answers: dict, unit: str = "") -> Path:
    rows = ["item,value,unit"] + [f"{key},{value},{unit}" for key, value in answers.items()]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, answers: dict, *extra: str, unit: str = ""):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", answers, unit)), *extra, "--out", str(out)])
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    return code, (out / "report.md").read_text(encoding="utf-8"), result["outputs"]["uls8_score"]["value"], out


def test_manifest_matches_presets():
    declared = [item for item in MANIFEST["inputs"] if item["from"] == "measurements"]
    assert [item["key"] for item in declared] == list(KEYS)
    for item, (key, number, topic, _rev) in zip(declared, ITEMS):
        assert item["unit"] == "score" and item["range"] == [1, 4] and item["required"] is True
        assert f"第{number}题" in item["label_zh"] and topic in item["label_zh"]
    assert REVERSED == ("uls8_item3", "uls8_item6")
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["entry"]["result_json"] is True
    assert [(o["key"], o["unit"]) for o in MANIFEST["outputs"]] == [("uls8_score", "score")]
    assert (TOTAL_MIN, TOTAL_MAX) == (8, 32)


def test_published_range_and_reverse_scoring():
    assert total(LEAST) == 8
    assert total(MOST) == 32
    # Reversal: answering 4 ("often") to "outgoing" counts 1; answering 1 counts 4.
    flat = {key: 1 for key in KEYS}
    assert total(flat) == 6 * 1 + 2 * 4
    flat4 = {key: 4 for key in KEYS}
    assert total(flat4) == 6 * 4 + 2 * 1


@pytest.mark.parametrize("answers, expected", [(LEAST, 8), (MOST, 32)], ids=["min", "max"])
def test_result_json_holds_the_score(tmp_path: Path, answers, expected):
    code, text, value, out = _run(tmp_path, answers, "--age", "70")
    assert code == 0
    assert value == expected
    assert f"得分是 **{expected}**" in text
    assert not (out / "problems.json").exists()


def test_answer_words_and_plain_lines(tmp_path: Path):
    words = ["经常", "有时", "从不", "很少", "总是", "很少", "有时", "从不"]
    measures = tmp_path / "m.txt"
    measures.write_text("\n".join(f"第{n}题,{word}" for n, word in enumerate(words, start=1)) + "\n", encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(measures), "--out", str(out)]) == 0
    # 4 + 3 + (5-1) + 2 + 4 + (5-2) + 3 + 1
    assert json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]["uls8_score"]["value"] == 24


def test_score_unit_written_as_fen_is_accepted(tmp_path: Path):
    code, _text, value, _out = _run(tmp_path, MOST, unit="分")
    assert code == 0 and value == 32


@pytest.mark.parametrize(
    "change, extra, reason",
    [
        ({"uls8_item1": "5"}, [], "不在合理范围"),
        ({"uls8_item4": "0"}, [], "不在合理范围"),
        ({"uls8_item2": "2.5"}, [], "整数"),
        ({"uls8_item5": "maybe"}, [], "不是一个可以计算的数"),
        ({"uls8_item8": None}, [], "缺少"),
        ({}, ["--age", "8"], "实足年龄"),
    ],
    ids=["above-4", "zero", "half", "text", "missing-item", "age"],
)
def test_bad_answers_stop_the_computation(tmp_path: Path, change, extra, reason):
    answers = dict(MOST)
    for key, value in change.items():
        if value is None:
            answers.pop(key)
        else:
            answers[key] = value
    code, text, value, out = _run(tmp_path, answers, *extra)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert value is None
    assert (out / "problems.json").exists()
    assert "输入没有通过检查" in text and reason in text
    assert "## 论文卡片" in text
    assert text.rstrip().splitlines()[-1].startswith("边界: ")


def test_wrong_unit_is_refused(tmp_path: Path):
    code, text, value, _out = _run(tmp_path, MOST, unit="mg/dL")
    assert code == skillkit.EXIT_INPUT_PROBLEM and value is None
    assert "不能换算" in text


def test_conflicting_duplicate_is_refused(tmp_path: Path):
    path = _csv(tmp_path / "m.csv", MOST)
    path.write_text(path.read_text(encoding="utf-8") + "q1,2,\n", encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(path), "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    assert "出现了两次" in (out / "report.md").read_text(encoding="utf-8")
