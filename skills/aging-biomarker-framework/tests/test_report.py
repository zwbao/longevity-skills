import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import AGE_MORTALITY_R, BOUNDARY, GRIMAGE2_MORTALITY_HR, HORVATH_SKIN_R2


def test_deviation_and_published_benchmarks():
    assert personal_report.age_deviation(70, 60) == 10
    assert HORVATH_SKIN_R2 == 0.88
    assert GRIMAGE2_MORTALITY_HR == 2.57
    assert AGE_MORTALITY_R == 0.12


def test_report_keeps_deviation(tmp_path: Path):
    clocks = tmp_path / "clocks.csv"
    clocks.write_text("name,predicted,age\nGrimAge2,70,60\n未知时钟,50,40\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", clocks, meds, labs).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", clocks, None, None).read_text(encoding="utf-8")
    assert f"边界: {BOUNDARY}" in text
    assert "不能据此停" in text
    assert "年龄偏差 10.00" in text
    assert "2.57" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删方法算出的名单" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert _devs(bare) == _devs(text)


def _devs(text: str) -> list[str]:
    return [line for line in text.splitlines() if "年龄偏差" in line]


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 衰老标志物对照"
    assert "这次没有给出预测年龄和实足年龄" in text
    assert "2.57" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
