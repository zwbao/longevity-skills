import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, MEAN_READS_PER_CELL


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


def test_missense_above_dropout(tmp_path: Path):
    assert MEAN_READS_PER_CELL == 3620
    meas = tmp_path / "measurements.csv"
    meas.write_text("name,value\nmissense_heteroplasmy,0.70\nenvironment,galactose\numi,80\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林肠溶片\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n血红蛋白,90,g/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meas, meds, labs, None).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meas, meds, None, None).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "血红蛋白 90 g/L" in text
    assert listed(text) == listed(bare)
    blob = "\n".join(listed(text))
    assert "超过大约百分之六十" in blob
    assert "半乳糖" in blob
    assert "3620" not in text
    assert "该开始" not in text
    assert "建议停" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)


def test_silent_has_no_cutoff(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("name,value\nsilent_heteroplasmy,0.8\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meas, None, None, None).read_text(encoding="utf-8")
    assert "没有清除切点" in text
    assert "超过大约百分之六十" not in text
    assert "3620" not in text


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank", None, None, None).read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("# ")
    assert not any(ch.isdigit() for ch in text.splitlines()[0])
    assert "没有项目进入名单" in text
    assert "没有提供现用药" in text
    assert "体检不增删" in text
    assert "location" in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
