"""Box 1 descriptor-to-grade reproduction; no synthetic clinical decision rule."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import presets


def run_report(tmp_path, rows, out_name="out"):
    source = tmp_path / "assessment.csv"
    source.write_text("item,value,unit\n" + "\n".join(rows) + "\n", encoding="utf-8")
    out = tmp_path / out_name
    run = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                          "--measurements", str(source), "--out", str(out)],
                         capture_output=True, text=True)
    result = json.loads((out / "result.json").read_text())["outputs"]
    return run, result, (out / "report.md").read_text(), out


def test_box1_mildly_frail_grade(tmp_path):
    # Box 1: "5 Mildly frail — with limited dependence on others for
    # instrumental activities of daily living". The input records the clinician's
    # selection of this complete descriptor, not an independently scored symptom.
    run, result, report, _ = run_report(tmp_path, ["Mildly frail,1,1"])
    assert run.returncode == 0, run.stderr
    assert result["cfs7_grade"]["value"] == 5
    assert result["cfs7_category"]["value"] == "轻度衰弱"
    assert "工具性日常生活活动" in report


@pytest.mark.parametrize("descriptor,grade", [
    ("Very fit", 1), ("Well", 2), ("Well with treated comorbid disease", 3),
    ("Apparently vulnerable", 4), ("Mildly frail", 5),
    ("Moderately frail", 6), ("Severely frail", 7),
])
def test_box1_all_printed_grade_labels(tmp_path, descriptor, grade):
    # Expected ordinal numbers and labels are printed in Box 1, not model outputs.
    run, result, report, _ = run_report(tmp_path, [f"{descriptor},1,1"])
    assert run.returncode == 0, run.stderr
    assert result["cfs7_grade"]["value"] == grade
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert presets.BOUNDARY in report
    assert "10.1503/cmaj.050051" in report


@pytest.mark.parametrize("rows,kind", [
    (["Mildly frail,1,mg/L"], "unit"),
    (["Mildly frail,8,1"], "range"),
    (["Mildly frail,0.5,1"], "selection"),
    (["Mildly frail,NaN,1"], "parse"),
    ([], "missing"),
    (["Mildly frail,0,1"], "missing"),
    (["Mildly frail,1,1", "Moderately frail,1,1"], "selection"),
    (["CFS,8,score"], "unknown"),
    (["Mildly frail,1,1", "Mildly frail,0,1"], "duplicate"),
])
def test_invalid_inputs_stop_without_grade(tmp_path, rows, kind):
    run, result, report, out = run_report(tmp_path, rows)
    assert run.returncode == 3, run.stderr
    assert all(item["value"] is None for item in result.values())
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert kind in {p["kind"] for p in problems}
    assert "## 你的结果" not in report
    assert "## 论文卡片" in report and presets.BOUNDARY in report


def test_reusing_output_does_not_leave_stale_results(tmp_path):
    run_report(tmp_path, ["轻度衰弱,1,1"])
    _, result, _, out = run_report(tmp_path, [])
    assert all(item["value"] is None for item in result.values())
    assert (out / "problems.json").exists()
    run, result, _, out = run_report(tmp_path, ["轻度衰弱,1,1"])
    assert run.returncode == 0 and result["cfs7_grade"]["value"] == 5
    assert not (out / "problems.json").exists()


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / "skill.json").read_text())
    assert {i["key"] for i in manifest["inputs"]} == set(presets.DESCRIPTORS)
    for spec in manifest["inputs"]:
        assert spec["unit"] == presets.SELECTION_UNIT == "1"
        assert spec["range"] == list(presets.SELECTION_RANGE) == [0, 1]
        assert spec["accept"] == {}
        assert spec["from"] == "measurements"
    assert manifest["validation"]["status"] == "reproduced"
    assert manifest["inputs_status"] == "verified"
