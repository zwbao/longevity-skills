"""Expected values transcribed from Yin et al. 2017, Table 2, before implementation."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# Order: all-cause mortality, total CVD, CHD, stroke; each is (RR, lower, upper).
# Table 2 prints no confidence interval for the reference and dots for missing cells.
PRINTED = {
    3: [(1.12, 1.10, 1.14), (1.14, 1.09, 1.19), None, None],
    4: [(1.08, 1.06, 1.09), (1.09, 1.06, 1.13), (1.16, 1.09, 1.23), (1.05, 0.96, 1.15)],
    5: [(1.04, 1.03, 1.05), (1.05, 1.03, 1.08), (1.11, 1.06, 1.16), (1.02, 0.96, 1.08)],
    6: [(1.01, 1.00, 1.01), (1.02, 1.00, 1.03), (1.05, 1.03, 1.08), (0.99, 0.96, 1.03)],
    7: [(1.00, None, None)] * 4,
    8: [(1.04, 1.04, 1.05), (1.03, 1.02, 1.05), (1.01, 0.99, 1.03), (1.08, 1.06, 1.11)],
    9: [(1.15, 1.14, 1.16), (1.16, 1.13, 1.19), (1.14, 1.08, 1.20), (1.30, 1.24, 1.37)],
    10: [(1.32, 1.29, 1.35), (1.37, 1.29, 1.45), (1.34, 1.20, 1.50), (1.64, 1.47, 1.82)],
    11: [(1.53, 1.47, 1.59), None, None, None],
}
OUTCOMES = ("all_cause_mortality", "total_cvd", "chd", "stroke")


def run(tmp_path, text=None, target=None, extra=()):
    argv = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--out", str(tmp_path / "out")]
    if text is not None:
        path = tmp_path / "measurements.csv"
        path.write_text(text, encoding="utf-8")
        argv += ["--measurements", str(path)]
    if target is not None:
        path = tmp_path / "targets.csv"
        path.write_text(target, encoding="utf-8")
        argv += ["--targets", str(path)]
    result = subprocess.run(argv + list(extra), capture_output=True, text=True)
    return result, tmp_path / "out"


def outputs(out):
    return {k: v["value"] for k, v in json.loads((out / "result.json").read_text())["outputs"].items()}


@pytest.mark.parametrize("hours,expected", PRINTED.items())
def test_table_2_printed_rows(tmp_path, hours, expected):
    result, out = run(tmp_path, f"item,value,unit\nsleep_duration_h,{hours},h\n")
    assert result.returncode == 0, result.stderr
    got = outputs(out)
    assert got["sleep_duration_h"] == hours
    assert got["reference_sleep_h"] == 7
    for outcome, cell in zip(OUTCOMES, expected):
        for suffix, value in zip(("rr", "ci_lower", "ci_upper"), cell or (None, None, None)):
            assert got[f"{outcome}_{suffix}"] == value
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("你的查表结果")
    assert "边界:" in report and "不是个人发病或死亡概率" in report


def test_manifest_matches_presets():
    import presets
    manifest = json.loads((ROOT / "skill.json").read_text())
    spec = next(s for s in manifest["inputs"] if s["from"] == "measurements")
    assert (spec["key"], spec["unit"], spec["range"]) == (presets.INPUT_KEY, presets.INPUT_UNIT, list(presets.PLAUSIBLE_RANGE))
    assert spec["accept"]["min"] == 1 / 60
    assert manifest["validation"]["status"] == "reproduced"
    assert tuple(presets.OUTCOMES) == OUTCOMES


def test_chinese_alias_minutes_and_profile_do_not_change_lookup(tmp_path):
    result, out = run(tmp_path, "项目,结果,单位\n睡眠时长,540,分钟\n", extra=("--age", "65", "--sex", "female"))
    assert result.returncode == 0, result.stderr
    got = outputs(out)
    assert got["sleep_duration_h"] == 9
    assert got["stroke_rr"] == 1.30


@pytest.mark.parametrize("text", [
    None, "item,value,unit\n", "item,value,unit\nsleep_duration_h,9,mg/dL\n",
    "item,value,unit\nsleep_duration_h,90,h\n", "item,value,unit\nsleep_duration_h,nan,h\n",
    "item,value,unit\nsleep_duration_h,6.5,h\n", "item,value,unit\nsleep_duration_h,2,h\n",
    "item,value,unit\nsleep_duration_h,9,h\n睡眠时长,8,h\n",
])
def test_bad_or_missing_input_exits_3_without_risks(tmp_path, text):
    result, out = run(tmp_path, text)
    assert result.returncode == 3, result.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert all(v is None for v in outputs(out).values())
    report = (out / "report.md").read_text()
    assert "论文卡片" in report and "边界:" in report
    assert "你的查表结果" not in report
    assert not (out / "levers.json").exists()


def test_targets_use_printed_values_and_discrete_sensitivity(tmp_path):
    result, out = run(tmp_path, "item,value,unit\nsleep_duration_h,9,h\n", "item,value,unit\nsleep_duration_h,420,min\n")
    assert result.returncode == 0, result.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    assert levers["current"]["stroke_rr"] == 1.30
    assert levers["targets"]["outputs"]["stroke_rr"] == 1.00
    assert levers["levers"][0]["rr_delta"]["stroke_rr"] == pytest.approx(1.00 - 1.30)
    nearby = levers["sensitivity"][0]["neighbors"]
    assert [p["sleep_duration_h"] for p in nearby] == [8, 10]
    assert [p["outputs"]["stroke_rr"] for p in nearby] == [1.08, 1.64]


def test_invalid_target_clears_previous_success(tmp_path):
    text = "item,value,unit\nsleep_duration_h,9,h\n"
    result, out = run(tmp_path, text)
    assert result.returncode == 0
    result, out = run(tmp_path, text, "item,value,unit\nsleep_duration_h,7.5,h\n")
    assert result.returncode == 3
    assert not (out / "levers.json").exists()
    assert all(v is None for v in outputs(out).values())
    result, out = run(tmp_path, text)
    assert result.returncode == 0 and not (out / "problems.json").exists()


def test_missing_table_cells_remain_missing_in_targets(tmp_path):
    result, out = run(tmp_path, "item,value,unit\nsleep_duration_h,11,h\n", "item,value,unit\nsleep_duration_h,10,h\n")
    assert result.returncode == 0
    data = json.loads((out / "levers.json").read_text())
    assert data["levers"][0]["rr_delta"]["stroke_rr"] is None
    assert data["targets"]["outputs"]["stroke_rr"] == 1.64
    assert len(data["sensitivity"][0]["neighbors"]) == 1
