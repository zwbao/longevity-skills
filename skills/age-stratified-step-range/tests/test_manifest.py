"""Printed ranges are regression checks, not a reproduced personal example.

Results (Figure 3 discussion) and Appendix Figure S2c, p19 print
6000–8000 for adults >=60 and 8000–10 000 for adults <60.
The paper prints no individual input-to-category worked example; validation
therefore remains draft. Other fixtures below are software checks only.
"""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import presets


def test_printed_age_group_ranges():
    assert presets.AGE_SPLIT_YEARS == 60
    assert presets.reference_range(60) == (6000, 8000)
    assert presets.reference_range(59) == (8000, 10000)


def run(tmp_path, rows="daily_steps,6000,1\n", age="60", targets=None):
    path = tmp_path / "measurements.csv"
    path.write_text("marker,value,unit\n" + rows)
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(path), "--out", str(out)]
    if age is not None:
        args += ["--age", age]
    if targets is not None:
        target_path = tmp_path / "targets.csv"
        target_path.write_text("marker,value,unit\n" + targets)
        args += ["--targets", str(target_path)]
    proc = subprocess.run(args, text=True, capture_output=True)
    return proc, out


def outputs(out):
    return {k: v["value"] for k, v in json.loads((out / "result.json").read_text())["outputs"].items()}


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / "skill.json").read_text())
    specs = {x["key"]: x for x in manifest["inputs"]}
    assert specs["daily_steps"]["unit"] == presets.COUNT_UNIT == "1"
    assert specs["daily_steps"]["range"] == list(presets.STEP_INPUT_RANGE)
    assert specs["age"]["range"] == list(presets.AGE_INPUT_RANGE)
    assert specs["age"]["unit"] == "a"
    assert manifest["validation"]["status"] == "draft"


@pytest.mark.parametrize("age,steps,position", [
    (60, 5999, "below"), (60, 6000, "within"), (60, 8000, "within"),
    (60, 8001, "above"), (59, 7999, "below"), (59, 8000, "within"),
    (59, 10000, "within"), (59, 10001, "above"), (59.99, 6000, "below"),
])
def test_cli_boundaries(tmp_path, age, steps, position):
    proc, out = run(tmp_path, f"日均步数,{steps},1\n", str(age))
    assert proc.returncode == 0, proc.stderr
    result = outputs(out)
    assert result["step_position"] == position
    assert result["daily_steps"] == steps
    assert set(result) == {s["key"] for s in json.loads((ROOT / "skill.json").read_text())["outputs"]}
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的步数")
    assert "仍在验证" in report
    assert f"边界: {presets.BOUNDARY}" in report


@pytest.mark.parametrize("rows,age", [
    ("daily_steps,6000,km\n", "60"), ("daily_steps,6000,/min\n", "60"),
    ("daily_steps,-1,1\n", "60"), ("daily_steps,100001,1\n", "60"),
    ("daily_steps,nan,1\n", "60"), ("daily_steps,abc,1\n", "60"),
    ("", "60"), ("daily_steps,6000,1\n", None),
    ("daily_steps,6000,1\n", "17"), ("daily_steps,6000,1\n", "abc"),
    ("daily_steps,6000,1\n", "nan"), ("daily_steps,6000,1\n", "131"),
    ("daily_steps,6000,1\ndaily_steps,7000,1\n", "60"),
])
def test_invalid_inputs_exit_three(tmp_path, rows, age):
    proc, out = run(tmp_path, rows, age)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert all(v is None for v in outputs(out).values())
    assert not (out / "levers.json").exists()
    report = (out / "report.md").read_text()
    assert "## 论文卡片" in report and "## 你的步数" not in report
    assert f"边界: {presets.BOUNDARY}" in report


def test_target_comparison_and_stale_output_cleanup(tmp_path):
    proc, out = run(tmp_path, targets="daily_steps,8000,1\n")
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / "levers.json").read_text())
    assert result["schema"] == "longevity-levers/1"
    assert result["targets"]["outputs"]["step_position"] == "within"
    assert result["levers"][0]["daily_steps_delta"] == 2000
    assert result["sensitivity"][0]["signed_gap_per_step"] == 1
    proc, out = run(tmp_path, targets="daily_steps,9000,km\n")
    assert proc.returncode == 3
    assert not (out / "levers.json").exists()
    assert all(v is None for v in outputs(out).values())
    proc, out = run(tmp_path)
    assert proc.returncode == 0
    assert not (out / "problems.json").exists()
    assert "targets" not in json.loads((out / "levers.json").read_text())


def test_target_cannot_modify_age(tmp_path):
    proc, out = run(tmp_path, targets="age,50,a\n")
    assert proc.returncode == 3
    assert json.loads((out / "problems.json").read_text())["problems"]


def test_missing_file(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                           "--age", "60", "--measurements", str(tmp_path / "absent.csv"),
                           "--out", str(tmp_path / "out")], capture_output=True)
    assert proc.returncode == 3
    assert (tmp_path / "out/problems.json").exists()


@pytest.mark.parametrize("marker", ["daily_steps", "steps", "步数"])
def test_unitless_daily_count_accepted(tmp_path, marker):
    proc, out = run(tmp_path, f"{marker},7000,\n", "65")
    assert proc.returncode == 0, proc.stderr
    assert outputs(out)["step_position"] == "within"


@pytest.mark.parametrize("unit", ["步/周", "steps/week", "万步", "steps/day"])
def test_weekly_or_scaled_units_rejected(tmp_path, unit):
    proc, out = run(tmp_path, f"daily_steps,49000,{unit}\n", "65")
    assert proc.returncode == 3
