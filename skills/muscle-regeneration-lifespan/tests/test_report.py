import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, CELL_N


def test_supplied_score_uses_published_cutoff(tmp_path: Path):
    assert CELL_N == 273923
    measurements = tmp_path / "m.csv"
    measurements.write_text("name,value\noneway_fbr_sen_score,3000\nAldh1a3,1.2\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.write_report(tmp_path / "full", measurements, meds, labs, 60).read_text(encoding="utf-8")
    bare = personal_report.write_report(tmp_path / "bare", measurements, meds, None, 60).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert personal_report.method_section(text) == personal_report.method_section(bare)
    method = personal_report.method_section(text)
    assert "senescent-like" in method
    assert "达到" in method
    assert "Aldh1a3" not in method
    assert "logFC" in text
    assert "273923" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "该开始" not in text
    assert "建议停" not in text
