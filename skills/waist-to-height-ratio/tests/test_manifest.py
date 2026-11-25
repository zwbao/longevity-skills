"""Engineering checks, NOT a reproduction of a printed personal example.

Ashwell et al. (2012), p. 284 prints the boundary 0.5 but no paired
waist/height inputs and personal output. Synthetic measurements below test
dimensional identities and input handling; validation must remain draft.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as report
import presets
import skillkit

MANIFEST = json.loads((ROOT / "skill.json").read_text())


def run(tmp_path, rows, *extra):
    path = tmp_path / "measurements.csv"
    path.write_text("item,value,unit\n" + rows, encoding="utf-8")
    out = tmp_path / "out"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/personal_report.py"),
         "--measurements", str(path), "--out", str(out), *extra],
        capture_output=True, text=True,
    )
    return proc, out


def outputs(out):
    return {k: v["value"] for k, v in json.loads((out / "result.json").read_text())["outputs"].items()}


def test_manifest_and_printed_boundary():
    # p. 284 supplies this constant, not a worked personal calculation.
    assert presets.SCREENING_BOUNDARY == 0.5
    specs = {s["key"]: s for s in MANIFEST["inputs"] if s["from"] == "measurements"}
    assert {key: s["unit"] for key, s in specs.items()} == presets.MEASUREMENT_UNITS
    assert MANIFEST["validation"]["status"] == "draft"
    assert MANIFEST["inputs_status"] == "draft"


def test_normal_result_obeys_ratio_identity_and_has_paper_card(tmp_path):
    proc, out = run(tmp_path, "腰围,87,cm\n身高,172,cm\n", "--age", "40")
    assert proc.returncode == 0, proc.stderr
    values = outputs(out)
    assert values["waist_height_ratio"] * 172 == pytest.approx(87)
    assert values["screening_category"] == "at_or_above_boundary"
    text = (out / "report.md").read_text()
    assert text.index("## 论文卡片") < text.index("## 你的结果")
    assert "10.1111/j.1467-789x.2011.00952.x" in text
    assert presets.BOUNDARY in text
    assert "仍在验证" in text
    assert not (out / "problems.json").exists()
    assert (out / "levers.json").exists()


@pytest.mark.parametrize("unit,waist,height", [("cm", 87, 172), ("m", .87, 1.72), ("mm", 870, 1720), ("in", 87 / 2.54, 172 / 2.54)])
def test_units_preserve_dimensionless_ratio(tmp_path, unit, waist, height):
    proc, out = run(tmp_path, f"WC,{waist},{unit}\nstature,{height},{unit}\n", "--age", "40")
    assert proc.returncode == 0, proc.stderr
    assert outputs(out)["waist_height_ratio"] * height == pytest.approx(waist)


@pytest.mark.parametrize("factor,category", [(0.5, "at_or_above_boundary"), (0.5 - 1e-7, "below_boundary"), (0.5 + 1e-7, "at_or_above_boundary")])
def test_boundary_classifies_before_rounding(factor, category):
    # Synthetic dimensionless boundary probe; not claimed as a paper example.
    result = report.calculate({"waist_cm": factor * 170, "height_cm": 170})
    assert result["screening_category"] == category


@pytest.mark.parametrize("rows,age,kind", [
    ("腰围,87,kg\n身高,172,cm\n", "40", "unit"),
    ("腰围,870,cm\n身高,172,cm\n", "40", "range"),
    ("腰围,87,cm\n", "40", "missing"),
    ("腰围,34,\n身高,172,cm\n", "40", "unit_missing"),
    ("腰围,NaN,cm\n身高,172,cm\n", "40", "parse"),
    ("腰围,87,cm\n腰围,88,cm\n身高,172,cm\n", "40", "duplicate"),
    ("腰围,87,cm\n身高,172,cm\n", "17", "range"),
    ("腰围,87,cm\n身高,172,cm\n", "bad", "parse"),
    ("腰围,87,cm\n身高,172,cm\n", "NaN", "parse"),
])
def test_bad_inputs_exit_three_without_calculated_outputs(tmp_path, rows, age, kind):
    proc, out = run(tmp_path, rows, "--age", age)
    assert proc.returncode == 3, proc.stderr
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert any(p["kind"] == kind for p in problems)
    assert all(v is None for v in outputs(out).values())
    assert not (out / "levers.json").exists()
    text = (out / "report.md").read_text()
    assert "## 论文卡片" in text and "这次没有计算" in text
    assert "## 你的结果" not in text


def test_missing_age_and_unreadable_file(tmp_path):
    proc, out = run(tmp_path, "腰围,87,cm\n身高,172,cm\n")
    assert proc.returncode == 3
    assert any(p["key"] == "age" for p in json.loads((out / "problems.json").read_text())["problems"])
    assert report.main(["--measurements", str(tmp_path / "absent.csv"), "--age", "40", "--out", str(out)]) == 3


def test_targets_and_sensitivity_are_arithmetic_not_risk(tmp_path):
    targets = tmp_path / "targets.csv"
    targets.write_text("item,value,unit\n腰围,0.82,m\n")
    proc, out = run(tmp_path, "腰围,87,cm\n身高,172,cm\n", "--age", "40", "--targets", str(targets))
    assert proc.returncode == 0, proc.stderr
    lever = json.loads((out / "levers.json").read_text())
    assert lever["schema"] == "longevity-levers/1"
    target_value = skillkit.collect_file(targets, MANIFEST).values["waist_cm"]
    assert lever["targets"]["waist_height_ratio"] * 172 == pytest.approx(target_value)
    assert lever["levers"][0]["waist_height_ratio_delta"] * 172 == pytest.approx(target_value - 87)
    slopes = {s["key"]: s["ratio_per_unit"] for s in lever["sensitivity"]}
    assert slopes["waist_cm"] * 172 == pytest.approx(1)
    assert slopes["height_cm"] * 172 ** 2 == pytest.approx(-87)
    assert "患病概率" in lever["note_zh"]


@pytest.mark.parametrize("target_rows", ["height,180,cm\n", "waist,87,kg\n", "typo,80,cm\n", ""])
def test_invalid_targets_stop_and_clear_stale_results(tmp_path, target_rows):
    proc, out = run(tmp_path, "腰围,87,cm\n身高,172,cm\n", "--age", "40")
    assert proc.returncode == 0
    target = tmp_path / "targets.csv"
    target.write_text("item,value,unit\n" + target_rows)
    proc, out = run(tmp_path, "腰围,87,cm\n身高,172,cm\n", "--age", "40", "--targets", str(target))
    assert proc.returncode == 3
    assert all(v is None for v in outputs(out).values())
    assert not (out / "levers.json").exists()
