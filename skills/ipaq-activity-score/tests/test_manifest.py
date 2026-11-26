"""Engineering checks only: the paper prints no complete individual score example.

Table 1, p.1382 prints short-form MET weights: vigorous 8, moderate 4,
walking vigorous 5, moderate 3.3, slow 2.5. These are parameter checks,
not a claim to reproduce a printed personal MET-min/week result.
Synthetic questionnaire responses below test algebra and input handling;
no synthetic total is presented as a paper-printed expected value.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ipaq_presets", ROOT / "scripts/presets.py")
presets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(presets)


def sample():
    return {"walking_days": 5, "walking_min": 30,
            "moderate_days": 2, "moderate_min": 40,
            "vigorous_days": 3, "vigorous_min": 20}


def csv_text(values):
    return "marker,value,unit\n" + "".join(
        f"{key},{value},{'d' if key.endswith('_days') else 'min'}\n"
        for key, value in values.items())


def run(tmp_path, text=None, targets=None, pace="moderate", age="40"):
    out = tmp_path / "out"
    command = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--out", str(out)]
    if text is not None:
        path = tmp_path / "measurements.csv"
        path.write_text(text)
        command += ["--measurements", str(path)]
    if targets is not None:
        path = tmp_path / "targets.csv"
        path.write_text(targets)
        command += ["--targets", str(path)]
    if pace is not None:
        command += ["--walking-pace", pace]
    if age is not None:
        command += ["--age", age]
    return subprocess.run(command, capture_output=True, text=True), out


def outputs(out):
    return {k: v["value"] for k, v in json.loads((out / "result.json").read_text())["outputs"].items()}


def test_manifest_and_printed_parameters():
    manifest = json.loads((ROOT / "skill.json").read_text())
    assert manifest["validation"]["status"] == "draft"
    assert manifest["inputs_status"] == "draft"
    actual = {s["key"]: (s["unit"], tuple(s["range"])) for s in manifest["inputs"] if "range" in s}
    assert actual == presets.INPUT_RULES
    assert presets.METS == {"vigorous": 8, "moderate": 4}
    assert presets.WALKING_METS == {"vigorous": 5, "moderate": 3.3, "slow": 2.5}
    # Appendix B, pp.1392–1395, printed range and qualifying bout duration.
    assert presets.MAX_DAILY_MIN == 960
    assert presets.MIN_BOUT_MIN == 10


@pytest.mark.parametrize("pace,weight", [("slow", 2.5), ("moderate", 3.3), ("vigorous", 5)])
def test_normal_outputs_obey_printed_formula(tmp_path, pace, weight):
    values = sample()
    result, out = run(tmp_path, csv_text(values), pace=pace)
    assert result.returncode == 0, result.stderr
    got = outputs(out)
    # Check coefficients and the additive identity, not an invented paper example.
    for activity, met in (("walking", weight), ("moderate", 4), ("vigorous", 8)):
        duration = values[f"{activity}_days"] * values[f"{activity}_min"]
        assert got[f"{activity}_met_min_week"] / duration == pytest.approx(met)
    assert got["total_met_min_week"] == pytest.approx(sum(got[f"{a}_met_min_week"] for a in presets.ACTIVITIES))
    assert got["sitting_weekday_min"] is None
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("你的活动量")
    assert "边界:" in report and "尚未复现" in report


@pytest.mark.parametrize("mutation", [
    "missing", "wrong_unit", "out_of_range", "fractional_days", "nan",
    "missing_pace", "bad_pace", "missing_age", "bad_age", "young_age",
    "unknown", "duplicate", "short_bout", "inconsistent_zero", "sentinel",
])
def test_invalid_input_exits_3_without_scores(tmp_path, mutation):
    values = sample()
    pace, age = "moderate", "40"
    if mutation == "missing": del values["walking_min"]
    if mutation == "out_of_range": values["walking_days"] = 8
    if mutation == "fractional_days": values["walking_days"] = 2.5
    if mutation == "nan": values["walking_min"] = "nan"
    if mutation == "sentinel": values["walking_min"] = 998
    if mutation == "short_bout": values["walking_min"] = 5
    if mutation == "inconsistent_zero": values["walking_days"] = 0
    if mutation == "missing_pace": pace = None
    if mutation == "bad_pace": pace = "fastest"
    if mutation == "missing_age": age = None
    if mutation == "bad_age": age = "unknown"
    if mutation == "young_age": age = "17"
    text = csv_text(values)
    if mutation == "wrong_unit": text = text.replace("walking_min,30,min", "walking_min,30,mg/L")
    if mutation == "unknown": text += "typo,30,min\n"
    if mutation == "duplicate": text += "walking_min,50,min\n"
    result, out = run(tmp_path, text, pace=pace, age=age)
    assert result.returncode == 3, result.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert all(v is None for v in outputs(out).values())
    assert "你的活动量" not in (out / "report.md").read_text()
    assert "论文卡片" in (out / "report.md").read_text()
    assert "边界:" in (out / "report.md").read_text()
    assert not (out / "levers.json").exists()


def test_missing_file_and_empty_inputs(tmp_path):
    result, out = run(tmp_path)
    assert result.returncode == 3
    assert all(v is None for v in outputs(out).values())


def test_units_aliases_and_sitting_does_not_change_total(tmp_path):
    text = csv_text(sample())
    result, out = run(tmp_path, text)
    assert result.returncode == 0
    baseline = outputs(out)
    text = text.replace("walking_min,30,min", "步行活动日平均时长,0.5,h")
    text += "工作日坐姿时长,4,h\n"
    result, out = run(tmp_path, text)
    assert result.returncode == 0, result.stderr
    got = outputs(out)
    assert got["total_met_min_week"] == baseline["total_met_min_week"]
    assert got["sitting_weekday_min"] / 4 == 60  # exact h-to-min unit conversion


def test_targets_sensitivity_and_stale_output_cleanup(tmp_path):
    text = csv_text(sample())
    result, out = run(tmp_path, text, csv_text({"walking_min": 60}))
    assert result.returncode == 0, result.stderr
    lever = json.loads((out / "levers.json").read_text())
    assert lever["schema"] == "longevity-levers/1"
    current, target = lever["current"], lever["targets"]["outputs"]
    assert target["walking_met_min_week"] == 2 * current["walking_met_min_week"]
    assert lever["levers"][0]["total_delta"] == pytest.approx(current["walking_met_min_week"])
    sensitivity = {s["key"]: s for s in lever["sensitivity"]}
    assert sensitivity["walking_min"]["met_min_week_per_unit"] / sample()["walking_days"] == 3.3
    # Reject bad targets rather than leaving a prior successful readout behind.
    result, out = run(tmp_path, text, csv_text({"walking_days": 8}))
    assert result.returncode == 3
    assert all(v is None for v in outputs(out).values())
    assert not (out / "levers.json").exists()
    result, out = run(tmp_path, text)
    assert result.returncode == 0
    assert not (out / "problems.json").exists()


def test_explicit_zero_and_infeasible_individual_target(tmp_path):
    values = {k: 0 for k in sample()}
    result, out = run(tmp_path, csv_text(values), csv_text({"walking_days": 2, "walking_min": 20}))
    assert result.returncode == 0, result.stderr
    lever = json.loads((out / "levers.json").read_text())
    assert lever["targets"]["outputs"]["total_met_min_week"] > lever["current"]["total_met_min_week"]
    assert all(row["outputs"] is None for row in lever["levers"])
    assert all(row["reason_zh"] for row in lever["levers"])
