import math
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, GAMMA, SAMPLES


def test_formulas():
    assert personal_report.relative_r2(0.5, 0.8) == 0.625
    assert personal_report.switch_probability(0.05) == 1 - math.exp(-GAMMA * 0.05)
    assert SAMPLES == 22770


def test_report_keeps_fractions(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", "Horvath", 0.5, 0.8, 0.05, meds, labs).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", "Horvath", 0.5, 0.8, 0.05, None, None).read_text(encoding="utf-8")
    assert f"边界: {BOUNDARY}" in text
    assert "不能据此停" in text
    assert "RR2=0.6250" in text
    assert "66–75%" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删方法算出的名单" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert _fractions(bare) == _fractions(text)


def _fractions(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("- Horvath") or line.startswith("- Zhang") or line.startswith("- PhenoAge")]


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 表观遗传随机成分"
    assert "这次没有同时给出两个决定系数" in text
    assert "66–75%" not in text
    assert "90%" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
