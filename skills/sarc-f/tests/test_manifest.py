"""The first test reproduces the printed falls item, before implementation.

Source: Malmstrom et al., 2016, Methods, SARC-F questionnaire (0–10 points).
The manifest preserves the verbatim excerpt; four falls in the past year
is explicitly assigned 2 points. No participant-level example is claimed.
"""

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_printed_falls_per_term_score():
    from personal_report import falls_points

    assert falls_points(4) == 2


@pytest.mark.parametrize("count,expected", [(0, 0), (1, 1), (3, 1)])
def test_remaining_printed_falls_scores(count, expected):
    from personal_report import falls_points

    # Other count-to-point rules explicitly printed in the same paragraph.
    assert falls_points(count) == expected


def test_manifest_matches_presets():
    from presets import MEASUREMENTS

    manifest = json.loads((ROOT / "skill.json").read_text())
    actual = {s["key"]: (s["unit"], tuple(s["range"]))
              for s in manifest["inputs"] if s["from"] == "measurements"}
    assert actual == MEASUREMENTS
    assert manifest["validation"]["status"] == "reproduced"


# Integration fixture uses the printed best responses (all zero), not a patient.
VALID = [("strength_response_score", "0", "score"),
         ("walking_response_score", "0", "score"),
         ("chair_response_score", "0", "score"),
         ("stairs_response_score", "0", "score"),
         ("falls_past_year_count", "0", "1")]


def run_report(tmp_path, rows=VALID, extra=()):
    path = tmp_path / "measurements.csv"
    path.write_text("marker,value,unit\n" + "\n".join(",".join(r) for r in rows) + "\n")
    out = tmp_path / "out"
    run = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                          "--measurements", str(path), "--out", str(out), *extra],
                         capture_output=True, text=True)
    return run, out


def test_result_and_report(tmp_path):
    run, out = run_report(tmp_path)
    assert run.returncode == 0, run.stderr
    results = json.loads((out / "result.json").read_text())["outputs"]
    # Methods prints 0 as the best total and 0–3 as the lower category.
    assert results["sarc_f_total_score"]["value"] == 0
    assert results["sarc_f_category"]["value"] == "screen_negative"
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "边界:" in report and "不能排除" in report


@pytest.mark.parametrize("total,expected", [(0, "screen_negative"),
    (3, "screen_negative"), (4, "screen_positive"), (10, "screen_positive")])
def test_printed_category_boundaries(total, expected):
    from personal_report import classify

    assert classify(total) == expected


def test_printed_worst_total_via_cli(tmp_path):
    rows = [(k, "2", u) for k, _, u in VALID[:-1]] + [(VALID[-1][0], "4", "1")]
    run, out = run_report(tmp_path, rows)
    assert run.returncode == 0, run.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    # Methods explicitly gives 0–2 for each component and 10 as the worst total.
    assert result["sarc_f_total_score"]["value"] == 10
    assert result["falls_score"]["value"] == 2
    assert result["sarc_f_category"]["value"] == "screen_positive"


@pytest.mark.parametrize("key,value,unit", [
    ("strength_response_score", "1", "kg"),
    ("walking_response_score", "3", "score"),
    ("chair_response_score", "0.5", "score"),
    ("stairs_response_score", "nan", "score"),
    ("falls_past_year_count", "-1", "1"),
    ("falls_past_year_count", "1.5", "1"),
    ("falls_past_year_count", "2", "score"),
])
def test_invalid_inputs_exit_three(tmp_path, key, value, unit):
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
    aliases = ["Strength", "室内步行困难", "Rise from a chair", "Climb stairs", "过去一年跌倒次数"]
    run, out = run_report(tmp_path, [(a, v, u) for a, (_, v, u) in zip(aliases, VALID)])
    assert run.returncode == 0, run.stderr
    assert json.loads((out / "result.json").read_text())["outputs"]["sarc_f_total_score"]["value"] == 0


@pytest.mark.parametrize("extra", [("--age", "nan"), ("--sex", "bad")])
def test_invalid_context(tmp_path, extra):
    assert run_report(tmp_path, extra=extra)[0].returncode == 3
