"""Expected HRs are printed cells, not generated calculator outputs."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from personal_report import calculate
from presets import INPUT_KEY, INPUT_UNIT, MODELS


def test_printed_apoe_hazard_ratios():
    # Figure 3 caption: HRs are per e4 allele. Tables S1/S3/S4, APOE rows:
    # order is total, via cognitive level, via cognitive change, direct.
    expected = {
        "EUR": (1.98, 0.99, 1.88, 1.07),
        "AFR": (1.37, 1.04, 1.16, 1.13),
        "AMR": (1.03, 0.98, 1.14, 0.92),
    }
    for ancestry, printed in expected.items():
        result = calculate(1, ancestry)
        for key, value in zip(("hr_total", "hr_level", "hr_change", "hr_direct"), printed):
            # Beta is printed to .001 and HR to .01; allow combined rounding.
            assert result[key] == pytest.approx(value, abs=0.006)


def run_report(tmp_path, value="1", unit="1", ancestry="EUR", marker=INPUT_KEY, extra=()):
    path = tmp_path / "measurements.csv"
    path.write_text(f"marker,value,unit\n{marker},{value},{unit}\n", encoding="utf-8")
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(path), "--out", str(tmp_path / "out")]
    if ancestry is not None:
        args += ["--ancestry", ancestry]
    return subprocess.run(args + list(extra), capture_output=True, text=True)


def test_manifest_and_paper_example_in_result(tmp_path):
    manifest = json.loads((ROOT / "skill.json").read_text())
    spec = next(item for item in manifest["inputs"] if item["key"] == INPUT_KEY)
    assert spec["unit"] == INPUT_UNIT == "1"
    assert spec["range"] == [0, 2]
    assert set(MODELS) == {"EUR", "AFR", "AMR"}
    assert manifest["validation"]["status"] == "draft"
    assert manifest["validation"]["gap_zh"].startswith("预印本，未经同行评审")
    assert manifest["validation"]["examples"]
    assert run_report(tmp_path, marker="APOE ε4拷贝数").returncode == 0
    result = json.loads((tmp_path / "out/result.json").read_text())["outputs"]
    assert set(result) == {item["key"] for item in manifest["outputs"]}
    assert result["hr_total"]["value"] == pytest.approx(1.98, abs=0.006)
    assert result["hr_change"]["value"] == pytest.approx(1.88, abs=0.006)
    report = (tmp_path / "out/report.md").read_text()
    assert report.index("论文卡片") < report.index("本次结果")
    assert "边界:" in report and "预印本，未经同行评审" in report
    assert "0 拷贝" in report and "95%" in report


@pytest.mark.parametrize("value,unit,ancestry,extra", [
    ("1", "mg/L", "EUR", ()),
    ("1", "%", "EUR", ()),
    ("3", "1", "EUR", ()),
    ("-1", "1", "EUR", ()),
    ("0.5", "1", "EUR", ()),
    ("NaN", "1", "EUR", ()),
    ("", "1", "EUR", ()),
    ("1", "1", None, ()),
    ("1", "1", "EAS", ()),
    ("1", "1", "EUR", ("--age", "unknown")),
    ("1", "1", "EUR", ("--age", "999")),
    ("1", "1", "EUR", ("--sex", "invalid")),
])
def test_invalid_inputs_exit_3_without_results(tmp_path, value, unit, ancestry, extra):
    completed = run_report(tmp_path, value, unit, ancestry, extra=extra)
    assert completed.returncode == 3, completed.stderr
    assert json.loads((tmp_path / "out/problems.json").read_text())["problems"]
    assert not (tmp_path / "out/result.json").exists()
    report = (tmp_path / "out/report.md").read_text()
    assert "这次没有计算" in report
    assert "本次结果" not in report
    assert report.index("论文卡片") < report.index("输入没有通过检查")


def test_missing_file_and_reused_output_directory(tmp_path):
    assert run_report(tmp_path).returncode == 0
    completed = subprocess.run([
        sys.executable, str(ROOT / "scripts/personal_report.py"),
        "--measurements", str(tmp_path / "missing.csv"),
        "--ancestry", "EUR", "--out", str(tmp_path / "out"),
    ], capture_output=True, text=True)
    assert completed.returncode == 3
    assert not (tmp_path / "out/result.json").exists()
    assert run_report(tmp_path).returncode == 0
    assert not (tmp_path / "out/problems.json").exists()


def test_no_measurements_exits_3(tmp_path):
    completed = subprocess.run([
        sys.executable, str(ROOT / "scripts/personal_report.py"),
        "--ancestry", "EUR", "--out", str(tmp_path / "out"),
    ], capture_output=True, text=True)
    assert completed.returncode == 3


def test_dosage_law_and_context_only_age_sex(tmp_path):
    # Algebraic invariants, not additional claims of printed examples.
    for ancestry in MODELS:
        zero, one, two = (calculate(n, ancestry) for n in (0, 1, 2))
        for key in ("hr_total", "hr_level", "hr_change", "hr_direct"):
            assert zero[key] == 1
            assert two[key] == pytest.approx(one[key] ** 2)
    assert run_report(tmp_path, extra=("--age", "40", "--sex", "female")).returncode == 0
    result = json.loads((tmp_path / "out/result.json").read_text())["outputs"]
    assert result["hr_total"]["value"] == pytest.approx(1.98, abs=0.006)
    assert "年龄不在" in (tmp_path / "out/report.md").read_text()
