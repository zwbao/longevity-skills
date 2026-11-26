"""Paper-first test: Table 2, p.302, Post, Patient M (SD).

Initial 1.0 (1.0)
Middle 1.4 (0.9)
Terminal 1.4 (1.1)
Satisfaction 1.8 (1.1)
Interference 1.1 (0.9)
Noticeability 0.9 (0.9)
Distress 1.3 (1.2)
Total 8.9 (5.0)

This checks the additive rule on published group means, not an individual.
"""

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_table_2_post_patient_total():
    from personal_report import sum_scores

    # Printed means, in the paper's row order. SDs are not added.
    assert sum_scores([1.0, 1.4, 1.4, 1.8, 1.1, 0.9, 1.3]) == pytest.approx(8.9, abs=1e-12)


def test_manifest_matches_presets():
    from presets import MEASUREMENTS

    manifest = json.loads((ROOT / "skill.json").read_text())
    assert {s["key"]: (s["unit"], tuple(s["range"]))
            for s in manifest["inputs"] if s["from"] == "measurements"} == MEASUREMENTS
    assert manifest["inputs_status"] == "verified"


@pytest.mark.parametrize("low,high,category", [
    (0, 7, "no_clinically_significant_insomnia"),
    (8, 14, "subthreshold_insomnia"),
    (15, 21, "moderate_insomnia"),
    (22, 28, "severe_insomnia"),
])
def test_figure_1_bands(low, high, category):
    from personal_report import classify

    for total in range(low, high + 1):
        assert classify(total) == category


KEYS = ["sleep_onset_score", "sleep_maintenance_score", "early_awakening_score",
        "sleep_dissatisfaction_score", "daily_interference_score",
        "noticeability_score", "sleep_distress_score"]
# Synthetic software fixture, not a published participant.
VALID = [(k, "2", "score") for k in KEYS]


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
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["isi_total_score"]["value"] == 14
    assert result["isi_category"]["value"] == "subthreshold_insomnia"
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "边界:" in report and "过去两周" in report


@pytest.mark.parametrize("value,unit", [
    ("2", "h"), ("5", "score"), ("-1", "score"),
    ("1.5", "score"), ("nan", "score"), ("inf", "score"), ("不清楚", "score"),
])
def test_invalid_inputs_exit_three(tmp_path, value, unit):
    run, out = run_report(tmp_path, [(KEYS[0], value, unit), *VALID[1:]])
    assert run.returncode == 3, run.stderr
    assert (out / "problems.json").exists() and not (out / "result.json").exists()
    report = (out / "report.md").read_text()
    assert "## 论文卡片" in report and "边界:" in report
    assert "## 你的结果" not in report


def test_missing_item(tmp_path):
    run, out = run_report(tmp_path, VALID[:-1])
    assert run.returncode == 3
    assert any(p["key"] == KEYS[-1] and p["kind"] == "missing"
               for p in json.loads((out / "problems.json").read_text())["problems"])


def test_aliases_and_satisfaction_direction(tmp_path):
    names = ["入睡困难", "Difficulty staying asleep", "早醒", "Satisfaction",
             "日间功能干扰", "Noticeability", "Distress"]
    rows = [(name, "4" if i == 3 else "0", "score") for i, name in enumerate(names)]
    run, out = run_report(tmp_path, rows)
    assert run.returncode == 0, run.stderr
    assert json.loads((out / "result.json").read_text())["outputs"]["isi_total_score"]["value"] == 4


@pytest.mark.parametrize("extra", [("--age", "unknown"), ("--age", "-1"), ("--sex", "invalid")])
def test_invalid_context(tmp_path, extra):
    run, out = run_report(tmp_path, extra=extra)
    assert run.returncode == 3
    assert (out / "problems.json").exists()


def test_stale_output_cleanup(tmp_path):
    assert run_report(tmp_path)[0].returncode == 0
    run, out = run_report(tmp_path, VALID[:-1])
    assert run.returncode == 3 and not (out / "result.json").exists()
    run, out = run_report(tmp_path)
    assert run.returncode == 0 and not (out / "problems.json").exists()
