import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


import argparse
from presets import MAE_YEARS, OUTCOMES

MEDS = "阿司匹林\n"

def run(tmp_path, meds, labs, tag="full"):
    ns = argparse.Namespace(
        medications=meds, labs=labs, out=tmp_path / tag, retinal_age=60, age=50, probs=None
    )
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

def test_gap_and_probability_expectation(tmp_path: Path):
    text = run(tmp_path, None, None, tag="gap")
    assert "差 10 年" in text
    assert "超出" in text
    probs = [0.0] * 77
    probs[35] = 1.0
    path = tmp_path / "probs.txt"
    path.write_text("\n".join(str(value) for value in probs), encoding="utf-8")
    assert personal_report.retinal_from_probs(probs) == 50
    assert OUTCOMES[0][0] == "白内障"
    assert len(OUTCOMES) == 11
    assert MAE_YEARS == 2.79

