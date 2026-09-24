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

from presets import (
    CLINICAL,
    DNAM_MAE_TEST,
    FIG4_CLINICAL_PANEL,
    FIG4_METABOLITE_PANEL,
    FIG4_PROTEIN_PANEL,
    METABOLITES,
    MORTALITY_HR_TEST,
    PROTEINS,
    emr_age,
)


def test_formula_is_not_printed(tmp_path: Path):
    assert emr_age(0) == 51.68254
    assert DNAM_MAE_TEST == 8.50
    assert MORTALITY_HR_TEST == 4.53
    assert FIG4_PROTEIN_PANEL == 16
    assert FIG4_METABOLITE_PANEL == 14
    assert FIG4_CLINICAL_PANEL == 10
    assert len(METABOLITES) == 14
    assert len(CLINICAL) == 9
    assert len(PROTEINS) == 13
    assert "albumin" in PROTEINS and "albumin" in CLINICAL
    text = run(tmp_path, "name,value\nalbumin,4.2\nbun,15\ncreatinine,1.1\n")
    assert "尿素氮" in listed(text)[0]
    assert "肌酐" in listed(text)[1]
    assert "白蛋白" in listed(text)[2]
    assert "没有算出个人 EMRAge" in text
    assert "51.68254" not in text
    assert "血红蛋白" not in "\n".join(listed(text))

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

