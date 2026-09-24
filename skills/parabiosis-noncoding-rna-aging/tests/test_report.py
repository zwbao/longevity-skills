import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, COHORT_TOKEN


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


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("""name,value\nhsa-miR-29c-3p,12\nmiR-999-5p,3\n""", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "full", meas, meds, labs, 52).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meas, meds, None, 52).read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert listed(text) == listed(bare)
    assert "该开始" not in text
    assert "建议停" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert COHORT_TOKEN not in text
    assert "miR-29c-3p" in "\n".join(listed(text))
    assert "miR-999-5p" not in "\n".join(listed(text))
    assert "Supplementary Table 8" in text



def test_blank(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank", None, None, None).read_text(encoding="utf-8")
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "没有项目进入名单。" in text
    assert COHORT_TOKEN not in text
    assert "## 论文卡片" in text
    assert "## 能算的" in text
    assert "## 不能算的" in text
    assert "## 体检" in text
