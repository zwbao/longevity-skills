"""Printed expectations: Li et al., Circulation 2018 Table 2 and eTable 1.

These are direct stratum lookups, not validation of a personal risk model.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def run(tmp_path, status="current", count="15", unit="1", targets=None):
    source = tmp_path / "input.csv"
    source.write_text("marker,value,unit\n" + (f"每日卷烟支数,{count},{unit}\n" if count is not None else ""))
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(source), "--out", str(out)]
    if status is not None:
        args += ["--smoking-status", status]
    if targets is not None:
        target = tmp_path / "target.csv"
        target.write_text("marker,value,unit\n" + targets)
        args += ["--targets", str(target)]
    result = subprocess.run(args, capture_output=True, text=True)
    return result, out


def outputs(out):
    return {k: v["value"] for k, v in json.loads((out / "result.json").read_text())["outputs"].items()}


def test_table2_current_15_24(tmp_path):
    # Table 2: Current 15–24/day | 2.33 (2.21–2.45) | 2.28 (2.11–2.48) | 2.62 (2.37–2.91)
    result, out = run(tmp_path)
    assert result.returncode == 0, result.stderr
    actual = outputs(out)
    for cause, expected in zip(("all_cause", "cancer", "cvd"),
                               ((2.33, 2.21, 2.45), (2.28, 2.11, 2.48), (2.62, 2.37, 2.91))):
        assert tuple(actual[f"{cause}_{part}"] for part in ("hr", "ci_low", "ci_high")) == expected
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("你的吸烟分档")
    assert "边界" in report and "不是个人死亡概率" in report


def test_etable1_current_15_24(tmp_path):
    # eTable 1, p. 6: Current 15-24/day | 2.46 (2.31-2.61) | 2.13 (1.95-2.34) | 3.32 (2.94-3.76)
    result, out = run(tmp_path, count="24")
    assert result.returncode == 0, result.stderr
    actual = outputs(out)
    for cause, expected in zip(("all_cause", "cancer", "cvd"),
                               ((2.46, 2.31, 2.61), (2.13, 1.95, 2.34), (3.32, 2.94, 3.76))):
        assert tuple(actual[f"before75_{cause}_{part}"] for part in ("hr", "ci_low", "ci_high")) == expected


@pytest.mark.parametrize("status,count,expected", [
    ("never", None, (1.0, None, None)),
    ("past", "0", (1.41, 1.38, 1.44)),
    ("current", "1", (2.02, 1.93, 2.10)),
    ("current", "14", (2.02, 1.93, 2.10)),
    ("current", "24", (2.33, 2.21, 2.45)),
    ("current", "25", (2.87, 2.70, 3.06)),
])
def test_table2_smoking_rows(tmp_path, status, count, expected):
    result, out = run(tmp_path, status, count)
    assert result.returncode == 0, result.stderr
    actual = outputs(out)
    assert tuple(actual[f"all_cause_{part}"] for part in ("hr", "ci_low", "ci_high")) == expected


@pytest.mark.parametrize("status,count,unit", [
    (None, "15", "1"), ("unknown", "15", "1"), ("current", None, "1"),
    ("current", "15", "pack/day"), ("current", "201", "1"),
    ("current", "NaN", "1"), ("current", "14.5", "1"),
    ("current", "0", "1"), ("past", "10", "1"), ("never", "1", "1"),
])
def test_bad_inputs_stop_without_readout(tmp_path, status, count, unit):
    result, out = run(tmp_path, status, count, unit)
    assert result.returncode == 3, result.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    text = (out / "report.md").read_text()
    assert "论文卡片" in text and "边界" in text and "2.33" not in text


def test_manifest_matches_presets():
    sys.path.insert(0, str(ROOT / "scripts"))
    from presets import MEASUREMENTS
    manifest = json.loads((ROOT / "skill.json").read_text())
    assert [(x["key"], x["unit"], x["range"]) for x in manifest["inputs"] if x["from"] == "measurements"] == MEASUREMENTS
    assert manifest["inputs_status"] == "verified"


def test_targets_use_printed_groups_and_do_not_erase_history(tmp_path):
    result, out = run(tmp_path, count="25", targets="cigarettes_per_day,0,1\n")
    assert result.returncode == 0, result.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    assert levers["current"]["all_cause_hr"] == 2.87
    assert levers["targets"]["all_cause_hr"] == 1.41
    assert levers["targets"]["smoking_category"] == "past"
    assert levers["levers"][0]["all_cause_hr_delta"] == pytest.approx(1.41 - 2.87)
    assert "不能预测戒烟后" in (out / "report.md").read_text()


@pytest.mark.parametrize("target", ["cigarettes_per_day,9,pack/day\n", "cigarettes_per_day,201,1\n", "smoking_status,0,1\n", "", "cigarettes_per_day,0.5,1\n"])
def test_bad_targets_remove_previous_results(tmp_path, target):
    result, out = run(tmp_path)
    assert result.returncode == 0
    result, out = run(tmp_path, targets=target)
    assert result.returncode == 3, result.stderr
    assert not (out / "result.json").exists() and not (out / "levers.json").exists()


def test_bad_measurement_removes_previous_results(tmp_path):
    assert run(tmp_path)[0].returncode == 0
    result, out = run(tmp_path, count="-1")
    assert result.returncode == 3
    assert not (out / "result.json").exists()
