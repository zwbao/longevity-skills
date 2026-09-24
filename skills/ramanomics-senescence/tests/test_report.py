import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, N_FROZEN, load_table

SAMPLE = """name,value
symbol,Cdkn1a
symbol,Krt10
symbol,NOTAREALGENEXYZ
"""


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_table_counts():
    rows, by_gene = load_table()
    assert len(rows) == N_FROZEN
    assert "CDKN1A" in by_gene


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n白细胞,6.0,10^9/L\n", encoding="utf-8")
    meas = tmp_path / "measurements.csv"
    meas.write_text(SAMPLE, encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas, 60)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 60)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "白细胞 6.0" in text
    assert _section(text, "## 方法算出的名单") == _section(
        bare.read_text(encoding="utf-8"), "## 方法算出的名单"
    )
    assert "该开始" not in text
    assert "avg_log2FC" in text
    assert "NOTAREALGENEXYZ" in text
    assert "## 论文卡片" in text
    assert "10.1038/s43587-026-01219-7" in text
