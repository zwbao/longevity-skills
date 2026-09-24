import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, COHORT_MARKER


def listed(body):
    grab = False
    rows = []
    for line in body.splitlines():
        if line.startswith("## "):
            if grab:
                break
            grab = line == "## 方法算出的名单"
            continue
        if grab:
            rows.append(line)
    return rows


def run(tmp_path, measurements, labs=True):
    meas = tmp_path / "measurements.csv"
    meas.write_text(measurements, encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林肠溶片\n", encoding="utf-8")
    lab = None
    if labs:
        lab = tmp_path / "labs.csv"
        lab.write_text("项目,结果,单位\n血红蛋白,90,g/L\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meas, meds, lab, 60).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meas, meds, None, 60).read_text(encoding="utf-8")
    assert text.endswith(f"边界: {BOUNDARY}\n")
    assert "不能据此停" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert listed(text) == listed(bare)
    assert re.search(rf"(?<!\d){COHORT_MARKER}(?!\d)", text) is None
    if labs:
        assert "血红蛋白 90 g/L" in text
    return text


def test_named_genes_keep_paper_order(tmp_path: Path):
    text = run(tmp_path, "name,value\nGPX4,named\nFOXO3,named\np53,named\nNOTAGENE,1\n")
    rows = listed(text)
    assert rows[0].startswith("FOXO3。")
    assert rows[1].startswith("TP53。")
    assert rows[2].startswith("GPX4。")
    assert "NOTAGENE" not in "\n".join(rows)
    assert "没有系数列" in text


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank", None, None, None).read_text(encoding="utf-8")
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "没有提供现用药" in text
    assert "体检不增删" in text
    assert re.search(rf"(?<!\d){COHORT_MARKER}(?!\d)", text) is None
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
