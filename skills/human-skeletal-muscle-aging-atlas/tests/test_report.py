import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, CELL_N


def test_named_states_keep_paper_direction(tmp_path: Path):
    assert CELL_N == 90902
    measurements = tmp_path / "m.csv"
    measurements.write_text("name,value\nTNF+,named\ntype I,named\n未知细胞,1\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n血红蛋白,90,g/L\n", encoding="utf-8")
    text = personal_report.write_report(tmp_path / "full", measurements, meds, labs, 60).read_text(encoding="utf-8")
    bare = personal_report.write_report(tmp_path / "bare", measurements, meds, None, 60).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "血红蛋白 90 g/L" in text
    assert personal_report.method_section(text) == personal_report.method_section(bare)
    method = personal_report.method_section(text)
    assert "TNF+" in method or "TNF+ 肌干细胞" in method
    assert "I 型慢肌纤维" in method
    assert "IIX" not in method
    assert "未知细胞" not in method
    assert "90902" not in text
    assert "没有截距" in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "该开始" not in text
    assert "建议停" not in text
