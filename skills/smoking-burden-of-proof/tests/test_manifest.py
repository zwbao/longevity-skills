"""Expected risks are printed in Dai et al., Nature Medicine 2022, Table 2.

The first tests were written before the implementation. These reproduce the
published prediction table, not the underlying spline fitting pipeline.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def run_report(tmp_path, rows, outcome="lung_cancer", age="57", sex="male", status="current", targets=None):
    path = tmp_path / "measurements.csv"
    with path.open("w") as f:
        writer = csv.writer(f)
        writer.writerow(["marker", "value", "unit"])
        writer.writerows(rows)
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(path), "--outcome", outcome,
            "--age", age, "--sex", sex, "--smoking-status", status, "--out", str(out)]
    if targets is not None:
        target_path = tmp_path / "targets.csv"
        with target_path.open("w") as f:
            writer = csv.writer(f)
            writer.writerow(["marker", "value", "unit"])
            writer.writerows(targets)
        args += ["--targets", str(target_path)]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode in (0, 3), proc.stderr
    return proc.returncode, out


def outputs(out):
    return {k: v["value"] for k, v in json.loads((out / "result.json").read_text())["outputs"].items()}


def test_printed_lung_cancer_20_pack_years(tmp_path):
    # Table 2: Lung cancer | Pack-years | [20] 5.11 (1.84, 14.99)
    code, out = run_report(tmp_path, [("pack_years", 20, "a")])
    assert code == 0
    values = outputs(out)
    assert values["exposure"] == 20
    assert (values["relative_risk"], values["ui_lower"], values["ui_upper"]) == (5.11, 1.84, 14.99)
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("本次查表")
    assert "边界:" in report and "95% 不确定区间" in report


def test_printed_diabetes_20_cigarettes(tmp_path):
    # Table 2: Type 2 diabetes | Cigarettes per day | [20] 1.49 (1.18, 1.90)
    code, out = run_report(tmp_path, [("cigarettes_per_day", 20, "1")], outcome="type_2_diabetes")
    assert code == 0
    values = outputs(out)
    assert values["exposure"] == 20
    assert (values["relative_risk"], values["ui_lower"], values["ui_upper"]) == (1.49, 1.18, 1.90)


def test_printed_lung_cancer_percentile(tmp_path):
    # Table 2: 85th percentile risk level 50.88 | 13.42 (2.63, 74.59)
    code, out = run_report(tmp_path, [("pack_years", 50.88, "a")])
    assert code == 0
    values = outputs(out)
    assert values["exposure"] == 50.88
    assert (values["relative_risk"], values["ui_lower"], values["ui_upper"]) == (13.42, 2.63, 74.59)


def test_manifest_units_and_ranges_match_presets():
    from presets import INPUT_RANGES, INPUT_UNITS, OUTCOMES
    manifest = json.loads((ROOT / "skill.json").read_text())
    specs = {s["key"]: s for s in manifest["inputs"]}
    for key, unit in INPUT_UNITS.items():
        assert specs[key]["unit"] == unit
        assert specs[key]["range"] == INPUT_RANGES[key]
    assert len(OUTCOMES) == 36
    assert manifest["inputs_status"] == "verified"
    assert manifest["validation"]["status"] == "reproduced"


@pytest.mark.parametrize("rows", [
    [], [("pack_years", 20, "mg/L")], [("pack_years", 301, "a")],
    [("pack_years", "NaN", "a")], [("pack_years", "nonsense", "a")],
    [("累计包年", 20, "")], [("pack_years", -1, "a")],
    [("pack_years", 20, "a"), ("累计包年", 10, "a")],
    [("cigarettes_per_day", 20, "1")],
])
def test_bad_or_missing_measurements_exit_3_without_old_results(tmp_path, rows):
    code, out = run_report(tmp_path, [("pack_years", 20, "a")])
    assert code == 0
    code, out = run_report(tmp_path, rows)
    assert code == 3
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    assert not (out / "lookup.json").exists()
    report = (out / "report.md").read_text()
    assert "这次没有计算" in report and "边界:" in report
    assert report.index("论文卡片") < report.index("输入没有通过检查")
    assert "5.11" not in report


@pytest.mark.parametrize("age,status", [("29", "current"), ("NaN", "current"), ("abc", "current"), ("57", "former"), ("57", "never")])
def test_population_validation(tmp_path, age, status):
    code, out = run_report(tmp_path, [("pack_years", 20, "a")], age=age, status=status)
    assert code == 3 and not (out / "result.json").exists()


def test_aliases_and_exact_equivalent_year_unit(tmp_path):
    code, out = run_report(tmp_path, [("累计包年", 20, "year")])
    assert code == 0 and outputs(out)["relative_risk"] == 5.11
    code, out = run_report(tmp_path, [("每日支数", 20, "1")], outcome="type_2_diabetes")
    assert code == 0 and outputs(out)["relative_risk"] == 1.49


def test_between_points_has_no_invented_personal_rr(tmp_path):
    code, out = run_report(tmp_path, [("pack_years", 15, "a")])
    assert code == 0
    values = outputs(out)
    assert values["lookup_status"] == "between_printed_points"
    assert all(values[k] is None for k in ["relative_risk", "ui_lower", "ui_upper"])
    refs = json.loads((out / "lookup.json").read_text())["references"]
    # Table 2, Lung cancer at 10 and 20 pack-years.
    assert [(x["exposure"], x["rr"], x["ui_lower"], x["ui_upper"]) for x in refs] == [
        (10, 2.48, 1.40, 4.53), (20, 5.11, 1.84, 14.99)]


@pytest.mark.parametrize("dose", [1, 100])
def test_outside_printed_points_not_extrapolated(tmp_path, dose):
    code, out = run_report(tmp_path, [("pack_years", dose, "a")])
    assert code == 0 and outputs(out)["relative_risk"] is None
    assert outputs(out)["lookup_status"] == "outside_printed_points"


def test_cardiovascular_reference_age_and_sex_specific_outcomes(tmp_path):
    code, out = run_report(tmp_path, [("cigarettes_per_day", 20, "1")], outcome="aortic_aneurysm")
    assert code == 0
    v = outputs(out)
    # Table 2, Aortic aneurism (ref. age: 55–59 years), 20 cigarettes/day.
    assert (v["relative_risk"], v["ui_lower"], v["ui_upper"]) == (5.39, 2.89, 10.36)
    code, out = run_report(tmp_path, [("cigarettes_per_day", 20, "1")], outcome="aortic_aneurysm", age="60")
    assert code == 3
    code, out = run_report(tmp_path, [("pack_years", 20, "a")], outcome="breast_cancer", sex="male")
    assert code == 3
    code, out = run_report(tmp_path, [("pack_years", 20, "a")], outcome="breast_cancer", sex="female")
    assert code == 0
    v = outputs(out)
    assert (v["relative_risk"], v["ui_lower"], v["ui_upper"]) == (1.17, 1.04, 1.31)


def test_fracture_is_binary_and_parkinsons_not_promoted(tmp_path):
    code, out = run_report(tmp_path, [], outcome="fracture")
    assert code == 0
    v = outputs(out)
    # Table 2 Fracture: binary 1.34 (0.84, 1.97), 1 star.
    assert (v["relative_risk"], v["ui_lower"], v["ui_upper"], v["evidence_stars"]) == (1.34, 0.84, 1.97, 1)
    assert v["exposure"] is None and v["lookup_status"] == "binary"
    code, out = run_report(tmp_path, [("cigarettes_per_day", 20, "1")], outcome="parkinsons_disease")
    assert code == 0
    v = outputs(out)
    assert (v["relative_risk"], v["ui_lower"], v["ui_upper"]) == (0.54, 0.34, 0.84)
    assert "不能解释为吸烟有净健康获益" in (out / "report.md").read_text()


def test_targets_compare_only_printed_points(tmp_path):
    code, out = run_report(tmp_path, [("pack_years", 20, "a")], targets=[("pack_years", 10, "a")])
    assert code == 0
    levers = json.loads((out / "levers.json").read_text())
    # Both risks printed in Table 2: the difference is a calculation, not a paper example.
    assert levers["current"]["rr"] == 5.11
    assert levers["targets"]["rr"] == 2.48
    assert levers["targets"]["rr_delta"] == 2.48 - 5.11
    assert levers["sensitivity"][0]["rr_per_unit"] is None
    assert "累计包年不能" in levers["note_zh"]
    code, out = run_report(tmp_path, [("pack_years", 20, "a")], targets=[("pack_years", 15, "a")])
    assert code == 0
    levers = json.loads((out / "levers.json").read_text())
    assert levers["targets"]["rr"] is None and levers["targets"]["rr_delta"] is None


@pytest.mark.parametrize("targets", [[("pack_years", 0, "a")], [("pack_years", 10, "g")], [("cigarettes_per_day", 10, "1")]])
def test_bad_targets_fail(tmp_path, targets):
    code, out = run_report(tmp_path, [("pack_years", 20, "a")], targets=targets)
    assert code == 3 and not (out / "result.json").exists()


def test_every_frozen_point_matches_its_printed_cell():
    # Independent comparison to preserved source cells checks all 36 rows and both UI ends.
    import re
    from presets import OUTCOMES
    from personal_report import lookup
    for row in OUTCOMES.values():
        cells = row["raw_cells"]
        exposures = [5, 10, 20, 40, float(cells[6])] if row["exposure_key"] else [None]
        printed = cells[2:6] + [cells[7]] if row["exposure_key"] else [cells[7]]
        for dose, cell in zip(exposures, printed):
            expected = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", cell)]
            found = lookup(row, dose)
            assert [found[k] for k in ["rr", "ui_lower", "ui_upper"]] == expected


@pytest.mark.parametrize("contents", ["marker,value,unit\npack_years,20,a,unexpected\n", "other,columns\nx,y\n"])
def test_malformed_csv_is_an_input_problem(tmp_path, contents):
    path = tmp_path / "bad.csv"
    path.write_text(contents)
    out = tmp_path / "out"
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                           "--measurements", str(path), "--outcome", "lung_cancer",
                           "--age", "57", "--smoking-status", "current", "--out", str(out)], capture_output=True)
    assert proc.returncode == 3
    assert (out / "problems.json").exists() and not (out / "result.json").exists()


def test_missing_required_profile_and_outcome_are_input_problems(tmp_path):
    out = tmp_path / "out"
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"), "--out", str(out)], capture_output=True)
    assert proc.returncode == 3
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert {p["key"] for p in problems} >= {"age", "smoking_status", "outcome"}
