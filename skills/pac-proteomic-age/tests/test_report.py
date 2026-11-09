"""Report wording: paper card first, boundary kept, no start/stop or dose language."""

import re

import personal_report
from conftest import synthetic_subjects, write_rows
from presets import BOUNDARY


def _report(tmp_path, **extra):
    age, rows = synthetic_subjects()["syn_2"]
    path = write_rows(tmp_path / "npx.csv", rows)
    args = ["--measurements", str(path), "--age", str(age), "--out", str(tmp_path / "out")]
    if extra.get("medications"):
        med = tmp_path / "med.txt"
        med.write_text("吡非尼酮\n", encoding="utf-8")
        args += ["--medications", str(med)]
    assert personal_report.main(args) == 0
    return (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


def test_paper_card_comes_first(tmp_path):
    text = _report(tmp_path)
    card, rest = text.split("## 输入", 1)
    assert "10.1038/s41587-026-03286-y" in card
    assert "Integration of proteomic aging clocks" in card
    assert "Nature Biotechnology" in card and "2026" in card
    assert "蛋白质组年龄是 42.73 岁" in rest


def test_boundary_and_no_dose_or_stop_advice(tmp_path):
    text = _report(tmp_path, medications=True)
    assert f"边界: {BOUNDARY}" in text
    assert "不能据此停用" in text
    assert not re.search(r"\d+\s*mg", text)
    assert "建议服用" not in text and "开始服用" not in text
