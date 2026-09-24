import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, GESTALT_MALE_MRNA_N


def method(body: str) -> str:
    return personal_report.method_section(body)


def test_no_score_and_labs_do_not_edit_the_list(tmp_path: Path):
    assert GESTALT_MALE_MRNA_N == 49
    measurements = tmp_path / "m.csv"
    measurements.write_text("name,value\nHSPA8,1.2\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.write_report(tmp_path / "full", measurements, meds, labs, 60).read_text(encoding="utf-8")
    bare = personal_report.write_report(tmp_path / "bare", measurements, meds, None, 60).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert method(text) == method(bare)
    assert method(text).strip().endswith("名单是空的。")
    assert "HSPA8" not in method(text)
    assert "缺权重列和方向列" in text
    assert "49" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "该开始" not in text
    assert "建议停" not in text
    assert "体检不增删" in text
