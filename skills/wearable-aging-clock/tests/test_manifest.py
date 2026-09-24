"""skill.json inputs match the script, and unit or range mistakes stop the subtraction.

Before the kit, a PpgAge gap written where PpgAge belongs was subtracted again,
an age of 400 gave a gap, and a unit column was ignored.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import BOUNDARY, MAE_POOLED, ppg_gap

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
# Row names the report code reads in pair(): items() lower-cases them.
SCRIPT_NAMES = {"ppgage": ("ppgage", "ppg_age"), "age": ("age",)}


def _csv(path: Path, rows, header=None) -> Path:
    header = header or ",".join(MANIFEST["entry"]["measurements_header"])
    path.write_text("\n".join([header] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _result(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "wearable-aging-clock"
    return result["outputs"]


def test_manifest_matches_script():
    measured = [item["key"] for item in MANIFEST["inputs"] if item["from"] == "measurements"]
    assert measured == ["ppgage"]
    index = skillkit.alias_index(skillkit.input_specs(MANIFEST))
    for name in SCRIPT_NAMES["ppgage"]:
        assert index[skillkit.fold_name(name)][0]["key"] == "ppgage"
    spec = skillkit.spec_by_key(MANIFEST, "ppgage")
    assert (spec["unit"], spec["required"]) == ("a", True)
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"], age["required"]) == ("profile", "--age", "a", True)
    assert all(personal_report._is_age_row(name, age) for name in SCRIPT_NAMES["age"] + ("年龄", "实足年龄"))
    assert not personal_report._is_age_row("ppgage", age)
    assert MANIFEST["inputs_status"] == "verified"
    entry = MANIFEST["entry"]
    assert (entry["measurements_flag"], entry["age_flag"], entry["out_flag"]) == ("--measurements", "--age", "--out")
    assert entry["result_json"] is True
    assert personal_report.has_header(",".join(entry["measurements_header"]))
    assert {item["key"]: item["unit"] for item in MANIFEST["outputs"]} == {"ppgage_gap": "a"}


@pytest.mark.parametrize(
    "rows, age",
    [
        ([("ppgage", "70", "岁")], "64"),
        ([("脉搏波年龄", "70", ""), ("age", "64", "")], None),
        ([("PpgAge", "70", "a")], "64"),
    ],
    ids=["age-flag", "age-row", "english-name"],
)
def test_correct_csv_gives_the_same_gap(tmp_path: Path, rows, age):
    out = tmp_path / "out"
    argv = ["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]
    if age is not None:
        argv += ["--age", age]
    assert personal_report.main(argv) == 0
    expected = ppg_gap(70.0, 64.0)
    text = (out / "report.md").read_text(encoding="utf-8")
    assert f"脉搏波年龄减去实足年龄是 {expected:.1f} 年" in text
    assert f"- 脉搏波年龄差：{expected:.1f} 年。" in text
    assert str(MAE_POOLED) in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    outputs = _result(out)
    assert outputs["ppgage_gap"]["value"] == pytest.approx(expected)
    assert outputs["ppgage_gap"]["unit"] == "a"
    assert not (out / "problems.json").exists()


def test_old_two_column_file_still_works(tmp_path: Path):
    old = tmp_path / "old.csv"
    old.write_text("item,value\nppgage,71.5\nage,64\n", encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(old), "--out", str(out)]) == 0
    assert _result(out)["ppgage_gap"]["value"] == pytest.approx(ppg_gap(71.5, 64.0))


@pytest.mark.parametrize(
    "rows, age, reason",
    [
        ([("ppgage", "70", "%")], "64", "不能换算"),
        ([("ppgage", "6", "")], "64", "不在合理范围"),
        ([("ppgage", "70岁左右", "")], "64", "不是一个可以计算的数"),
        ([("ppgage", "70", ""), ("ppg_age", "72", "")], "64", "出现了两次"),
        ([("ppgage", "70", "")], "400", "实足年龄"),
        ([("ppgage", "70", ""), ("age", "640", "")], None, "实足年龄"),
        ([("ppgage", "70", "")], None, "缺少实足年龄"),
        ([("age", "64", "")], None, "缺少脉搏波年龄"),
    ],
    ids=["unit", "gap-not-age", "text", "duplicate", "age-flag-range", "age-row-range", "no-age", "no-ppgage"],
)
def test_wrong_or_missing_input_is_refused(tmp_path: Path, rows, age, reason):
    out = tmp_path / "out"
    argv = ["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]
    if age is not None:
        argv += ["--age", age]
    assert personal_report.main(argv) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 腕部脉搏波年龄差"
    assert "## 论文卡片" in text
    assert "输入没有通过检查，所以没有算出年龄差" in text and reason in text
    assert "这次算出" not in text and str(MAE_POOLED) not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))
    assert problems["schema"] == "longevity-problems/1" and problems["problems"]
    assert _result(out)["ppgage_gap"]["value"] is None


def test_nothing_given_is_refused(tmp_path: Path):
    out = tmp_path / "out"
    assert personal_report.main(["--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    keys = {item["key"] for item in json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]}
    assert keys == {"ppgage", "age"}


def test_a_good_run_clears_old_problems(tmp_path: Path):
    out = tmp_path / "out"
    bad = _csv(tmp_path / "bad.csv", [("ppgage", "70", "%")])
    assert personal_report.main(["--measurements", str(bad), "--age", "64", "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    good = _csv(tmp_path / "good.csv", [("ppgage", "70", "")])
    assert personal_report.main(["--measurements", str(good), "--age", "64", "--out", str(out)]) == 0
    assert not (out / "problems.json").exists()
    assert _result(out)["ppgage_gap"]["value"] == pytest.approx(ppg_gap(70.0, 64.0))
