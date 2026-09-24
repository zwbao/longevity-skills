import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from personal_report import render_report
from presets import BOUNDARY
import presets


def _section(text: str) -> list[str]:
    lines = []
    grab = False
    for line in text.splitlines():
        if line.startswith("## 方法算出的名单"):
            grab = True
            continue
        if grab and line.startswith("## "):
            break
        if grab:
            lines.append(line)
    return lines


def test_boundary_missing_medicine_and_labs():
    rows = presets.fixture_rows()
    meds = ["阿司匹林"]
    report_a = render_report(rows, meds, ["血红蛋白,90,g/L"])
    report_b = render_report(rows, meds, ["血小板,40,10^9/L", "肌酐,200,umol/L"])
    assert report_a.strip().splitlines()[-1] == BOUNDARY
    assert report_b.strip().splitlines()[-1] == BOUNDARY
    assert "不能据此停" in report_a
    assert "阿司匹林：名单里没有这个名字。不能据此停。" in report_a
    assert _section(report_a) == _section(report_b)
    assert not hasattr(presets, "WEIGHTS")


def test_cli_writes_report(tmp_path: Path):
    measurements = tmp_path / "measurements.csv"
    medications = tmp_path / "meds.txt"
    labs = tmp_path / "labs.csv"
    presets.write_fixture(measurements)
    medications.write_text("阿司匹林\n", encoding="utf-8")
    labs.write_text("谷丙转氨酶,80,U/L\n", encoding="utf-8")
    out = tmp_path / "out"
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "scripts" / "personal_report.py"),
            "--measurements",
            str(measurements),
            "--medications",
            str(medications),
            "--labs",
            str(labs),
            "--out",
            str(out),
        ]
    )
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.strip().splitlines()[-1] == BOUNDARY
    assert "不能据此停" in text


def test_published_numbers():
    presets.check_published_numbers()
