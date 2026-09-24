import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, CARVACROL_RANK, COMPOUNDS, GSE_MUSCLE, SAMP8_PER_GROUP, THYMOL_RANK


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_public_counts():
    assert GSE_MUSCLE == "GSE298195"
    assert SAMP8_PER_GROUP == 15
    assert COMPOUNDS[0]["display"].startswith("百里香酚")
    assert CARVACROL_RANK == 1
    assert THYMOL_RANK == 2
    assert len(COMPOUNDS) == 8


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("name,value\nthymol,1\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas, 50)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 50)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "阿司匹林" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(
        bare.read_text(encoding="utf-8"), "## 方法算出的名单"
    )
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "298195" not in text
    assert "mg/kg" not in text
    assert "百里香酚" in text
    assert "CpG" in text
    assert "没有打开" not in text
    assert "建议停" not in text
    assert "该开始" not in text
