import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, PARTICIPANTS, UKB_MTCN_MEAN


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


def test_pathogenic_call_and_copy_number_gate(tmp_path: Path):
    assert PARTICIPANTS == 274832
    meas = tmp_path / "measurements.csv"
    meas.write_text(
        "name,value\nchrM:3243:A,G,0.2\nmtCN,40\nchrM:302:A,AC,0.4\n"
        "chrM:302:A,ACC,0.3\nchrM:302:A,ACCC,0.2\nchrM:302:Other,0\n",
        encoding="utf-8",
    )
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林肠溶片\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n血红蛋白,90,g/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meas, meds, labs, 75).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meas, meds, None, 75).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "血红蛋白 90 g/L" in text
    assert listed(text) == listed(bare)
    assert any("chrM:3243:A,G" in line and "质控后的携带者" in line for line in listed(text))
    assert any("低于 50" in line for line in listed(text))
    assert any("参考比例" in line and "0.1" in line for line in listed(text))
    assert "274832" not in text
    assert UKB_MTCN_MEAN not in text
    assert "178134" not in text
    assert "该开始" not in text
    assert "建议停" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)


def test_low_fraction_is_not_a_carrier(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("name,value\nchrM:1555:A,G,0.02\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meas, None, None, None).read_text(encoding="utf-8")
    assert "不算质控后的携带者" in text
    assert "274832" not in text


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank", None, None, None).read_text(encoding="utf-8")
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "没有项目进入名单" in text
    assert "没有提供现用药" in text
    assert "体检不增删" in text
    assert "Supplementary Notes 2" in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
