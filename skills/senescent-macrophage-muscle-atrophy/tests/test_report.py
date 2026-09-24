import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, OA_PATIENT_N


def test_ferric_iron_and_named_compound(tmp_path: Path):
    assert OA_PATIENT_N == 15
    measurements = tmp_path / "m.csv"
    measurements.write_text("name,value\ntotal_iron,4\nferrous_iron,1\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("辅酶Q10\n阿司匹林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.write_report(tmp_path / "full", measurements, meds, labs, 60).read_text(encoding="utf-8")
    bare = personal_report.write_report(tmp_path / "bare", measurements, meds, None, 60).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert personal_report.method_section(text) == personal_report.method_section(bare)
    method = personal_report.method_section(text)
    assert "辅酶Q10" in method
    assert "没有个人剂量" in method
    assert "结果是 3" in method
    assert "缺 IIb 计数列" in text
    assert "15" not in text
    assert "µg" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "该开始" not in text
    assert "建议停" not in text
