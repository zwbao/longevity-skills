"""Expected risks are printed in Dai et al., Nature Medicine 2022, Table 2.

These tests were written before the lookup/report implementation. They validate
an exact table lookup, not reconstruction of the authors' spline ensemble.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def run(tmp_path, outcome="lung_cancer", exposure=20, unit="a", key="equivalent_smoking_years", age="57", sex="male", current=1, targets=None):
    sheet = tmp_path / "input.csv"
    rows = ["marker,value,unit", f"current_smoker,{current},1"]
    if exposure is not None:
        rows.append(f"{key},{exposure},{unit}")
    sheet.write_text("\n".join(rows) + "\n")
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--measurements", str(sheet), "--outcome", outcome, "--age", age, "--sex", sex, "--out", str(out)]
    if targets is not None:
        target = tmp_path / "targets.csv"
        target.write_text(f"marker,value,unit\n{key},{targets},{unit}\n")
        args += ["--targets", str(target)]
    proc = subprocess.run(args, capture_output=True, text=True)
    result = json.loads((out / "result.json").read_text()) if (out / "result.json").exists() else None
    return proc, result, out


def outputs(result):
    return {k: v["value"] for k, v in result["outputs"].items()}


@pytest.mark.parametrize("exposure,rr,lower,upper", [
    (5, 1.58, 1.19, 2.15), (10, 2.48, 1.40, 4.53),
    (20, 5.11, 1.84, 14.99), (40, 11.62, 2.49, 58.73),
    (50.88, 13.42, 2.63, 74.59),
])
def test_table2_lung_cancer(tmp_path, exposure, rr, lower, upper):
    proc, result, out = run(tmp_path, exposure=exposure)
    assert proc.returncode == 0, proc.stderr
    value = outputs(result)
    assert value["mean_rr"] == rr
    assert value["ui_lower"] == lower
    assert value["ui_upper"] == upper
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("你的查表结果")
    assert "边界" in report and "不是个人发病概率" in report
    assert "793项" in report and "30岁及以上成人" in report


def test_table2_diabetes(tmp_path):
    proc, result, _ = run(tmp_path, outcome="type_2_diabetes", key="daily_cigarette_count", unit="1")
    assert proc.returncode == 0, proc.stderr
    value = outputs(result)
    assert (value["mean_rr"], value["ui_lower"], value["ui_upper"]) == (1.49, 1.18, 1.90)


def test_chinese_exposure_alias_and_year_unit(tmp_path):
    proc, result, out = run(tmp_path, key="累计包年数", unit="year", sex="男")
    assert proc.returncode == 0, proc.stderr
    assert outputs(result)["mean_rr"] == 5.11  # Table 2, 20 pack-years.
    assert "性别组：男" in (out / "report.md").read_text()


def test_table2_reference_age_ihd(tmp_path):
    proc, result, _ = run(tmp_path, outcome="ischemic_heart_disease", key="daily_cigarette_count", unit="1", age="55")
    assert proc.returncode == 0, proc.stderr
    value = outputs(result)
    assert (value["mean_rr"], value["ui_lower"], value["ui_upper"]) == (2.43, 1.17, 5.27)


@pytest.mark.parametrize("kwargs", [
    {"unit": "mg/L"}, {"exposure": 900}, {"exposure": None},
    {"exposure": 15}, {"exposure": "nan"}, {"current": 0},
    {"current": 0.5}, {"age": "29"}, {"age": "nan"},
    {"sex": "unknown"}, {"outcome": "invented"},
    {"outcome": "breast_cancer", "sex": "male"},
    {"outcome": "ischemic_heart_disease", "key": "daily_cigarette_count", "unit": "1", "age": "60"},
    {"outcome": "peripheral_artery_disease", "key": "daily_cigarette_count", "unit": "1", "age": "59"},
    {"targets": 15},
])
def test_invalid_inputs_stop(tmp_path, kwargs):
    proc, result, out = run(tmp_path, **kwargs)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert all(v is None for v in outputs(result).values())
    assert not (out / "levers.json").exists()
    report = (out / "report.md").read_text()
    assert "论文卡片" in report and "边界" in report
    assert "你的查表结果" not in report


def test_targets_compare_printed_points_only(tmp_path):
    # Table 2: diabetes at 20 and 10 cigarettes/day, respectively.
    proc, _, out = run(tmp_path, outcome="type_2_diabetes", key="daily_cigarette_count", unit="1", targets=10)
    assert proc.returncode == 0, proc.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    assert levers["current"]["mean_rr"] == 1.49
    assert levers["targets"]["mean_rr"] == 1.38
    assert levers["levers"][0]["mean_rr_delta"] == pytest.approx(1.38 - 1.49)
    assert "不能预测减量或戒烟后的获益" in (out / "report.md").read_text()


def test_rerun_clears_stale_success(tmp_path):
    assert run(tmp_path, targets=10)[0].returncode == 0
    proc, result, out = run(tmp_path, exposure=None)
    assert proc.returncode == 3
    assert outputs(result)["mean_rr"] is None
    assert not (out / "levers.json").exists()


def test_manifest_matches_presets():
    sys.path.insert(0, str(ROOT / "scripts"))
    from presets import INPUT_UNITS
    manifest = json.loads((ROOT / "skill.json").read_text())
    declared = {s["key"]: s["unit"] for s in manifest["inputs"] if s.get("unit")}
    assert declared == INPUT_UNITS
    assert manifest["inputs_status"] == "verified"
