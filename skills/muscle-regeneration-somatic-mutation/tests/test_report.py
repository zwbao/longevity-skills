import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, MSM_VARIANT_N


def test_gene_lookup_is_not_personal_sequencing(tmp_path: Path):
    assert MSM_VARIANT_N == 2127
    measurements = tmp_path / "m.csv"
    measurements.write_text("name,value\nRpsa,named\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n肌酐,70,µmol/L\n", encoding="utf-8")
    text = personal_report.write_report(tmp_path / "full", measurements, meds, labs, 60).read_text(encoding="utf-8")
    bare = personal_report.write_report(tmp_path / "bare", measurements, meds, None, 60).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "肌酐 70 µmol/L" in text
    assert personal_report.method_section(text) == personal_report.method_section(bare)
    method = personal_report.method_section(text)
    assert "Rpsa" in method
    assert "不是你的测序结果" in method
    assert "握力" not in method
    assert "归一化的式子" in text
    assert "2127" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "该开始" not in text
    assert "建议停" not in text
