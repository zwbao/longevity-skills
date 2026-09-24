import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, HIDDEN_COHORT


def _list_section(text: str) -> str:
    start = text.index("## 方法算出的名单")
    end = text.index("## 体检")
    return text[start:end]


def test_boundary_medicine_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    out = personal_report.report(tmp_path / "out", 60, meds, labs, None)
    text = out.read_text(encoding="utf-8")
    assert text.rstrip().splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80" in text
    assert "该开始" not in text
    assert "建议停" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert str(HIDDEN_COHORT) not in text
    bare = personal_report.report(tmp_path / "bare", 60, meds, None, None)
    assert _list_section(text) == _list_section(bare.read_text(encoding="utf-8"))

def test_allele(tmp_path: Path):
    measures = tmp_path / "m.txt"
    measures.write_text("lmna,C>T\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "o", None, None, None, measures).read_text(encoding="utf-8")
    assert "对上这个突变" in text
    assert "20.8" not in text
    assert "24.1" not in text
