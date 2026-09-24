import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, BROKEN_MIDDLE_AGE, YOUNG_MEAN


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


def run(tmp_path, measurements, age, labs=True):
    meas = tmp_path / "measurements.csv"
    meas.write_text(measurements, encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林肠溶片\n", encoding="utf-8")
    lab = None
    if labs:
        lab = tmp_path / "labs.csv"
        lab.write_text("项目,结果,单位\n血红蛋白,90,g/L\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meas, meds, lab, age).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meas, meds, None, age).read_text(encoding="utf-8")
    assert text.endswith(f"边界: {BOUNDARY}\n")
    assert "不能据此停" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert listed(text) == listed(bare)
    if labs:
        assert "血红蛋白 90 g/L" in text
    assert YOUNG_MEAN not in text
    assert BROKEN_MIDDLE_AGE not in text
    return text


def test_age_window_and_organ(tmp_path: Path):
    young = run(tmp_path, "name,value\novary,named\n", 22)
    assert young.splitlines()[0] == "# 卵巢烟酰胺酶"
    assert not any(ch.isdigit() for ch in young.splitlines()[0])
    body = "\n".join(listed(young))
    assert "年轻窗" in body
    assert "CD38" in body
    older = run(tmp_path, "name,value\n肝,named\n", 40)
    assert "中年窗" in "\n".join(listed(older))
    assert "以外的组织" in "\n".join(listed(older))
    assert "截距" in young


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank", None, None, None).read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("# ")
    assert not any(ch.isdigit() for ch in text.splitlines()[0])
    assert "## 体检" in text
    assert "体检不增删" in text
    assert "没有提供现用药" in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert YOUNG_MEAN not in text
