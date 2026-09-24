import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, C105Y_PROTEIN_PHOSPHATASE_PERCENT, classify

SAMPLE = """name,value
variant,C105Y
"""


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_alleles():
    assert classify("C150Y") == "C150Y"
    assert classify("daf-18(yh1)") == "C150Y"
    assert classify("syb499") == "C150Y"
    assert classify("PTEN C105Y") == "C105Y"
    assert classify("C124S") == "C124S"
    assert classify("yh2") == "yh2"
    assert classify("yh3") == "yh3"
    assert classify("R130Q") == "other"
    assert C105Y_PROTEIN_PHOSPHATASE_PERCENT == 57.3


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    meas = tmp_path / "measurements.csv"
    meas.write_text(SAMPLE, encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas, 70)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 70)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(
        bare.read_text(encoding="utf-8"), "## 方法算出的名单"
    )
    assert "该开始" not in text
    assert "建议停" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "对上人 PTEN C105Y" in text
    assert str(C105Y_PROTEIN_PHOSPHATASE_PERCENT) not in text
