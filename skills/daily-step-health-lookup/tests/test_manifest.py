"""Expected values are printed Table 2 cells, p e676, Ding et al. 2025.

These tests were written before the lookup implementation. Decimal middle dots
are represented as Python decimal points; no fitted model is being validated.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def run_report(tmp_path, value="7000", unit="1", age="50", targets=None):
    measurements = tmp_path / "measurements.csv"
    measurements.write_text(f"marker,value,unit\n日均步数,{value},{unit}\n")
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(measurements), "--out", str(out)]
    if age is not None:
        args += ["--age", age]
    if targets is not None:
        path = tmp_path / "targets.csv"
        path.write_text(targets)
        args += ["--targets", str(path)]
    completed = subprocess.run(args, text=True, capture_output=True)
    return completed, out


def values(out):
    return {key: obj["value"] for key, obj in json.loads((out / "result.json").read_text())["outputs"].items()}


def test_table2_7000_all_outcomes(tmp_path):
    # Table 2, Steps per day = 7000; reference 2000. EXACT table values,
    # including diabetes upper CI 1.00 (the abstract instead prints 0.99).
    expected = {
        "all_cause_mortality": (0.53, 0.46, 0.60),
        "cvd_incidence": (0.75, 0.67, 0.85),
        "cvd_mortality": (0.53, 0.37, 0.77),
        "cancer_incidence": (0.94, 0.87, 1.01),
        "cancer_mortality": (0.63, 0.55, 0.72),
        "diabetes_incidence": (0.86, 0.74, 1.00),
        "dementia": (0.62, 0.53, 0.73),
        "depressive_symptoms": (0.78, 0.73, 0.83),
        "falls": (0.72, 0.65, 0.81),
    }
    completed, out = run_report(tmp_path)
    assert completed.returncode == 0, completed.stderr
    result = values(out)
    assert result["reference_steps_per_day"] == 2000
    assert result["lower_steps_per_day"] == result["upper_steps_per_day"] == 7000
    for outcome, triple in expected.items():
        for side in ("lower", "upper"):
            assert tuple(result[f"{outcome}_{side}_{stat}"] for stat in ("hr", "ci_low", "ci_high")) == triple
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("你的步数")
    assert "边界：" in report
    assert "不是个人发病概率" in report
    assert "1.00" in report and "跨越或触及 1" in report


def test_table2_12000_printed_cells(tmp_path):
    # Table 2 p e676: CVD mortality 0·48 (0·33–0·71),
    # cancer mortality 0·50 (0·41–0·60), falls 0·78 (0·67–0·92).
    # PDF cells take priority over search-engine PDF transcriptions.
    completed, out = run_report(tmp_path, "12000")
    assert completed.returncode == 0
    result = values(out)
    for key, triple in {
        "cvd_mortality": (0.48, 0.33, 0.71),
        "cancer_mortality": (0.50, 0.41, 0.60),
        "falls": (0.78, 0.67, 0.92),
    }.items():
        assert tuple(result[f"{key}_lower_{stat}"] for stat in ("hr", "ci_low", "ci_high")) == triple


@pytest.mark.parametrize("value,unit,age", [
    ("7000", "km", "50"), ("12001", "1", "50"), ("1999", "1", "50"),
    ("", "1", "50"), ("nan", "1", "50"), ("abc", "1", "50"),
    ("7000", "1", "17"), ("7000", "1", None), ("7000", "1", "bad"),
])
def test_invalid_inputs_stop_without_readouts(tmp_path, value, unit, age):
    completed, out = run_report(tmp_path, value, unit, age)
    assert completed.returncode == 3, completed.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "levers.json").exists()
    assert all(value is None for value in values(out).values())
    report = (out / "report.md").read_text()
    assert "论文卡片" in report and "边界：" in report
    assert "0.53" not in report


def test_between_rows_is_not_an_interpolated_estimate(tmp_path):
    completed, out = run_report(tmp_path, "7500.5")
    assert completed.returncode == 0
    result = values(out)
    assert result["lookup_mode"] == "bracket"
    assert (result["lower_steps_per_day"], result["upper_steps_per_day"]) == (7000, 8000)
    # Table 2, all-cause mortality at 7000 and 8000 respectively.
    assert result["all_cause_mortality_lower_hr"] == 0.53
    assert result["all_cause_mortality_upper_hr"] == 0.52
    assert "不是你的置信区间" in (out / "report.md").read_text()


def test_reference_has_no_invented_confidence_interval(tmp_path):
    completed, out = run_report(tmp_path, "2000")
    assert completed.returncode == 0
    result = values(out)
    assert result["all_cause_mortality_lower_hr"] == 1
    assert result["all_cause_mortality_lower_ci_low"] is None
    assert result["all_cause_mortality_lower_ci_high"] is None


def test_targets_keep_same_reference_and_no_personal_risk_ratio(tmp_path):
    completed, out = run_report(tmp_path, targets="marker,value,unit\ndaily steps,10000,1\n")
    assert completed.returncode == 0, completed.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    assert levers["targets"]["outputs"]["all_cause_mortality_lower_hr"] == 0.52
    assert levers["current"]["all_cause_mortality_lower_hr"] == 0.53
    assert levers["levers"][0]["hr_delta"]["all_cause_mortality"] == pytest.approx(0.52 - 0.53)
    assert levers["sensitivity"][0]["derivative"] is None
    assert "不是目标相对当前的危险比" in levers["note_zh"]


def test_invalid_target_clears_stale_success_outputs(tmp_path):
    assert run_report(tmp_path)[0].returncode == 0
    completed, out = run_report(tmp_path, targets="marker,value,unit\ndaily steps,13000,1\n")
    assert completed.returncode == 3
    assert not (out / "levers.json").exists()
    assert all(value is None for value in values(out).values())


def test_manifest_matches_presets():
    sys.path.insert(0, str(ROOT / "scripts"))
    import presets
    manifest = json.loads((ROOT / "skill.json").read_text())
    declared = {item["key"]: item for item in manifest["inputs"]}
    assert declared["steps_per_day"]["unit"] == presets.STEP_UNIT
    assert declared["steps_per_day"]["range"] == [presets.STEP_MIN, presets.STEP_MAX]
    assert declared["age"]["range"] == [presets.ADULT_MIN, presets.AGE_MAX]
    assert {item["key"] for item in manifest["outputs"]} == set(presets.output_specs())
