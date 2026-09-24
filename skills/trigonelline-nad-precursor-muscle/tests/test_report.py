import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


import argparse

MEDS = "烟酰胺核糖\n阿司匹林\n"

def run(tmp_path, meds, labs, tag="full"):
    ns = argparse.Namespace(medications=meds, labs=labs, out=tmp_path / tag, trigonelline=1.0)
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

def test_trigonelline_on_the_list_matches(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("葫芦巴碱\n阿司匹林\n", encoding="utf-8")
    text = personal_report.report(
        argparse.Namespace(medications=meds, labs=None, out=tmp_path / "hit", trigonelline=1.0)
    ).read_text(encoding="utf-8")
    assert "对应名单上的 葫芦巴碱" in text
    assert "阿司匹林：名单里没有这个名字。不能据此停。" in text
    bare = personal_report.report(
        argparse.Namespace(medications=meds, labs=None, out=tmp_path / "miss", trigonelline=None)
    ).read_text(encoding="utf-8")
    assert "对应名单上的" not in bare
    assert "不能据此停" in bare


def test_precursor_match_and_ec50():
    from presets import EC50_CONTROL_UM

    text = run_bare()
    assert EC50_CONTROL_UM == 315
    assert "烟酰胺核糖" in text
    assert "不参与分档" in text
    assert "315" not in text
    assert "不能据此停" in text

def run_bare():
    from pathlib import Path
    import tempfile
    folder = Path(tempfile.mkdtemp())
    meds = folder / "meds.txt"
    meds.write_text("烟酰胺核糖\n", encoding="utf-8")
    ns = argparse.Namespace(medications=meds, labs=None, out=folder / "o", trigonelline=1.0)
    return personal_report.report(ns).read_text(encoding="utf-8")

