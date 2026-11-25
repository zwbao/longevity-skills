"""Printed preprocessing check plus software checks, not a published risk example.

Table S1 prints HbA1c means 5.58%, 6.13% and 37.5, 43.5 mmol/mol.
Section 2.1's affine conversion reproduces them within rounding. No table
prints a Model A probability for a complete set of individual inputs.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as report
import presets

MANIFEST = json.loads((ROOT / "skill.json").read_text())


def test_printed_hba1c_mean_conversion():
    # 0.005% rounding gives 0.054645 mmol/mol uncertainty, plus 0.05
    # from rounding the printed mmol/mol mean: absolute tolerance 0.105.
    assert report.to_ifcc(5.58) == pytest.approx(37.5, abs=0.105)
    assert report.to_ifcc(6.13) == pytest.approx(43.5, abs=0.105)


def run(tmp_path, rows="HbA1c,5.58,%\n", extra=(), age="67.71", sex="female"):
    path = tmp_path / "measurements.csv"
    path.write_text("marker,value,unit\n" + rows)
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(path), "--age", age, "--sex", sex,
            "--years-next", "4", "--eligible-baseline", "1",
            "--out", str(tmp_path / "out"), *extra]
    return subprocess.run(args, capture_output=True, text=True)


def test_manifest_and_printed_s4_constants():
    # Independent transcription of Model A, Table S4, p.32.
    assert presets.INTERCEPT == -4.053
    assert presets.MODEL == {
        "hba1c_ifcc": (38.74, 3.47, 1.469),
        "age": (67.71, 7.30, -0.147),
        "female": (0.57, 0.50, -0.067),
        "log_years_next": (1.56, 0.26, 0.507),
    }
    specs = {x["key"]: x for x in MANIFEST["inputs"]}
    assert {k: specs[k]["unit"] for k in presets.INPUT_UNITS} == presets.INPUT_UNITS
    assert MANIFEST["validation"]["status"] == "draft"
    assert MANIFEST["validation"]["gap_zh"].startswith("预印本，未经同行评审")


def test_result_matches_printed_equation(tmp_path):
    # This is an analytical software oracle from S2/S4, NOT a printed
    # patient prediction or evidence of scientific reproduction.
    proc = run(tmp_path)
    assert proc.returncode == 0, proc.stderr
    eta = (-4.053 + 1.469 * ((5.58 - 2.15) * 10.929 - 38.74) / 3.47
           - 0.067 * (1 - 0.57) / 0.50 + 0.507 * (math.log(4) - 1.56) / 0.26)
    output = json.loads((tmp_path / "out/result.json").read_text())["outputs"]
    assert output["diabetes_probability_pct"]["value"] == pytest.approx(100 / (1 + math.exp(-eta)))
    assert output["linear_predictor"]["value"] == pytest.approx(eta)
    text = (tmp_path / "out/report.md").read_text()
    assert text.index("论文卡片") < text.index("## 本次计算")
    assert "预印本，未经同行评审" in text and "边界:" in text
    assert "4 年" in text and "并非干预效果" in text


@pytest.mark.parametrize("rows,extra,age,sex", [
    ("HbA1c,5.58,mg/dL\n", (), "67", "female"),
    ("HbA1c,40,%\n", (), "67", "female"),
    ("HbA1c,40,mmol/mol\n", (), "67", "female"),
    ("HbA1c,5.58,\n", (), "67", "female"),
    ("", (), "67", "female"),
    ("HbA1c,nan,%\n", (), "67", "female"),
    ("HbA1c,5.58,%\n", (), "nan", "female"),
    ("HbA1c,5.58,%\n", (), "67", "unknown"),
    ("HbA1c,5.58,%\n", ("--years-next", "0"), "67", "female"),
    ("HbA1c,5.58,%\n", ("--eligible-baseline", "0"), "67", "female"),
    ("HbA1c,5.58,%\n", ("--eligible-baseline", "0.5"), "67", "female"),
    ("HbA1c,6.5,%\n", (), "67", "female"),
    ("HbA1c,5.58,%\n", (), "40", "female"),
])
def test_bad_inputs_exit_three_without_prediction(tmp_path, rows, extra, age, sex):
    proc = run(tmp_path, rows, extra, age, sex)
    assert proc.returncode == 3, proc.stderr
    assert (tmp_path / "out/problems.json").exists()
    assert not (tmp_path / "out/levers.json").exists()
    result = json.loads((tmp_path / "out/result.json").read_text())
    assert all(v["value"] is None for v in result["outputs"].values())
    text = (tmp_path / "out/report.md").read_text()
    assert "论文卡片" in text and "边界:" in text
    assert "模型概率为" not in text


def test_missing_arguments_are_structured(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                           "--out", str(tmp_path / "out")], capture_output=True, text=True)
    assert proc.returncode == 3
    problems = json.loads((tmp_path / "out/problems.json").read_text())["problems"]
    assert {"hba1c_pct", "age", "sex", "years_next", "eligible_baseline"} <= {p["key"] for p in problems}


def test_targets_and_analytic_sensitivity(tmp_path):
    target = tmp_path / "targets.csv"
    target.write_text("marker,value,unit\n糖化血红蛋白,5.4,%\n")
    assert run(tmp_path, extra=("--targets", str(target))).returncode == 0
    payload = json.loads((tmp_path / "out/levers.json").read_text())
    assert payload["schema"] == "longevity-levers/1"
    assert payload["targets"]["diabetes_probability_pct"] < payload["current"]["diabetes_probability_pct"]
    p = payload["current"]["diabetes_probability_pct"] / 100
    slopes = {r["key"]: r for r in payload["sensitivity"]}
    assert slopes["hba1c_pct"]["probability_pct_per_unit"] == pytest.approx(100 * p * (1-p) * 1.469 / 3.47 * 10.929)
    assert set(slopes) == {"hba1c_pct", "age", "sex", "years_next"}
    assert payload["levers"][0]["diabetes_probability_pct_delta"] == pytest.approx(
        payload["targets"]["diabetes_probability_pct"] - payload["current"]["diabetes_probability_pct"])


@pytest.mark.parametrize("row", ["age,60,a", "unknown,1,1", "HbA1c,6.5,%", "HbA1c,40,mmol/mol"])
def test_invalid_targets_cannot_be_silently_ignored(tmp_path, row):
    target = tmp_path / "targets.csv"
    target.write_text("marker,value,unit\n" + row + "\n")
    assert run(tmp_path, extra=("--targets", str(target))).returncode == 3
    assert not (tmp_path / "out/levers.json").exists()


def test_reused_output_clears_stale_results(tmp_path):
    assert run(tmp_path).returncode == 0
    assert run(tmp_path, rows="HbA1c,40,%\n").returncode == 3
    assert not (tmp_path / "out/levers.json").exists()
    assert run(tmp_path).returncode == 0
    assert not (tmp_path / "out/problems.json").exists()
