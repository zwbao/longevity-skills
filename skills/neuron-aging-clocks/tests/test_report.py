import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, NEURONS, PAPER_OLDEST_N, PAPER_YOUNGEST_N


def test_quantile_counts_differ_from_the_figure():
    young_n, old_n = personal_report.tail_counts()
    assert young_n == 26
    assert old_n == 26
    assert young_n != PAPER_YOUNGEST_N
    assert old_n != PAPER_OLDEST_N
    assert NEURONS["ADL"][0] > NEURONS["ALN"][0]
    assert personal_report.age_bin(107.4) == 0
    assert personal_report.age_bin(176.9) == 4


def test_report_keeps_boundary_and_neuron_line(tmp_path: Path):
    neurons = tmp_path / "neurons.txt"
    neurons.write_text("ALN\nADL\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("丁香酸\n不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", neurons, meds, labs).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", neurons, None, None).read_text(encoding="utf-8")
    assert f"边界: {BOUNDARY}" in text
    assert "不能据此停" in text
    assert "丁香酸（syringic acid）" in text
    assert "钥更西汀（vanoxerine）" not in text
    assert "放线菌酮（cycloheximide）" not in text
    assert "论文测试过这个化合物" in text
    assert "不能据此停" in text
    assert "延缓" not in text
    assert "谷丙转氨酶 80" in text
    assert "不增删方法算出的名单" in text
    assert "syringic acid" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert _neuron_lines(bare) == _neuron_lines(text)


def _neuron_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("- ALN") or line.startswith("- ADL")]


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank", None, None, None).read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 神经元预测年龄"
    assert "这次没有给出神经元名字" in text
    assert "丁香酸" not in text
    assert "延缓" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
