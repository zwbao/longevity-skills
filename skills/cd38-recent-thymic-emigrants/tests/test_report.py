import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


import argparse

MEDS = "达雷妥尤单抗\n"

def run(tmp_path, meds, labs, tag="full"):
    markers = tmp_path / "markers.csv"
    markers.write_text("lineage,cxcr3,cd38,cd25\nCD8,0.2,3.0,0.1\n", encoding="utf-8")
    ns = argparse.Namespace(medications=meds, labs=labs, out=tmp_path / tag, markers=markers, age=70)
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

def test_cd8_gate_uses_repository_threshold():
    from presets import COHORT_N, GATES, GROUP_SIZE_HIGH, GROUP_SIZE_LOW

    assert personal_report.assign("CD8", 0.2, 3.0, 0.1) == "CD38++"
    assert personal_report.assign("CD8", 1.6, 3.0, 0.1) == "CXCR3 hi"
    assert personal_report.assign("CD4", 0.1, 1.0, 0.8) == "CD25+"
    assert personal_report.assign("CD8", 1.5, 2.2, 0.75) == "剩余成熟初始细胞"
    assert personal_report.age_group(34) == "A"
    assert personal_report.age_group(64) == "D"
    assert personal_report.age_group(65) == "E"
    assert personal_report.age_group(20) is None
    assert GATES["CD8"]["CD38"] == 2.2
    assert COHORT_N == 158
    assert GROUP_SIZE_LOW == 21
    assert GROUP_SIZE_HIGH == 45

