"""Printed examples: Table 1 (p. 531), Falls scoring cells.

None = 0
1–3 falls = 1
4 or more falls = 2
"""

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_table1_falls_per_term_scores():
    from personal_report import falls_points

    assert falls_points(0) == 0
    for count in (1, 2, 3):
        assert falls_points(count) == 1
    assert falls_points(4) == 2


def test_manifest_matches_presets():
    from presets import MEASUREMENTS

    manifest = json.loads((ROOT / "skill.json").read_text())
    assert {s["key"]: (s["unit"], tuple(s["range"])) for s in manifest["inputs"]
            if s["from"] == "measurements"} == MEASUREMENTS
    assert manifest["validation"]["status"] == "reproduced"
    assert manifest["inputs_status"] == "verified"


# Integration fixture: all Table 1 responses at their printed minimum.
VALID = [
    ("strength_score", "0", "score"),
    ("walking_score", "0", "score"),
    ("chair_score", "0", "score"),
    ("stairs_score", "0", "score"),
    ("falls_past_year_count", "0", "1"),
]


def run_report(tmp_path, rows=VALID, extra=()):
    measurements = tmp_path / "measurements.csv"
    measurements.write_text("marker,value,unit\n" + "\n".join(",".join(row) for row in rows) + "\n")
    out = tmp_path / "out"
    run = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                          "--measurements", str(measurements), "--out", str(out), *extra],
                         capture_output=True, text=True)
    return run, out


def test_printed_score_endpoints_and_threshold(tmp_path):
    from personal_report import classify

    run, out = run_report(tmp_path)
    assert run.returncode == 0, run.stderr
    outputs = json.loads((out / "result.json").read_text())["outputs"]
    assert outputs["sarc_f_total_score"]["value"] == 0
    assert outputs["sarc_f_category"]["value"] == "below_cutoff"
    rows = [(key, "4" if key == "falls_past_year_count" else "2", unit) for key, _, unit in VALID]
    run, out = run_report(tmp_path, rows)
    assert run.returncode == 0, run.stderr
    outputs = json.loads((out / "result.json").read_text())["outputs"]
    assert outputs["sarc_f_total_score"]["value"] == 10
    assert outputs["falls_score"]["value"] == 2
    assert outputs["sarc_f_category"]["value"] == "screen_positive"
    assert classify(4) == "screen_positive"
    assert classify(3) == "below_cutoff"
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "边界:" in report and "不能单独确诊" in report


@pytest.mark.parametrize("key,value,unit", [
    ("strength_score", "1", "kg"),
    ("walking_score", "3", "score"),
    ("chair_score", "0.5", "score"),
    ("stairs_score", "nan", "score"),
    ("falls_past_year_count", "-1", "1"),
    ("falls_past_year_count", "1.5", "1"),
    ("falls_past_year_count", "1001", "1"),
    ("falls_past_year_count", "2", "score"),
])
def test_invalid_input_exits_three_without_result(tmp_path, key, value, unit):
    rows = [(k, value, unit) if k == key else (k, v, u) for k, v, u in VALID]
    run, out = run_report(tmp_path, rows)
    assert run.returncode == 3, run.stderr
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()
    report = (out / "report.md").read_text()
    assert "## 论文卡片" in report and "边界:" in report
    assert "## 你的结果" not in report


def test_missing_input_and_stale_output_cleanup(tmp_path):
    assert run_report(tmp_path)[0].returncode == 0
    run, out = run_report(tmp_path, VALID[:-1])
    assert run.returncode == 3 and not (out / "result.json").exists()
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert any(p["key"] == "falls_past_year_count" and p["kind"] == "missing" for p in problems)
    assert run_report(tmp_path)[0].returncode == 0
    assert not (out / "problems.json").exists()


def test_aliases(tmp_path):
    rows = [("力量", "0", "score"), ("Assistance in walking", "0", "score"),
            ("起身", "0", "score"), ("Climb stairs", "0", "score"),
            ("过去一年跌倒次数", "0", "1")]
    run, out = run_report(tmp_path, rows)
    assert run.returncode == 0, run.stderr
    assert json.loads((out / "result.json").read_text())["outputs"]["sarc_f_total_score"]["value"] == 0


@pytest.mark.parametrize("extra", [("--age", "unknown"), ("--age", "121"), ("--sex", "invalid")])
def test_invalid_optional_profile(tmp_path, extra):
    run, out = run_report(tmp_path, extra=extra)
    assert run.returncode == 3
    assert not (out / "result.json").exists()
