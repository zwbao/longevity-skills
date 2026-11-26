"""Expected percentages are printed Table 2 cells, not generated outputs."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from personal_report import compute, levers
from presets import INPUT_UNITS, INPUT_RANGES
import skillkit

MANIFEST = json.loads((ROOT / "skill.json").read_text())


def test_table2_printed_examples():
    # Integer cells plus rounded log coefficients: 0.51 percentage points.
    # The 3.5 mmol/L, 40-year cell falls just past the half-point boundary.
    # Columns: baseline, absolute reduction, then 5, 10, 20, 30, 40 years.
    # Verbatim numeric cells: 7 | 3.5 | 58 | 68 | 81 | 89 | 93
    # Verbatim numeric cells: 3 | 0.5 | 12 | 15 | 21 | 27 | 32
    for reduction, printed in [(3.5, [58, 68, 81, 89, 93]),
                               (0.5, [12, 15, 21, 27, 32])]:
        for years, expected in zip([5, 10, 20, 30, 40], printed):
            actual = compute({"ldl_reduction_mmol_l": reduction,
                              "duration_years": years})
            assert actual["relative_risk_reduction_pct"] == pytest.approx(expected, abs=0.51)


def test_manifest_matches_presets():
    specs = {x["key"]: x for x in MANIFEST["inputs"]}
    assert {k: x["unit"] for k, x in specs.items()} == INPUT_UNITS
    assert {k: tuple(x["range"]) for k, x in specs.items()} == INPUT_RANGES


def run_cli(tmp_path, rows, targets=None):
    m = tmp_path / "measurements.csv"
    m.write_text("marker,value,unit\n" + rows, encoding="utf-8")
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(m), "--out", str(out)]
    if targets is not None:
        t = tmp_path / "targets.csv"
        t.write_text("marker,value,unit\n" + targets, encoding="utf-8")
        args += ["--targets", str(t)]
    return subprocess.run(args, capture_output=True, text=True), out


def test_result_report_and_targets(tmp_path):
    proc, out = run_cli(tmp_path, "LDL-C reduction,0.5,mmol/L\n持续年数,5,a\n",
                        "LDL-C reduction,3.5,mmol/L\n持续年数,40,a\n")
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["relative_risk_reduction_pct"]["value"] == pytest.approx(12, abs=0.51)
    ls = json.loads((out / "levers.json").read_text())
    assert ls["schema"] == "longevity-levers/1"
    assert ls["targets"]["relative_risk_reduction_pct"] == pytest.approx(93, abs=0.51)
    assert len(ls["sensitivity"]) == 2 and len(ls["levers"]) == 2
    assert ls["levers"][0]["relative_risk_reduction_pct"] == pytest.approx(58, abs=0.51)
    assert ls["levers"][1]["relative_risk_reduction_pct"] == pytest.approx(32, abs=0.51)
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("你的情景")
    assert "边界：" in report and "不能据此开始、停用或调整药物" in report
    assert "长期外推" in report


@pytest.mark.parametrize("rows", [
    "LDL-C reduction,1,kg\n持续年数,5,a\n",
    "LDL-C reduction,4,mmol/L\n持续年数,5,a\n",
    "LDL-C reduction,-1,mmol/L\n持续年数,5,a\n",
    "LDL-C reduction,1,mmol/L\n持续年数,4,a\n",
    "LDL-C reduction,1,mmol/L\n持续年数,41,a\n",
    "LDL-C reduction,1,mmol/L\n",
    "LDL-C reduction,nan,mmol/L\n持续年数,5,a\n",
    "LDL-C reduction,1,\n持续年数,5,a\n",
    "LDL-C,1,mmol/L\n持续年数,5,a\n",
])
def test_bad_input_exits_three_without_numbers(tmp_path, rows):
    proc, out = run_cli(tmp_path, rows)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    report = (out / "report.md").read_text()
    assert "这次没有计算" in report and "论文卡片" in report


def test_exact_molar_unit_conversion(tmp_path):
    proc, out = run_cli(tmp_path, "LDL-C reduction,500,umol/L\n持续年数,5,年\n")
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["relative_risk_reduction_pct"]["value"] == pytest.approx(12, abs=0.51)


def test_invalid_target_and_stale_outputs_are_removed(tmp_path):
    good = "LDL-C reduction,1,mmol/L\n持续年数,5,a\n"
    proc, out = run_cli(tmp_path, good)
    assert proc.returncode == 0
    proc, out = run_cli(tmp_path, good, "持续年数,60,a\n")
    assert proc.returncode == 3
    assert not (out / "result.json").exists() and not (out / "levers.json").exists()
    proc, out = run_cli(tmp_path, good)
    assert proc.returncode == 0 and not (out / "problems.json").exists()


def test_sensitivity_matches_finite_difference():
    values = {"ldl_reduction_mmol_l": 1.0, "duration_years": 20.0}
    for row in levers(values, {})["sensitivity"]:
        key, h = row["key"], 1e-5
        plus, minus = dict(values), dict(values)
        plus[key] += h
        minus[key] -= h
        slope = (compute(plus)["relative_risk_reduction_pct"] -
                 compute(minus)["relative_risk_reduction_pct"]) / (2*h)
        assert row["rrr_percentage_points_per_unit"] == pytest.approx(slope, rel=1e-7)


def test_missing_file_is_input_problem(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                           "--measurements", str(tmp_path / "absent.csv"),
                           "--out", str(tmp_path / "out")], capture_output=True)
    assert proc.returncode == 3
