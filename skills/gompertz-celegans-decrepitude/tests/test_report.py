import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, COHORT_N


def test_boundary_medicine_labs_and_spans(tmp_path: Path):
    measurements = tmp_path / "m.csv"
    measurements.write_text("name,value\nh_span_days,10\ng_span_days,30\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿托伐他汀\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.write_report(tmp_path / "full", measurements, meds, labs, 20).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert "相对健康期 0.2500" in text
    assert "相对衰弱期 0.7500" in text
    assert "α 列" in text
    assert str(COHORT_N) not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    bare = personal_report.write_report(tmp_path / "bare", measurements, meds, None, 20)
    assert personal_report.method_section(text) == personal_report.method_section(bare.read_text(encoding="utf-8"))
    assert "该开始" not in text
    assert "建议停" not in text
