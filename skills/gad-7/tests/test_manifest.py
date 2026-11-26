"""Paper-printed per-item scores, then integration and input-contract checks.

Figure 1, p1094, first row (same four cells in all seven rows):
1. Feeling nervous, anxious or on edge 0 1 2 3
The four response columns are not at all, several days, more than half the
days, nearly every day. These are per-term examples, not an observed patient.
"""

import csv
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
KEYS = [f"gad7_item_{i}_score" for i in range(1, 8)]


def run_report(tmp_path, rows, extra=()):
    path = tmp_path / "answers.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["marker", "value", "unit"])
        writer.writerows(rows)
    out = tmp_path / "out"
    run = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                          "--measurements", str(path), "--out", str(out), *extra],
                         capture_output=True, text=True)
    return run, out


def test_figure_1_printed_per_term_scores(tmp_path):
    # Each column prints these scores in each of the seven symptom rows.
    # Test the complete input/report path, not just a copied constant dictionary.
    for printed_score in (0, 1, 2, 3):
        rows = [(key, printed_score, "score") for key in KEYS]
        run, out = run_report(tmp_path, rows)
        assert run.returncode == 0, run.stderr
        actual = json.loads((out / "result.json").read_text())["outputs"]
        for key in KEYS:
            assert actual[key]["value"] == printed_score


def test_printed_total_range_endpoints(tmp_path):
    # p1093 Item Selection: seven items each 0 to 3; total range 0 to 21.
    # Endpoint configurations, not individual participants from the study.
    for item_score, printed_total in ((0, 0), (3, 21)):
        run, out = run_report(tmp_path, [(k, item_score, "score") for k in KEYS])
        assert run.returncode == 0, run.stderr
        assert json.loads((out / "result.json").read_text())["outputs"]["gad7_total_score"]["value"] == printed_total


def test_table_3_printed_severity_intervals():
    from personal_report import classify

    # Table 3 p1096: Minimal 0-4; Mild 5-9; Moderate 10-14; Severe 15-21.
    for low, high, category in [(0, 4, "minimal"), (5, 9, "mild"),
                                 (10, 14, "moderate"), (15, 21, "severe")]:
        for total in range(low, high + 1):
            assert classify(total) == category


def test_manifest_matches_presets():
    from presets import MEASUREMENTS

    manifest = json.loads((ROOT / "skill.json").read_text())
    assert {s["key"]: (s["unit"], tuple(s["range"])) for s in manifest["inputs"]
            if s["from"] == "measurements"} == MEASUREMENTS
    assert manifest["validation"]["status"] == "reproduced"
    assert manifest["inputs_status"] == "verified"


# Synthetic integration arrangement: the expected cutpoint 10 is printed in
# Table 1 and the Comment, but this seven-answer pattern is not a paper case.
VALID = list(zip(KEYS, [3, 2, 1, 0, 1, 2, 1], ["score"] * 7))


def test_result_json_and_chinese_report(tmp_path):
    from presets import BOUNDARY

    run, out = run_report(tmp_path, VALID)
    assert run.returncode == 0, run.stderr
    values = json.loads((out / "result.json").read_text())["outputs"]
    assert values["gad7_total_score"]["value"] == 10
    assert values["anxiety_severity"]["value"] == "moderate"
    assert values["screening_threshold_status"]["value"] == "at_or_above_cutoff"
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "边界: " + BOUNDARY in report
    assert "过去两周" in report and "解释性翻译" in report
    assert not (out / "problems.json").exists()


@pytest.mark.parametrize("value,unit", [(1, "mg/L"), (4, "score"), (-1, "score"),
                                        (0.5, "score"), ("nan", "score"),
                                        ("inf", "score"), ("unknown", "score")])
def test_invalid_input_exits_three_without_result(tmp_path, value, unit):
    rows = [(KEYS[0], value, unit), *VALID[1:]]
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
    assert any(p["key"] == KEYS[-1] and p["kind"] == "missing" for p in problems)


def test_aliases(tmp_path):
    manifest = json.loads((ROOT / "skill.json").read_text())
    specs = [s for s in manifest["inputs"] if s["from"] == "measurements"]
    for selector in (lambda s: s["label_zh"], lambda s: s["aliases"][-1]):
        run, out = run_report(tmp_path, [(selector(s), 3, "score") for s in specs])
        assert run.returncode == 0, run.stderr
        assert json.loads((out / "result.json").read_text())["outputs"]["gad7_total_score"]["value"] == 21


def test_stale_outputs_cleared(tmp_path):
    assert run_report(tmp_path, VALID)[0].returncode == 0
    run, out = run_report(tmp_path, VALID[:-1])
    assert run.returncode == 3 and not (out / "result.json").exists()
    run, out = run_report(tmp_path, VALID)
    assert run.returncode == 0 and not (out / "problems.json").exists()


@pytest.mark.parametrize("extra", [("--age", "nan"), ("--age", "-1"), ("--sex", "invalid")])
def test_wrong_context_exits_three(tmp_path, extra):
    assert run_report(tmp_path, VALID, extra)[0].returncode == 3


def test_age_outside_study_warns_without_rescoring(tmp_path):
    run, out = run_report(tmp_path, VALID, ("--age", "96", "--sex", "female"))
    assert run.returncode == 0
    assert "不在本研究" in (out / "report.md").read_text()
    assert json.loads((out / "result.json").read_text())["outputs"]["gad7_total_score"]["value"] == 10
