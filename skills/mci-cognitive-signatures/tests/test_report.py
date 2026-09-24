import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


import argparse
from presets import AUC_MCI_SPECIFIC, DOMAINS

MEDS = "美金刚\n"

def run(tmp_path, meds, labs, tag="full"):
    ns = argparse.Namespace(medications=meds, labs=labs, out=tmp_path / tag)
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

def test_domain_order_and_auc():
    from presets import ADNI_N, BABRI_N, BABRI_NC

    assert DOMAINS[0][0] == "注意"
    assert AUC_MCI_SPECIFIC == 0.83
    assert BABRI_N == 918
    assert BABRI_NC == 459
    assert ADNI_N == 1293
    text = run_bare()
    assert "名单是空的" in text
    assert "0.83" not in text


def run_bare():
    import tempfile

    folder = Path(tempfile.mkdtemp())
    ns = argparse.Namespace(medications=None, labs=None, out=folder)
    return personal_report.report(ns).read_text(encoding="utf-8")

