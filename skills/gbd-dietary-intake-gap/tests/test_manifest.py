"""Printed examples first; intake fixtures are Table values, not patient data.

Lancet 2019 Table (p1960): whole grains 125 g/day, milk 435 g/day.
Results / Consumption of major foods and nutrients: whole grains 29 g/day
is 23% of optimum; milk 71 g/day is 16%. Percentages used unrounded data.
Half a percentage point is the precision of the printed integer percentages.
"""
import csv
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as report
from presets import FACTORS

MANIFEST = json.loads((ROOT / "skill.json").read_text())

# The complete Table, converted from mg to g only for EPA+DHA.
TABLE = {
    "fruits_g_d": (250, 200, 300),
    "vegetables_g_d": (360, 290, 430),
    "legumes_g_d": (60, 50, 70),
    "whole_grains_g_d": (125, 100, 150),
    "nuts_seeds_g_d": (21, 16, 25),
    "milk_g_d": (435, 350, 520),
    "red_meat_g_d": (23, 18, 27),
    "processed_meat_g_d": (2, 0, 4),
    "sugar_sweetened_beverages_g_d": (3, 0, 5),
    "fibre_g_d": (24, 19, 28),
    "calcium_g_d": (1.25, 1.00, 1.50),
    "seafood_omega3_g_d": (250 / 1000, 200 / 1000, 300 / 1000),
    "omega6_energy_pct": (11, 9, 13),
    "trans_fat_energy_pct": (0.5, 0.0, 1.0),
    "urinary_sodium_g_d": (3, 1, 5),
}


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["marker", "value", "unit"])
        writer.writerows(rows)


def rows():
    return [[key, values[0], "%" if key.endswith("_pct") else "g/d"]
            for key, values in TABLE.items()]


def run(tmp_path, data, targets=None, age="50"):
    source = tmp_path / "intake.csv"
    write_csv(source, data)
    out = tmp_path / "out"
    args = ["--measurements", str(source), "--age", age, "--out", str(out)]
    if targets is not None:
        target_file = tmp_path / "targets.csv"
        write_csv(target_file, targets)
        args += ["--targets", str(target_file)]
    process = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"), *args],
                             capture_output=True, text=True)
    return process, out


def test_printed_intake_percentages(tmp_path):
    data = rows()
    for row in data:
        if row[0] == "whole_grains_g_d":
            row[1] = 29
        elif row[0] == "milk_g_d":
            row[1] = 71
    process, out = run(tmp_path, data)
    assert process.returncode == 0, process.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert FACTORS["whole_grains_g_d"]["reference"] == 125
    assert FACTORS["milk_g_d"]["reference"] == 435
    assert result["whole_grains_ratio_pct"]["value"] == pytest.approx(23, abs=0.5)
    assert result["milk_ratio_pct"]["value"] == pytest.approx(16, abs=0.5)
    text = (out / "report.md").read_text()
    assert text.index("## 论文卡片") < text.index("## 你的摄入对照")
    assert text.rstrip().endswith("边界: " + report.BOUNDARY)


def test_manifest_table_units_and_outputs():
    inputs = {s["key"]: s for s in MANIFEST["inputs"] if s["from"] == "measurements"}
    assert inputs.keys() == FACTORS.keys() == TABLE.keys()
    for key, printed in TABLE.items():
        factor = FACTORS[key]
        assert (factor["reference"], *factor["reference_range"]) == printed
        assert factor["unit"] == inputs[key]["unit"]
    assert set(report.calculate({k: v[0] for k, v in TABLE.items()})) == {
        s["key"] for s in MANIFEST["outputs"]}


@pytest.mark.parametrize("change", ["unit", "range", "missing", "nan", "unknown", "salt"])
def test_bad_inputs_exit_three_and_clear_old_results(tmp_path, change):
    data = rows()
    process, out = run(tmp_path, data)
    assert process.returncode == 0
    if change == "unit":
        data[0][2] = "mg/dL"
    elif change == "range":
        data[0][1] = -1
    elif change == "missing":
        data.pop(0)
    elif change == "nan":
        data[0][1] = "nan"
    elif change == "unknown":
        data.append(["unrecognised_food", 1, "g/d"])
    else:
        data[-1][0] = "食盐"
    process, out = run(tmp_path, data)
    assert process.returncode == 3, process.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    text = (out / "report.md").read_text()
    assert "## 论文卡片" in text and "这次没有计算" in text
    assert "## 你的摄入对照" not in text


def test_targets_are_explicit_arithmetic_not_risk_predictions(tmp_path):
    data = rows()
    for row in data:
        if row[0] == "whole_grains_g_d":
            row[1] = 29
    process, out = run(tmp_path, data, [["whole_grains_g_d", 125, "g/d"]])
    assert process.returncode == 0, process.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    assert levers["targets"]["values"]["whole_grains_g_d"] == 125
    moved = {k: v[0] for k, v in TABLE.items()}
    assert levers["targets"]["outputs"] == report.calculate(moved)
    assert levers["levers"][0]["outputs"] == report.calculate(moved)
    assert "风险" in levers["note_zh"]


def test_fraction_conversion_and_partial_targets(tmp_path):
    data = rows()
    for row in data:
        if row[0] == "omega6_energy_pct":
            row[1], row[2] = 11 / 100, "1"
    process, out = run(tmp_path, data, [["牛奶", 71, "g/d"]])
    assert process.returncode == 0, process.stderr
    lever = json.loads((out / "levers.json").read_text())
    assert lever["targets"]["outputs"]["milk_ratio_pct"] == pytest.approx(16, abs=0.5)


@pytest.mark.parametrize("age", ["24", "nan", "abc", ""])
def test_age_input_problems(tmp_path, age):
    process, out = run(tmp_path, rows(), age=age)
    assert process.returncode == 3
    assert (out / "problems.json").exists()


@pytest.mark.parametrize("targets", [[], [["牛奶", 71, "mL"]], [["age", 30, "a"]]])
def test_invalid_targets_block_report(tmp_path, targets):
    process, out = run(tmp_path, rows(), targets)
    assert process.returncode == 3
    assert not (out / "result.json").exists()
