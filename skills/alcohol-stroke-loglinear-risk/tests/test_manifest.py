"""Printed validation is written before the implementation.

Lancet 2019 Results, paragraph accompanying Figure 4: per 100 g/week,
ischaemic stroke 1.09 (1.04–1.14), intracerebral haemorrhage
1.18 (1.12–1.24), total stroke 1.12 (1.09–1.16).
These are independent rescalings of the printed per-280-g/week constants.
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


def test_printed_100_g_week_example():
    expected = {
        "ischaemic_stroke": (1.09, 1.04, 1.14),
        "intracerebral_haemorrhage": (1.18, 1.12, 1.24),
        "total_stroke": (1.12, 1.09, 1.16),
    }
    actual = report.ratios_for_weekly_difference(100)
    for outcome, printed in expected.items():
        # Both the original coefficients and expected results have two decimals.
        assert actual[outcome] == pytest.approx(printed, abs=0.006)


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / "skill.json").read_text())
    inputs = {s["key"]: s for s in manifest["inputs"]}
    for key, unit in presets.INPUT_UNITS.items():
        assert inputs[key]["unit"] == unit
    for key in presets.INTAKE_KEYS:
        assert inputs[key]["range"] == list(presets.INTAKE_RANGE)
    assert inputs["age"]["range"] == list(presets.AGE_RANGE)


def run_cli(tmp_path, rows, targets=None, extra=None):
    measurements = tmp_path / "measurements.csv"
    measurements.write_text("marker,value,unit\n" + rows, encoding="utf-8")
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(measurements), "--age", "50", "--sex", "male",
            "--prior-cvd", "0", "--out", str(tmp_path / "out")]
    if targets is not None:
        path = tmp_path / "targets.csv"
        path.write_text("marker,value,unit\n" + targets, encoding="utf-8")
        args += ["--targets", str(path)]
    args += extra or []
    return subprocess.run(args, text=True, capture_output=True)


ROWS = "当前纯酒精摄入量,20,g/d\n比较纯酒精摄入量,10,g/d\n"


def test_report_result_and_targets(tmp_path):
    # The difference is the paper's 100 g/week example; 4 g/week is its
    # lowest genetic category. Only the difference enters the equation.
    rows = f"alcohol_g_day,{104/7},g/d\nreference_alcohol_g_day,{4/7},g/d\n"
    done = run_cli(tmp_path, rows, "alcohol_g_day,0,g/d\n")
    assert done.returncode == 0, done.stderr
    out = tmp_path / "out"
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["ischaemic_stroke_rr"]["value"] == pytest.approx(1.09, abs=0.006)
    assert result["intracerebral_haemorrhage_rr"]["value"] == pytest.approx(1.18, abs=0.006)
    assert result["total_stroke_rr"]["value"] == pytest.approx(1.12, abs=0.006)
    text = (out / "report.md").read_text()
    assert text.index("论文卡片") < text.index("情景比较")
    assert "边界：" in text and report.BOUNDARY in text
    assert "个人发病概率" in text and "目标情景" in text
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    assert len(levers["sensitivity"]) == 2
    assert len(levers["levers"]) == 1
    assert levers["targets"]["values"]["alcohol_g_day"] == 0
    assert levers["targets"]["applicability"] == "extrapolation"
    for outcome in presets.STROKE_RR:
        assert levers["targets"]["outputs"][outcome + "_rr"] < 1
        assert levers["levers"][0]["change"][outcome + "_rr"] < 0


@pytest.mark.parametrize("rows,targets,extra", [
    (ROWS.replace("g/d", "mL"), None, None),
    (ROWS.replace(",20,", ",201,"), None, None),
    (ROWS.splitlines()[0] + "\n", None, None),
    (ROWS.replace(",20,", ",nan,"), None, None),
    (ROWS.replace(",20,", ",-1,"), None, None),
    (ROWS.replace(",g/d", ","), None, None),
    (ROWS, "alcohol_g_day,5,mL\n", None),
    (ROWS, "alcohol_g_day,201,g/d\n", None),
    (ROWS, "reference_alcohol_g_day,0,g/d\n", None),
    (ROWS, "unknown,0,g/d\n", None),
    (ROWS, "", None),
    (ROWS, None, ["--sex", "female"]),
    (ROWS, None, ["--age", "29"]),
    (ROWS, None, ["--age", "abc"]),
    (ROWS, None, ["--prior-cvd", "1"]),
])
def test_invalid_inputs_exit_three_and_remove_stale_results(tmp_path, rows, targets, extra):
    assert run_cli(tmp_path, ROWS).returncode == 0
    done = run_cli(tmp_path, rows, targets, extra)
    assert done.returncode == 3, done.stderr
    out = tmp_path / "out"
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    text = (out / "report.md").read_text()
    assert "论文卡片" in text and "这次没有计算" in text
    assert "| 缺血性卒中 |" not in text


def test_negative_difference_reverses_confidence_limits():
    # Inversion property, using the printed per-280-g/week estimates.
    actual = report.ratios_for_weekly_difference(-280)
    assert actual["ischaemic_stroke"] == pytest.approx((1/1.27, 1/1.43, 1/1.13))
    assert actual["intracerebral_haemorrhage"] == pytest.approx((1/1.58, 1/1.84, 1/1.36))
    for value in report.ratios_for_weekly_difference(0).values():
        assert value == (1, 1, 1)
