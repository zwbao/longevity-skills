import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, MODEL_R2, MRFS


def test_table3_order_and_top_correlation():
    assert MRFS[0][1] == -0.054
    assert abs(MRFS[0][1]) > abs(MRFS[1][1]) > abs(MRFS[2][1])
    assert MODEL_R2 == 0.0145
    assert len(MRFS) == 12


def test_factors_do_not_move_when_labs_change(tmp_path: Path):
    factors = tmp_path / "factors.txt"
    factors.write_text("糖尿病\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n他汀\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", factors, meds, labs).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", factors, None, None).read_text(encoding="utf-8")
    assert f"边界: {BOUNDARY}" in text
    assert "不能据此停" in text
    assert "你报告了这项" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删方法算出的名单" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert _factors(bare) == _factors(text)


def _factors(text: str) -> list[str]:
    return [line for line in text.splitlines() if "你报告了这项" in line]


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 脆弱脑网络因素"
    assert "这次没有报告这些因素" in text
    assert "P=" not in text
    assert "-0.054" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
