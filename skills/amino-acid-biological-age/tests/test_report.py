import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


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
    if labs:
        assert "血红蛋白 90 g/L" in text
    return text


from presets import TEST_MAE, ADJUSTED_MAE


def test_ratio_needs_all_eight(tmp_path: Path):
    assert TEST_MAE == 7.53
    assert ADJUSTED_MAE == 6.73
    partial = run(tmp_path, "name,value\nalanine,20\nglutamine,80\nmethionine,50\n")
    assert "不算比例" in partial
    assert listed(partial)[0] == "没有项目进入名单。"
    assert not any(line.startswith("1.") for line in listed(partial))
    assert "0.2000" not in "\n".join(line for line in listed(partial))
    text = run(
        tmp_path,
        "name,value\nalanine,10\nglutamine,20\nglycine,10\nhistidine,10\n"
        "leucine,10\nphenylalanine,10\ntyrosine,10\nvaline,20\nmethionine,50\n",
    )
    rows = listed(text)
    assert rows[0].startswith("1. 丙氨酸")
    assert "0.1000" in rows[0]
    assert rows[1].startswith("2. 谷氨酰胺")
    assert "0.2000" in rows[1]
    assert rows[7].startswith("8. 缬氨酸")
    assert "0.2000" in rows[7]
    assert "蛋氨酸" not in "\n".join(rows)
    assert "没有算出 AmiAge" in text

def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank", None, None, None).read_text(encoding="utf-8")
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "## 方法算出的名单" in text
    assert "## 你正在使用的药" in text
    assert "没有提供现用药" in text
    assert "## 体检" in text
    assert "体检不增删" in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"

