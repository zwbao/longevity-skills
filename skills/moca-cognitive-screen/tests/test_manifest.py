"""Reproduce the printed item maxima and total; additional cases test rules only."""
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import presets

# Nasreddine et al. 2005, p. 697, Montreal Cognitive Assessment paragraph.
# These are printed per-task maxima, not a fabricated participant record.
PRINTED_MAXIMA = {
    "delayed_recall_score": 5, "clock_drawing_score": 3,
    "cube_copy_score": 1, "alternation_score": 1,
    "phonemic_fluency_score": 1, "abstraction_score": 2,
    "sustained_attention_score": 1, "serial_subtraction_score": 3,
    "digits_forward_score": 1, "digits_backward_score": 1,
    "naming_score": 3, "sentence_repetition_score": 2,
    "orientation_score": 6,
}


def run_report(tmp_path, overrides=None, omit=(), extra=()):
    rows = {key: (value, "score") for key, value in PRINTED_MAXIMA.items()}
    # p. 697: education <=12 adds a point only if the total is <30.
    rows["education_years"] = (12, "a")
    rows.update(overrides or {})
    source = tmp_path / "assessment.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["item", "value", "unit"])
        writer.writerows((key, *value) for key, value in rows.items() if key not in omit)
        writer.writerows(extra)
    out = tmp_path / "out"
    process = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                              "--measurements", str(source), "--out", str(out)],
                             capture_output=True, text=True)
    result = json.loads((out / "result.json").read_text())["outputs"]
    report = (out / "report.md").read_text()
    return process, result, report, out


def test_printed_task_maxima_sum_to_30(tmp_path):
    # p. 697 prints all 13 task maxima above and describes a 30-point test.
    # It does not print an individual patient's item vector: validation covers
    # the published scoring structure, not diagnosis or cohort sensitivity.
    process, result, report, _ = run_report(tmp_path)
    assert process.returncode == 0, process.stderr
    assert result["raw_score"]["value"] == 30
    assert result["adjusted_score"]["value"] == 30
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert presets.BOUNDARY in report


@pytest.mark.parametrize("recall,education,bonus,total,category", [
    (0, 12, 1, 26, "未低于原文筛查切点"),
    (0, 13, 0, 25, "低于原文筛查切点"),
    (4, 12, 1, 30, "未低于原文筛查切点"),
    (5, 12, 0, 30, "未低于原文筛查切点"),
])
def test_education_and_cutoff_rules(tmp_path, recall, education, bonus, total, category):
    # Synthetic boundary cases from the explicit p. 697-698 rules. These are
    # not claimed as printed patient examples in the validation manifest.
    process, result, _, _ = run_report(tmp_path, {
        "delayed_recall_score": (recall, "score"), "education_years": (education, "a")})
    assert process.returncode == 0, process.stderr
    assert result["education_bonus"]["value"] == bonus
    assert result["adjusted_score"]["value"] == total
    assert result["screening_category"]["value"] == category


@pytest.mark.parametrize("overrides,omit,extra,kind", [
    ({"naming_score": (3, "mg/L")}, (), (), "unit"),
    ({"naming_score": (4, "score")}, (), (), "range"),
    ({"naming_score": (1.5, "score")}, (), (), "integer"),
    ({"naming_score": ("NaN", "score")}, (), (), "parse"),
    ({}, ("education_years",), (), "missing"),
    ({}, ("delayed_recall_score",), (), "missing"),
    ({}, (), (("MoCA总分", 30, "score"),), "unknown"),
    ({}, (), (("naming_score", 2, "score"),), "duplicate"),
])
def test_invalid_inputs_stop(tmp_path, overrides, omit, extra, kind):
    process, result, report, out = run_report(tmp_path, overrides, omit, extra)
    assert process.returncode == 3, process.stderr
    assert all(item["value"] is None for item in result.values())
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert kind in {p["kind"] for p in problems}
    assert "## 你的结果" not in report
    assert "## 论文卡片" in report and presets.BOUNDARY in report


def test_stale_outputs_are_replaced(tmp_path):
    run_report(tmp_path)
    _, result, _, out = run_report(tmp_path, omit=("naming_score",))
    assert all(item["value"] is None for item in result.values())
    assert (out / "problems.json").exists()
    process, _, _, out = run_report(tmp_path)
    assert process.returncode == 0
    assert not (out / "problems.json").exists()


def test_manifest_matches_printed_limits():
    manifest = json.loads((ROOT / "skill.json").read_text())
    assert presets.TASK_MAXIMA == PRINTED_MAXIMA
    assert {i["key"] for i in manifest["inputs"]} == set(PRINTED_MAXIMA) | {"education_years"}
    for item in manifest["inputs"]:
        assert item["required"] and item["from"] == "measurements"
        assert item["accept"] == {}
        if item["key"] == "education_years":
            assert item["unit"] == "a"
            assert item["range"] == list(presets.EDUCATION_RANGE)
        else:
            assert item["unit"] == presets.SCORE_UNIT == "score"
            assert item["range"] == [0, PRINTED_MAXIMA[item["key"]]]
