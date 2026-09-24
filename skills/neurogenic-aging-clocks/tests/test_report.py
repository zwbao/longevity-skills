import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOOTSTRAP, BOUNDARY, PARABIOSIS


def test_published_parabiosis_average():
    assert PARABIOSIS["chrono"][2] == 4.52
    assert round((5.38 + 3.66) / 2, 2) == 4.52
    assert BOOTSTRAP["oligodendrocyte"] == (0.91, 1.6)
    assert BOOTSTRAP["microglia"] == (0.92, 2.1)


def test_absolute_error_and_stable_list(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", "aNSC-NPC", 21, 16, meds, labs).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", "aNSC-NPC", 21, 16, None, None).read_text(encoding="utf-8")
    assert f"边界: {BOUNDARY}" in text
    assert "不能据此停" in text
    assert "绝对误差是 5.00 个月" in text
    assert "4.52" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删方法算出的名单" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert _cells(bare) == _cells(text)


def _cells(text: str) -> list[str]:
    return [line for line in text.splitlines() if "绝对误差" in line]


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 神经发生区细胞时钟"
    assert "这次没有给出细胞类型" in text
    assert "4.52" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
