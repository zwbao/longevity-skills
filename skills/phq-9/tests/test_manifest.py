"""Table 2 printed score-to-severity intervals, written before implementation.

Minimal, 0–4
Mild, 5–9
Moderate, 10–14
Moderately severe, 15–19
Severe, 20–27

These are printed lookup examples, not a printed patient's nine answers.
"""

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_table_2_printed_severity_intervals():
    from personal_report import classify

    for low, high, category in [
        (0, 4, "minimal"), (5, 9, "mild"), (10, 14, "moderate"),
        (15, 19, "moderately_severe"), (20, 27, "severe"),
    ]:
        for total in range(low, high + 1):
            assert classify(total) == category


def test_manifest_matches_presets():
    from presets import ITEM_KEYS, ITEM_RANGE

    m = json.loads((ROOT / "skill.json").read_text())
    specs = [s for s in m["inputs"] if s["from"] == "measurements"]
    assert [s["key"] for s in specs] == list(ITEM_KEYS)
    assert all(s["unit"] == "score" and s["range"] == list(ITEM_RANGE) for s in specs)


def run_report(tmp_path, scores=None, rows=None, extra=()):
    # Synthetic integration fixture, not a patient printed in the paper.
    if rows is None:
        scores = scores if scores is not None else [0] * 9
        rows = [(f"phq9_q{i}_score", str(v), "score") for i, v in enumerate(scores, 1)]
    source = tmp_path / "answers.csv"
    source.write_text("marker,value,unit\n" + "\n".join(",".join(r) for r in rows) + "\n")
    out = tmp_path / "out"
    run = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                          "--measurements", str(source), "--out", str(out), *extra],
                         capture_output=True, text=True)
    return run, out


def test_result_and_report(tmp_path):
    run, out = run_report(tmp_path)
    assert run.returncode == 0, run.stderr
    results = json.loads((out / "result.json").read_text())["outputs"]
    assert results["phq9_total_score"]["value"] == 0
    assert results["phq9_severity"]["value"] == "minimal"
    assert results["item9_followup_needed"]["value"] == 0
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "边界:" in report and "过去两周" in report


@pytest.mark.parametrize("value,unit", [("4", "score"), ("-1", "score"),
                         ("1.5", "score"), ("2", "mg/dL"), ("nan", "score")])
def test_invalid_input_exits_three(tmp_path, value, unit):
    rows = [(f"phq9_q{i}_score", "0", "score") for i in range(1, 10)]
    rows[0] = (rows[0][0], value, unit)
    run, out = run_report(tmp_path, rows=rows)
    assert run.returncode == 3, run.stderr
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()
    report = (out / "report.md").read_text()
    assert "## 你的结果" not in report
    assert "## 论文卡片" in report and "边界:" in report


def test_missing_and_stale_result(tmp_path):
    assert run_report(tmp_path)[0].returncode == 0
    run, out = run_report(tmp_path, scores=[0] * 8)
    assert run.returncode == 3
    assert not (out / "result.json").exists()
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert any(p["key"] == "phq9_q9_score" and p["kind"] == "missing" for p in problems)


@pytest.mark.parametrize("q9", [1, 2, 3])
def test_item9_support_even_when_total_low(tmp_path, q9):
    run, out = run_report(tmp_path, scores=[0] * 8 + [q9])
    assert run.returncode == 0, run.stderr
    results = json.loads((out / "result.json").read_text())["outputs"]
    assert results["item9_followup_needed"]["value"] == 1
    report = (out / "report.md").read_text()
    assert report.index("## 先关注安全与支持") < report.index("## 你的结果")
    assert "急救" in report and "可信任" in report


def test_item9_support_survives_other_input_problem(tmp_path):
    rows = [(f"phq9_q{i}_score", "0", "score") for i in range(2, 9)]
    rows.append(("phq9_q9_score", "1", "score"))
    run, out = run_report(tmp_path, rows=rows)
    assert run.returncode == 3
    assert "## 先关注安全与支持" in (out / "report.md").read_text()


def test_upper_total_and_aliases(tmp_path):
    rows = [(f"PHQ-9 item {i}", "3", "score") for i in range(1, 10)]
    run, out = run_report(tmp_path, rows=rows)
    assert run.returncode == 0, run.stderr
    results = json.loads((out / "result.json").read_text())["outputs"]
    assert results["phq9_total_score"]["value"] == 27
    assert results["phq9_severity"]["value"] == "severe"


@pytest.mark.parametrize("extra", [("--age", "nan"), ("--age", "17"), ("--sex", "bad")])
def test_invalid_profile(tmp_path, extra):
    assert run_report(tmp_path, extra=extra)[0].returncode == 3
