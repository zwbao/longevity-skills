import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import (
    BOUNDARY,
    ADNI_EWM_R,
    MCSA_AWM_R,
    MCSA_EWM_R,
    N_PARTICIPANTS,

)


def test_public_counts():
    assert N_PARTICIPANTS == 3142
    assert MCSA_EWM_R == -0.51
    assert MCSA_AWM_R == 0.39
    assert ADNI_EWM_R == -0.34



def test_formula(tmp_path: Path):
    assert abs(personal_report.ewm_awm_difference(1.2, 0.9) - 0.3) < 1e-9
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\newm,1.2\nawm,0.9\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "0.3" in text



def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text('item,value\newm,1.2\nawm,0.9\n', encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text('美金刚\n', encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas)
    full = personal_report.report(tmp_path / "full", meds, labs, meas)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert '美金刚' in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(bare.read_text(encoding="utf-8"), "## 方法算出的名单")
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "0.3" in text
    assert "预期白质" in text

