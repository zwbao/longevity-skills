"""skill.json inputs match the script, and a wrong or missing input stops the check.

Before the kit, an age of 820 was called a SuperAger, a --memory word outside
the three comparisons crashed with a traceback, and a missing --age or
--memory finished with exit code 0.
"""

import argparse
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import BOUNDARY, MEMORY_REFERENCE_AGE_HIGH, MEMORY_REFERENCE_AGE_LOW, SUPERAGER_MIN_AGE

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _result(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "hippocampal-neurogenesis-adulthood-ageing"
    return result["outputs"]


def _direct(tmp_path: Path, age, memory) -> str:
    """The report report(Namespace) writes, the path the older tests call."""
    ns = argparse.Namespace(medications=None, labs=None, out=tmp_path / "direct", age=age, memory=memory)
    return personal_report.report(ns).read_text(encoding="utf-8")


# The three openings the decision code wrote before the kit, word for word.
MATCH = "{age:g} 岁，情景记忆不低于 {low}–{high} 岁，符合 SuperAger 的入组写法。"
NO_MATCH = "按年龄和情景记忆核对，这次的记录不满足该定义。"
NOT_JUDGED = "年龄或情景记忆比较没有给全，这次没有判断是否符合 SuperAger。"


def test_manifest_matches_script():
    assert [spec["key"] for spec in MANIFEST["inputs"]] == ["memory", "age"]
    memory = skillkit.spec_by_key(MANIFEST, "memory")
    assert (memory["from"], memory["flag"], memory["required"]) == ("argument", "--memory", True)
    assert "unit" not in memory and "range" not in memory
    for word in personal_report.MEMORY_CHOICES:
        assert word in memory["note_zh"]
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"], age["required"]) == ("profile", "--age", "a", True)
    assert age["range"][0] < SUPERAGER_MIN_AGE < age["range"][1]
    assert MANIFEST["inputs_status"] == "verified"
    entry = MANIFEST["entry"]
    assert "measurements_flag" not in entry
    assert (entry["age_flag"], entry["out_flag"], entry["result_json"]) == ("--age", "--out", True)
    assert [item["key"] for item in MANIFEST["outputs"]] == ["superager"]


@pytest.mark.parametrize(
    "age, memory, expected",
    [
        ("82", "equal_or_better", "符合"),
        ("80", "equal_or_better", "符合"),
        ("79.5", "equal_or_better", "不满足"),
        ("85", "below", "不满足"),
        ("85", "unknown", None),
    ],
    ids=["superager", "exactly-80", "under-80", "memory-below", "memory-unknown"],
)
def test_valid_inputs_give_the_same_check(tmp_path: Path, age, memory, expected):
    out = tmp_path / "out"
    assert personal_report.main(["--age", age, "--memory", memory, "--out", str(out)]) == 0
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text == _direct(tmp_path, float(age), memory)
    assert _result(out)["superager"]["value"] == expected
    if expected == "符合":
        opening = MATCH.format(age=float(age), low=MEMORY_REFERENCE_AGE_LOW, high=MEMORY_REFERENCE_AGE_HIGH)
        assert float(age) >= SUPERAGER_MIN_AGE and f"- SuperAger：{opening}" in text
    elif expected == "不满足":
        opening = NO_MATCH
        assert "名单是空的。" in text
    else:
        opening = NOT_JUDGED
    assert f"\n\n{opening}\n\n## 方法算出的名单" in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert not (out / "problems.json").exists()


@pytest.mark.parametrize(
    "argv, reason",
    [
        (["--age", "820", "--memory", "equal_or_better"], "实足年龄"),
        (["--age", "82", "--memory", "better"], "只收 equal_or_better、below、unknown"),
        (["--memory", "equal_or_better"], "缺少实足年龄"),
        (["--age", "82"], "缺少情景记忆比较"),
    ],
    ids=["age-range", "memory-word", "no-age", "no-memory"],
)
def test_wrong_or_missing_input_is_refused(tmp_path: Path, argv, reason):
    out = tmp_path / "out"
    assert personal_report.main(argv + ["--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 情景记忆对照"
    assert "## 论文卡片" in text
    assert "输入没有通过检查，所以这次没有核对 SuperAger 的定义" in text and reason in text
    assert "符合 SuperAger 的入组写法" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert _result(out)["superager"]["value"] is None


def test_a_good_run_clears_old_problems(tmp_path: Path):
    out = tmp_path / "out"
    assert personal_report.main(["--age", "82", "--memory", "better", "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    assert personal_report.main(["--age", "82", "--memory", "equal_or_better", "--out", str(out)]) == 0
    assert not (out / "problems.json").exists()
    assert _result(out)["superager"]["value"] == "符合"
