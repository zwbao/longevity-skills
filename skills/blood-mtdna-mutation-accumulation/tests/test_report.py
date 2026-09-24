import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, PARTICIPANTS


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


def test_age_class_and_named_gene(tmp_path: Path):
    assert PARTICIPANTS == 736038
    meas = tmp_path / "measurements.csv"
    meas.write_text(
        "name,value\nsubstitution,C>T\nstrand,heavy\nin_ori,no\nheteroplasmy,0.02\nTERT,named\n",
        encoding="utf-8",
    )
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林肠溶片\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n血红蛋白,90,g/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meas, meds, labs, 80).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meas, meds, None, 80).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "血红蛋白 90 g/L" in text
    assert listed(text) == listed(bare)
    blob = "\n".join(listed(text))
    assert "重链 C>T" in blob
    assert "已过 60 岁" in blob
    assert "低于 0.05" in blob
    assert "TERT" in blob
    assert "736038" not in text
    assert "17504" not in text
    assert "该开始" not in text
    assert "建议停" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank", None, None, None).read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("# ")
    assert not any(ch.isdigit() for ch in text.splitlines()[0])
    assert "没有项目进入名单" in text
    assert "Supplementary Tables 8" in text
    assert "体检不增删" in text
    assert "736038" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
