import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, CAR_DOSE_TEXT, GSE_ACCESSION, P_CUTOFF

MEAS = "name,value\np_ut,0.01\np_h19,0.04\n"

def _section(text, heading):
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])

def test_public_counts():
    assert P_CUTOFF == 0.05
    assert CAR_DOSE_TEXT == "0.5×10^6"
    assert GSE_ACCESSION == "GSE243616"

def test_call_from_p():
    assert personal_report.call_from_p(0.01, 0.04) == "有差别"
    assert personal_report.call_from_p(0.01, 0.2) == "不确定"
    assert personal_report.call_from_p(0.2, 0.2) == "不记为有差别"
    assert personal_report.call_from_p(0.05, 0.01) == "不确定"

def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text(MEAS, encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("没有这种药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meds, None, meas, 60)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 60)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80" in text
    assert "判定是有差别" in text
    assert "不算糖耐量分数" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    assert _section(text, "## 方法算出的名单") == _section(bare.read_text(encoding="utf-8"), "## 方法算出的名单")
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "243616" not in text
    assert "不是给你的用法" in text
