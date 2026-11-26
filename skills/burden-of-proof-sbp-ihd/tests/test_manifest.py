"""Expectations transcribed from Razo et al. 2022, Supplementary Table 4.

Written before the implementation. Table values are rounded to two decimals;
exact table lookups must retain those printed values, not refit the spline.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_supplementary_table_4():
    from personal_report import compute

    # SBP level (mmHg); RR (95% UI), Supplementary Information pp. 8–9.
    printed = [
        (100, 1, 1, 1),
        (107.5, 1.06, 1.06, 1.07),
        (110, 1.12, 1.10, 1.13),
        (120, 1.39, 1.34, 1.44),
        (130, 1.81, 1.70, 1.93),
        (140, 2.38, 2.17, 2.62),
        (150, 3.11, 2.75, 3.52),
        (160, 3.99, 3.43, 4.63),
        (165, 4.48, 3.81, 5.26),
        (170, 4.95, 4.17, 5.89),
        (180, 5.66, 4.69, 6.82),
        (190, 6.15, 5.05, 7.48),
        (200, 6.64, 5.41, 8.15),
    ]
    for sbp, rr, lo, hi in printed:
        result = compute(sbp)
        assert result["sbp_mmhg"] == sbp
        assert result["reference_sbp_mmhg"] == 100
        assert result["ihd_rr"] == rr
        assert result["ihd_rr_ui_lower"] == lo
        assert result["ihd_rr_ui_upper"] == hi
        assert result["readout_method"] == "table_lookup"


def test_independent_printed_interior_examples():
    from personal_report import compute

    # Results, Mean RR function: these two points are NOT table anchors.
    # An interpolation approximation, not a reproduction of the fitted spline.
    for sbp, rr, lo, hi in [(115, 1.23, 1.20, 1.27), (135, 2.08, 1.91, 2.26)]:
        result = compute(sbp)
        assert result["readout_method"] == "log_linear_interpolation"
        for key, expected in zip(
            ("ihd_rr", "ihd_rr_ui_lower", "ihd_rr_ui_upper"), (rr, lo, hi)
        ):
            assert result[key] == pytest.approx(expected, rel=0.02)


def run_cli(tmp_path, content, targets=None):
    source = tmp_path / "measurements.csv"
    source.write_text(content, encoding="utf-8")
    out = tmp_path / "out"
    command = [sys.executable, str(ROOT / "scripts/personal_report.py"),
               "--measurements", str(source), "--out", str(out)]
    if targets is not None:
        target = tmp_path / "targets.csv"
        target.write_text(targets, encoding="utf-8")
        command += ["--targets", str(target)]
    return subprocess.run(command, capture_output=True, text=True), out


def test_manifest_matches_presets():
    from presets import INPUT_KEY, INPUT_UNIT, PLAUSIBLE_RANGE, TABLE_RANGE
    manifest = json.loads((ROOT / "skill.json").read_text())
    spec = next(s for s in manifest["inputs"] if s["key"] == INPUT_KEY)
    assert spec["unit"] == INPUT_UNIT
    assert spec["range"] == list(PLAUSIBLE_RANGE)
    assert TABLE_RANGE == (100, 200)
    assert spec["accept"]["kPa"] == 7.500617


def test_report_result_and_targets(tmp_path):
    done, out = run_cli(tmp_path, "marker,value,unit\n收缩压,130,mmHg\n",
                       "marker,value,unit\nSBP,120,mmHg\n")
    assert done.returncode == 0, done.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["ihd_rr"]["value"] == 1.81
    assert result["ihd_rr_ui_lower"]["value"] == 1.70
    assert result["ihd_rr_ui_upper"]["value"] == 1.93
    lever = json.loads((out / "levers.json").read_text())
    assert lever["schema"] == "longevity-levers/1"
    assert lever["targets"]["ihd_rr"] == 1.39
    assert lever["levers"][0]["ihd_rr_delta"] == pytest.approx(1.39 - 1.81)
    assert lever["targets"]["rr_ratio_to_current"] == pytest.approx(1.39 / 1.81)
    assert lever["sensitivity"][0]["per_unit"] > 0
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("你的查算结果")
    assert "边界：" in report
    assert "不代表个人降压治疗的获益" in report


@pytest.mark.parametrize("row", [
    "收缩压,130,mg/dL", "收缩压,400,mmHg", "收缩压,90,mmHg",
    "收缩压,201,mmHg", "舒张压,80,mmHg", "收缩压,nan,mmHg",
    "收缩压,inf,mmHg", "收缩压,130/80,mmHg", "",
    "收缩压,130,mmHg\nSBP,140,mmHg",
])
def test_invalid_input_exits_three_without_result(tmp_path, row):
    # Reusing an output directory must not leave an earlier successful result.
    done, out = run_cli(tmp_path, "marker,value,unit\nSBP,130,mmHg\n")
    assert done.returncode == 0
    done, out = run_cli(tmp_path, "marker,value,unit\n" + row + "\n")
    assert done.returncode == 3, done.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    report = (out / "report.md").read_text()
    assert "这次没有计算" in report
    assert "论文卡片" in report and "边界：" in report
    assert "你的查算结果" not in report


@pytest.mark.parametrize("row", ["SBP,90,mmHg", "SBP,120,mg/dL", "", "typo,120,mmHg"])
def test_invalid_targets_fail_closed(tmp_path, row):
    done, out = run_cli(tmp_path, "marker,value,unit\nSBP,130,mmHg\n",
                       "marker,value,unit\n" + row + "\n")
    assert done.returncode == 3
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()


def test_kpa_conversion_matches_printed_example(tmp_path):
    kpa = 130 / 7.500617
    done, out = run_cli(tmp_path, f"marker,value,unit\nSystolic blood pressure,{kpa},kPa\n")
    assert done.returncode == 0, done.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["ihd_rr"]["value"] == pytest.approx(1.81)


def test_endpoints_and_interpolation_metadata(tmp_path):
    from personal_report import compute, levers
    for sbp in (100, 200):
        assert levers(sbp, None)["sensitivity"][0]["per_unit"] > 0
    done, out = run_cli(tmp_path, "marker,value,unit\nSBP,135,mmHg\n")
    assert done.returncode == 0
    report = (out / "report.md").read_text()
    assert "插值近似" in report
    assert compute(135)["bracket_lower_sbp_mmhg"] == 130
    assert compute(135)["bracket_upper_sbp_mmhg"] == 140


def test_missing_file_is_structured_problem(tmp_path):
    out = tmp_path / "out"
    done = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                           "--measurements", str(tmp_path / "missing.csv"), "--out", str(out)],
                          capture_output=True, text=True)
    assert done.returncode == 3
    assert (out / "problems.json").exists()
