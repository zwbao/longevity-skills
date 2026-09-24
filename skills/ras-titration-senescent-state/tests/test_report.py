import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


MEDS = "阿司匹林肠溶片\n不存在的药\n"

def run(tmp_path, meds, labs, tag="full"):
    ns = argparse.Namespace(medications=meds, labs=labs, out=tmp_path / tag, system="rpe1", bin="XL")
    path = personal_report.report(ns)
    return path.read_text(encoding="utf-8")

import argparse

def test_boundary_medicines_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text(MEDS, encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = run(tmp_path, meds, labs)
    assert text.endswith(f"边界: {BOUNDARY}\n")
    assert "不能据此停" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert "该开始" not in text
    assert "建议停" not in text
    bare = run(tmp_path, None, None, tag="bare")

    def method(body):
        lines = body.splitlines()
        start = lines.index("## 方法算出的名单")
        end = start + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        return lines[start:end]

    assert method(text) == method(bare)
    assert "体检不增删" in text
    assert "## 你正在使用的药" in text
    assert "## 体检" in text

def test_xl_is_high_ras_bin():
    assert "最高" in personal_report.RPE1_DETAIL["XL"]
    assert personal_report.DEG_ABS_LOG_FOLD == 1.2
    assert personal_report.DEG_FDR == 0.05
    assert "缺席" in personal_report.LIVER_DETAIL["UBC"]
    assert "弱于" in personal_report.LIVER_DETAIL["PGK"]

