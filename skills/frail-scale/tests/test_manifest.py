"""Printed per-term examples first; no patient-level example is claimed.

Morley et al. 2012, Appendix 1, Illnesse:
The total illnesses (0–11) are recoded as 0–4 = 0 and 5–11 = 1.
"""

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_appendix_illness_per_term_scores():
    from personal_report import illness_points

    # Every printed count in the two intervals, with the printed point values.
    for count in range(0, 4 + 1):
        assert illness_points(count) == 0
    for count in range(5, 11 + 1):
        assert illness_points(count) == 1


def test_manifest_matches_presets():
    from presets import MEASUREMENTS

    manifest = json.loads((ROOT / "skill.json").read_text())
    actual = {s["key"]: (s["unit"], tuple(s["range"]))
              for s in manifest["inputs"] if s["from"] == "measurements"}
    assert actual == MEASUREMENTS
    assert manifest["validation"]["status"] == "reproduced"
    assert manifest["inputs_status"] == "verified"


# Synthetic integration fixture, not a participant printed in the paper.
VALID = [
    ("fatigue_response_code", "5", "score"),
    ("resistance_difficulty_binary", "0", "1"),
    ("ambulation_difficulty_binary", "0", "1"),
    ("illnesses_count", "5", "1"),
    ("weight_current_kg", "80", "kg"),
    ("weight_year_ago_kg", "80", "kg"),
]


def run_report(tmp_path, rows=VALID, extra=()):
    measurements = tmp_path / "measurements.csv"
    measurements.write_text("marker,value,unit\n" + "\n".join(",".join(row) for row in rows) + "\n")
    out = tmp_path / "out"
    run = subprocess.run(
        [sys.executable, str(ROOT / "scripts/personal_report.py"),
         "--measurements", str(measurements), "--out", str(out), *extra],
        capture_output=True, text=True,
    )
    return run, out


def test_result_json_and_chinese_report(tmp_path):
    run, out = run_report(tmp_path)
    assert run.returncode == 0, run.stderr
    outputs = json.loads((out / "result.json").read_text())["outputs"]
    assert outputs["illnesses_score"]["value"] == 1  # Appendix 1: count 5 -> 1
    assert outputs["frail_total_score"]["value"] == 1
    assert outputs["frail_category"]["value"] == "prefrail"
    assert outputs["weight_loss_pct"]["value"] == 0
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "边界:" in report
    assert "至少 5%" in report
    assert not (out / "problems.json").exists()


@pytest.mark.parametrize("key,value,unit", [
    ("weight_current_kg", "80", "mg/dL"),
    ("weight_year_ago_kg", "0", "kg"),
    ("illnesses_count", "12", "1"),
    ("illnesses_count", "4.5", "1"),
    ("fatigue_response_code", "0", "score"),
    ("resistance_difficulty_binary", "0.5", "1"),
    ("weight_current_kg", "nan", "kg"),
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


def test_missing_input_exits_three(tmp_path):
    run, out = run_report(tmp_path, VALID[:-1])
    assert run.returncode == 3
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert any(p["key"] == "weight_year_ago_kg" and p["kind"] == "missing" for p in problems)


def test_wrong_optional_age_exits_three(tmp_path):
    run, out = run_report(tmp_path, extra=("--age", "unknown"))
    assert run.returncode == 3
    assert (out / "problems.json").exists()


def test_aliases_and_exact_pound_conversion(tmp_path):
    # Equal weights stay equal under the exact international-pound conversion.
    rows = [
        ("疲劳频度", "5", "score"), ("Resistance", "0", "1"),
        ("Ambulation", "0", "1"), ("疾病种数", "5", "1"),
        ("Current weight", "200", "lb"), ("Weight 1 year ago", "200", "lb"),
    ]
    run, out = run_report(tmp_path, rows)
    assert run.returncode == 0, run.stderr
    outputs = json.loads((out / "result.json").read_text())["outputs"]
    assert outputs["weight_loss_pct"]["value"] == 0
    assert outputs["frail_total_score"]["value"] == 1


def test_stale_outputs_cleared_between_runs(tmp_path):
    assert run_report(tmp_path)[0].returncode == 0
    run, out = run_report(tmp_path, VALID[:-1])
    assert run.returncode == 3 and not (out / "result.json").exists()
    run, out = run_report(tmp_path)
    assert run.returncode == 0 and not (out / "problems.json").exists()
