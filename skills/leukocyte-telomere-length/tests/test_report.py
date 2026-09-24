import sys
from decimal import Decimal
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import AGE_SD_PER_YEAR, BOUNDARY, FULL_TEXT_READ, MALE_SD, PARTICIPANTS


def test_published_cuts_and_slope():
    assert FULL_TEXT_READ is True
    assert PARTICIPANTS == 474074
    assert personal_report.quartile_name(Decimal("-0.70")) == "最短"
    assert personal_report.quartile_name(Decimal("-0.65")) == "次短"
    assert personal_report.quartile_name(Decimal("-0.002")) == "次长"
    assert personal_report.quartile_name(Decimal("0.65")) == "最长"
    assert personal_report.shortening_years(Decimal("-0.7")) == Decimal("29.2")
    years = (MALE_SD / AGE_SD_PER_YEAR).quantize(Decimal("0.1"))
    assert years == Decimal("7.4")


def test_z_is_binned_and_labs_do_not_change_it(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, meds, labs, Decimal("-0.7")).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, None, Decimal("-0.7")).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "最短" in text
    assert "29.2" in text
    assert "谷丙转氨酶 80" in text
    assert "体检不增删" in text
    assert "474074" not in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert _bin(bare) == _bin(text)


def test_raw_ratio_is_not_binned(tmp_path: Path):
    text = personal_report.report(tmp_path / "raw", 1.2).read_text(encoding="utf-8")
    assert "1.2" in text
    assert "这次不分档" in text
    assert "最短" not in text
    assert "474074" not in text


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 白细胞端粒"
    assert "这次没有给出 z 标准化后的对数端粒" in text
    assert "474074" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"


def _bin(text: str) -> str:
    return next(line for line in text.splitlines() if line.startswith("- 端粒分档"))
