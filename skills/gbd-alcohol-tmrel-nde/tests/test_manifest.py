"""Printed Table S1 predictions, followed by input and lookup contract checks."""
import json
import itertools
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import presets


def test_printed_central_asia_1990():
    # Appendix 2, Table S1, p 3 (PDF p 4), Female / Male columns.
    # Central Asia | 15 to 19 | 1990 | 0·0735 (0–0·300) |
    # 0·126 (0–0·600) | 0·00280 (0–0) | 0·00480 (0–0)
    female = presets.lookup("Central Asia", 15, "female", 1990)
    male = presets.lookup("Central Asia", 19, "male", 1990)
    assert [female[k] for k in presets.VALUE_KEYS] == [0.0735, 0, 0.300, 0.126, 0, 0.600]
    assert [male[k] for k in presets.VALUE_KEYS] == [0.00280, 0, 0, 0.00480, 0, 0]


def test_printed_east_asia_2020(tmp_path):
    # Appendix 2, Table S1, p 23 (PDF p 24): East Asia | 50 to 54 | 2020
    # Female: 0·505 (0·400–0·600), 1·79 (1·00–2·50)
    # Male:   0·459 (0·400–0·600), 1·51 (0·800–2·30)
    for sex, expected in [
        ("female", [0.505, 0.400, 0.600, 1.79, 1.00, 2.50]),
        ("male", [0.459, 0.400, 0.600, 1.51, 0.800, 2.30]),
    ]:
        row = presets.lookup("East Asia", 50, sex, 2020)
        assert [row[k] for k in presets.VALUE_KEYS] == expected
        code, outputs, report, _ = run_report(tmp_path, sex=sex)
        assert code == 0
        assert [outputs[k]["value"] for k in presets.VALUE_KEYS] == expected
        assert "10.1016/s0140-6736(22)00847-9" in report
        assert report.index("论文卡片") < report.index("你的输入")
        assert presets.BOUNDARY in report


def run_report(tmp_path, value="10", unit="g/d", age="50", sex="female", region="East Asia", year="2020", extra=()):
    measurements = tmp_path / "measurements.csv"
    measurements.write_text(f"item,value,unit\n平均每日纯酒精摄入量,{value},{unit}\n")
    out = tmp_path / "out"
    cmd = [sys.executable, str(ROOT / "scripts/personal_report.py"),
           "--measurements", str(measurements), "--out", str(out)]
    for flag, val in [("--age", age), ("--sex", sex), ("--region", region), ("--year", year)]:
        if val is not None:
            cmd += [flag, str(val)]
    proc = subprocess.run(cmd + list(extra), capture_output=True, text=True)
    assert proc.returncode in (0, 3), proc.stderr
    return (proc.returncode, json.loads((out / "result.json").read_text())["outputs"],
            (out / "report.md").read_text(), out)


@pytest.mark.parametrize("kwargs", [
    {"unit": "drinks/day"}, {"unit": "mL"}, {"unit": ""}, {"value": "-1"}, {"value": "101"},
    {"value": "nan"}, {"value": ""}, {"age": None}, {"age": "abc"}, {"age": "14"},
    {"sex": None}, {"sex": "both"}, {"region": None}, {"region": "unknown"},
    {"year": "2026"}, {"year": "2020.5"},
])
def test_invalid_inputs_exit_three(tmp_path, kwargs):
    code, outputs, report, out = run_report(tmp_path, **kwargs)
    assert code == 3
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert all(item["value"] is None for item in outputs.values())
    assert "这次没有计算" in report and presets.BOUNDARY in report


def test_lookup_boundaries_and_manifest():
    manifest = json.loads((ROOT / "skill.json").read_text())
    specs = {s["key"]: s for s in manifest["inputs"]}
    assert specs[presets.ALCOHOL_KEY]["unit"] == presets.ALCOHOL_UNIT
    assert specs[presets.ALCOHOL_KEY]["range"] == list(presets.ALCOHOL_RANGE)
    assert presets.lookup("East Asia", 54.999, "female", 2020)["age_group"] == "50 to 54"
    assert presets.lookup("East Asia", 55, "female", 2020)["age_group"] == "55 to 59"
    assert presets.lookup("East Asia", 95, "male", 2020)["age_group"] == "80 plus"
    with pytest.raises(ValueError):
        presets.lookup("Global", 50, "female", 2020)
    with pytest.raises(ValueError):
        presets.lookup("East Asia", 50, "female", 2021)


def test_missing_file_and_stale_output(tmp_path):
    run_report(tmp_path)
    code, outputs, _, out = run_report(tmp_path, extra=["--measurements", str(tmp_path / "absent.csv")])
    assert code == 3 and all(v["value"] is None for v in outputs.values())
    assert not (out / "levers.json").exists()
    code, _, _, out = run_report(tmp_path)
    assert code == 0 and not (out / "problems.json").exists()


def test_nde_equality_and_targets(tmp_path):
    # Target is the printed female East Asia 50–54 NDE (1.79 standard drinks/day).
    target = tmp_path / "targets.csv"
    target.write_text("item,value,unit\nethanol_g_day,17.9,g/d\n")
    code, outputs, _, out = run_report(tmp_path, value="17.9", extra=["--targets", str(target)])
    assert code == 0
    assert outputs["nde_side"]["value"] == "equal_to_printed_mean"
    assert outputs["nde_standard_drinks_day"]["value"] == 1.79
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    assert levers["targets"]["nde_standard_drinks_day"] == 1.79
    assert "风险" in levers["note_zh"]


def test_table_has_every_printed_stratum():
    # Source columns/labels: 21 regions, 15 to 19 through 75 to 79 + 80 plus,
    # 1990/2000/2010/2020, Female/Male. This audits extraction completeness.
    ages = [f"{age} to {age + 4}" for age in range(15, 80, 5)] + ["80 plus"]
    expected = set(itertools.product(presets.REGION_ZH, ages, presets.YEARS, ("female", "male")))
    assert set(presets.table()) == expected
    for row in presets.table().values():
        assert all(row[key] >= 0 for key in presets.VALUE_KEYS)
        assert row["tmrel_ui_low"] <= row["tmrel_ui_high"]
        assert row["nde_ui_low"] <= row["nde_ui_high"]


@pytest.mark.parametrize("contents", [
    "item,value,unit\nethanol_g_day,1,drinks/day\n",
    "item,value,unit\nethanol_g_day,10,g/d\nage,60,a\n",
    "item,value,unit\n",
])
def test_invalid_targets_block_all_results(tmp_path, contents):
    target = tmp_path / "targets.csv"
    target.write_text(contents)
    code, outputs, _, out = run_report(tmp_path, extra=["--targets", str(target)])
    assert code == 3
    assert all(v["value"] is None for v in outputs.values())
    assert not (out / "levers.json").exists()


def test_zero_intake_and_chinese_strata(tmp_path):
    # Zero is a printed exposure reference, not a recommendation generated here.
    code, outputs, report, _ = run_report(tmp_path, value="0", region="东亚", sex="女")
    assert code == 0
    assert outputs["standard_drinks_day"]["value"] == 0
    assert outputs["nde_side"]["value"] == "below_printed_mean"
    assert outputs["reference_region"]["value"] == "East Asia"
    assert "不能证明个人安全或有益" in report
