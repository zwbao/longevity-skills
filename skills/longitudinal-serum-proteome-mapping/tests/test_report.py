import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


import argparse
from presets import AGE_MODEL_IDS, AUC_86

MEDS = "葡萄糖酸锌\n二甲双胍\n"

def run(tmp_path, meds, labs, tag="full"):
    ns = argparse.Namespace(medications=meds, labs=labs, out=tmp_path / tag, proteins=None)
    return personal_report.report(ns).read_text(encoding="utf-8")

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

def test_no_phas_and_locked_counts(tmp_path: Path):
    assert len(AGE_MODEL_IDS) == 86
    assert AGE_MODEL_IDS[13] == "p01009"
    assert AUC_86 == 0.70
    proteins = tmp_path / "proteins.csv"
    proteins.write_text("名字,数值\nA1AT,1.2\np01009,3\nNOT_A_PROTEIN,9\n", encoding="utf-8")
    filled = argparse.Namespace(medications=None, labs=None, out=tmp_path / "filled", proteins=proteins)
    text = personal_report.report(filled).read_text(encoding="utf-8")
    assert "α-1-抗胰蛋白酶" in text
    assert "p01009" in text
    assert "NOT_A_PROTEIN" not in text
    assert "30%" not in text
    assert "0.70" not in text
    assert "没有计算健康衰老分数" in text
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    with_labs = argparse.Namespace(medications=None, labs=labs, out=tmp_path / "labs", proteins=proteins)
    again = personal_report.report(with_labs).read_text(encoding="utf-8")

    def method(body):
        lines = body.splitlines()
        start = lines.index("## 方法算出的名单")
        end = start + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        return lines[start:end]

    assert method(text) == method(again)

