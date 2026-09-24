import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import (
    BOUNDARY,
    COMPOUNDS,
    CSF_PERCENT_LOWER,
    NORCOG_N,
    SERUM_PERCENT_LOWER,

)


def test_public_counts():
    assert NORCOG_N == 316
    assert SERUM_PERCENT_LOWER == 41.35
    assert CSF_PERCENT_LOWER == 19.18
    assert COMPOUNDS[0] == "Rac-BL-918"
    assert len(COMPOUNDS) == 4



def test_formula(tmp_path: Path):
    assert personal_report.percent_change(100, 58.65) == -41.35
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nserum_baseline,100\nserum_follow,58.65\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "-41.35%" in text
    assert "Rac-BL-918" in text



def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text('item,value\nserum_baseline,100\nserum_follow,58.65\n', encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text('阿司匹林\n', encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas)
    full = personal_report.report(tmp_path / "full", meds, labs, meas)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert '阿司匹林' in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(bare.read_text(encoding="utf-8"), "## 方法算出的名单")
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "-41.35%" in text
    assert "Rac-BL-918" in text

