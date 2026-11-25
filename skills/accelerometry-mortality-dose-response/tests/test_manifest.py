"""Expected values are printed in Supplementary Table 5, PDF page 7."""

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as report
from presets import MEASURES, BOUNDARY


def test_printed_sedentary_examples():
    # Sedentary (h/d), HR (95% CI): 10 1.48 (1.22, 1.79);
    # 12 2.92 (2.24, 3.82). The main text says 3.83; use Table 5.
    for dose, hr, lo, hi in [(10, 1.48, 1.22, 1.79), (12, 2.92, 2.24, 3.82)]:
        result = report.lookup("sedentary_h_day", dose)
        assert result["hr"] == hr
        assert result["ci_low"] == lo
        assert result["ci_high"] == hi
        assert result["lower"]["dose"] == result["upper"]["dose"] == dose


@pytest.mark.parametrize("key,dose,hr,lo,hi", [
    ("total_activity_cpm", 300, 0.34, 0.27, 0.43),
    ("light_min_day", 375, 0.48, 0.38, 0.63),
    ("low_light_min_day", 325, 0.45, 0.34, 0.60),
    ("high_light_min_day", 80, 0.40, 0.31, 0.52),
    ("mvpa_min_day", 24, 0.39, 0.26, 0.59),
])
def test_printed_activity_examples(key, dose, hr, lo, hi):
    result = report.lookup(key, dose)
    assert (result["hr"], result["ci_low"], result["ci_high"]) == (hr, lo, hi)


def run_cli(tmp_path, rows, targets=None, extra=None):
    path = tmp_path / "measurements.csv"
    with path.open("w") as f:
        writer = csv.writer(f)
        writer.writerow(["marker", "value", "unit"])
        writer.writerows(rows)
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(path), "--age", "62", "--device", "actigraph",
            "--protocol", "vertical-60s-harmonised", "--out", str(out)]
    if targets is not None:
        p = tmp_path / "targets.csv"
        with p.open("w") as f:
            writer = csv.writer(f)
            writer.writerow(["marker", "value", "unit"])
            writer.writerows(targets)
        args += ["--targets", str(p)]
    args += extra or []
    process = subprocess.run(args, capture_output=True, text=True)
    return process, out


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / "skill.json").read_text())
    specs = {s["key"]: s for s in manifest["inputs"] if s["from"] == "measurements"}
    assert set(specs) == set(MEASURES)
    for key, spec in specs.items():
        assert spec["unit"] == MEASURES[key]["unit"]
        assert spec["range"] == MEASURES[key]["range"]
    assert manifest["inputs_status"] == "verified"


def test_cli_printed_example_and_conversion(tmp_path):
    process, out = run_cli(tmp_path, [("久坐时间", 600, "min")])
    assert process.returncode == 0, process.stderr
    values = json.loads((out / "result.json").read_text())["outputs"]
    assert values["exposure"]["value"] == 10
    assert values["hazard_ratio"]["value"] == 1.48
    assert values["ci_low"]["value"] == 1.22
    assert values["ci_high"]["value"] == 1.79
    text = (out / "report.md").read_text()
    assert text.index("## 论文卡片") < text.index("## 你的查表结果")
    assert BOUNDARY in text


@pytest.mark.parametrize("rows,extra", [
    ([("久坐时间", 10, "kg")], []),
    ([("久坐时间", 25, "h")], []),
    ([("久坐时间", 10, "")], []),
    ([("久坐时间", "nan", "h")], []),
    ([], []),
    ([("steps", 5000, "1")], []),
    ([("久坐时间", 10, "h"), ("MVPA", 24, "min")], []),
    ([("久坐时间", 10, "h")], ["--device", "wrist"]),
    ([("久坐时间", 10, "h")], ["--device", "actical"]),
    ([("久坐时间", 10, "h")], ["--protocol", "unknown"]),
    ([("久坐时间", 10, "h")], ["--age", "39"]),
    ([("久坐时间", 10, "h")], ["--age", "bad"]),
])
def test_invalid_inputs_stop_without_results(tmp_path, rows, extra):
    process, out = run_cli(tmp_path, rows, extra=extra)
    assert process.returncode == 3, process.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    text = (out / "report.md").read_text()
    assert "## 论文卡片" in text and BOUNDARY in text
    assert "HR =" not in text


def test_bracket_uses_printed_rows_without_interpolation(tmp_path):
    process, out = run_cli(tmp_path, [("sedentary_h_day", 9.75, "h")])
    assert process.returncode == 0, process.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["hazard_ratio"]["value"] is None
    assert result["lower_dose"]["value"] == 9.5
    assert result["lower_hr"]["value"] == 1.28
    assert result["upper_dose"]["value"] == 10
    assert result["upper_hr"]["value"] == 1.48


def test_targets_compare_printed_points(tmp_path):
    process, out = run_cli(tmp_path, [("久坐时间", 12, "h")], [("久坐时间", 600, "min")])
    assert process.returncode == 0, process.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert levers["current"]["hr"] == 2.92
    assert levers["targets"]["hr"] == 1.48
    assert levers["levers"][0]["hr_delta"] == pytest.approx(1.48 - 2.92)
    assert levers["sensitivity"][0]["hr_per_unit"] is None


@pytest.mark.parametrize("targets", [[], [("久坐时间", 9, "kg")], [("MVPA", 24, "min")], [("unknown", 10, "h")]])
def test_bad_targets_fail_atomically(tmp_path, targets):
    process, out = run_cli(tmp_path, [("久坐时间", 12, "h")], targets)
    assert process.returncode == 3, process.stderr
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()


def test_reference_has_no_invented_ci_and_no_extrapolation():
    for key, dose in [("total_activity_cpm", 140), ("light_min_day", 200),
                      ("low_light_min_day", 158), ("high_light_min_day", 28),
                      ("mvpa_min_day", 0), ("sedentary_h_day", 7.5)]:
        result = report.lookup(key, dose)
        assert result["hr"] == 1
        assert result["ci_low"] is None and result["ci_high"] is None
    with pytest.raises(ValueError):
        report.lookup("mvpa_min_day", 25)


def test_failure_removes_stale_success(tmp_path):
    process, out = run_cli(tmp_path, [("久坐时间", 10, "h")])
    assert process.returncode == 0
    process, out = run_cli(tmp_path, [("久坐时间", 10, "kg")])
    assert process.returncode == 3
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
