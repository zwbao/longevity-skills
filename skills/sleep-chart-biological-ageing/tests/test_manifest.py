"""skill.json inputs match presets, and unit mistakes stop the grouping.

Run by hand against the old script: 450 minutes written without a unit was
read as 450 hours and put in the long bin, a percent unit was ignored and the
number binned as hours, `睡眠时长,420,分钟` was not recognised, and `7:30` was
reported as no hours given.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import LONG_ABOVE, SHORT_BELOW

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
BINS = ("「短」", "「正常」", "「长」")


def _csv(path: Path, rows, header: str = "item,value,unit") -> Path:
    lines = [header] + [",".join(row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, header: str = "item,value,unit"):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows, header)), "--out", str(out)])
    return code, out


def _result(out: Path) -> dict:
    return json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]


def test_manifest_matches_presets():
    declared = {item["key"]: item for item in MANIFEST["inputs"] if item["from"] == "measurements"}
    assert list(declared) == ["sleep_hours"]
    spec = declared["sleep_hours"]
    assert skillkit.normalize_unit(spec["unit"]) == "h"
    low, high = spec["range"]
    assert low < SHORT_BELOW < LONG_ABOVE < high
    factor = skillkit.unit_factor(spec, "min")
    assert 360 * factor == SHORT_BELOW
    assert 480 * factor == LONG_ABOVE
    assert [item["key"] for item in MANIFEST["outputs"]] == ["sleep_duration_bin"]
    assert "unit" not in MANIFEST["outputs"][0]
    assert MANIFEST["entry"]["measurements_flag"] == "--measurements"
    assert MANIFEST["entry"]["measurements_header"] == ["item", "value", "unit"]


def test_inputs_are_verified():
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["entry"]["result_json"] is True


@pytest.mark.parametrize("row, reason", [
    (("睡眠时长", "450", ""), "单位是 min"),
    (("sleep_hours", "450", ""), "不在合理范围"),
    (("sleep", "30", "h"), "不在合理范围"),
    (("sleep_hours", "7", "%"), "不能换算"),
    (("睡眠时长", "7", "s"), "不能换算"),
    (("睡眠时长", "7:30", ""), "不是一个可以计算的数"),
])
def test_wrong_unit_or_range_stops_the_grouping(tmp_path: Path, row, reason):
    code, out = _run(tmp_path, [row])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 睡眠时长分组"
    assert "## 论文卡片" in text
    assert reason in text
    assert "所以这次没有分组" in text
    assert not any(label in text for label in BINS)
    assert "这次落在这里" not in text
    assert text.splitlines()[-1] == f"边界: {personal_report.BOUNDARY}"
    assert (out / "problems.json").exists()
    assert _result(out)["sleep_duration_bin"]["value"] is None


@pytest.mark.parametrize("row, expected", [
    (("sleep_hours", "5.5", ""), "短"),
    (("sleep_hours", "7.82", ""), "正常"),
    (("睡眠时长", "7.5", "小时"), "正常"),
    (("sleep", "9", "h"), "长"),
    (("睡眠时长", "330", "分钟"), "短"),
    (("睡眠时长", "360", "min"), "正常"),
    (("总睡眠时长", "480", "minutes"), "正常"),
    (("睡眠时长", "481", "min"), "长"),
])
def test_result_json_holds_the_bin(tmp_path: Path, row, expected):
    code, out = _run(tmp_path, [row])
    assert code == 0
    assert f"「{expected}」" in (out / "report.md").read_text(encoding="utf-8")
    result = _result(out)["sleep_duration_bin"]
    assert result["value"] == expected
    assert result["unit"] == ""
    assert not (out / "problems.json").exists()


def test_two_column_file_still_reads_hours(tmp_path: Path):
    code, out = _run(tmp_path, [("sleep_hours", "6")], header="item,value")
    assert code == 0
    assert _result(out)["sleep_duration_bin"]["value"] == "正常"


def test_no_hours_is_not_a_problem(tmp_path: Path):
    out = tmp_path / "out"
    assert personal_report.main(["--out", str(out)]) == 0
    assert "没有提供睡眠小时数，所以这次没有分组。" in (out / "report.md").read_text(encoding="utf-8")
    assert _result(out)["sleep_duration_bin"]["value"] is None
    assert not (out / "problems.json").exists()


def test_a_good_run_clears_old_problems(tmp_path: Path):
    out = tmp_path / "out"
    bad = _csv(tmp_path / "bad.csv", [("睡眠时长", "450", "")])
    assert personal_report.main(["--measurements", str(bad), "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    good = _csv(tmp_path / "good.csv", [("睡眠时长", "450", "分钟")])
    assert personal_report.main(["--measurements", str(good), "--out", str(out)]) == 0
    assert not (out / "problems.json").exists()
    assert _result(out)["sleep_duration_bin"]["value"] == "正常"
