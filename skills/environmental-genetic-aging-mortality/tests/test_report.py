import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


import argparse

MEDS = "阿托伐他汀\n"

def run(tmp_path, meds, labs, tag="full"):
    exposures = tmp_path / "exposures.csv"
    exposures.write_text("exposure,present\ncurrent_smoker,yes\n", encoding="utf-8")
    ns = argparse.Namespace(medications=meds, labs=labs, out=tmp_path / tag, exposures=exposures)
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

def test_eight_printed_bounds():
    from presets import DETRIMENTAL_HR_BOUND, EXPOSURES, PROTECTIVE_HR_BOUND, XWAS_N

    assert len(EXPOSURES) == 8
    assert XWAS_N == 492567
    assert PROTECTIVE_HR_BOUND == 0.8
    assert DETRIMENTAL_HR_BOUND == 1.4


def test_only_answered_exposures(tmp_path: Path):
    text = run(tmp_path, None, None, tag="yes")
    assert "现在吸烟" in text
    assert "家庭收入" not in text
    blank = run_bare()
    assert "名单是空的" in blank
    assert "现在吸烟" not in blank

def run_bare():
    from pathlib import Path
    import tempfile
    folder = Path(tempfile.mkdtemp())
    ns = argparse.Namespace(medications=None, labs=None, out=folder, exposures=None)
    return personal_report.report(ns).read_text(encoding="utf-8")

