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

def test_cosinor_age_and_no_zero_fill(tmp_path: Path):
    from decimal import Decimal
    from presets import cosinor_age

    full = tmp_path / "full.txt"
    full.write_text("MESOR,30\namplitude,20\nacrophase,3.5\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "o", 60, None, None, full).read_text(encoding="utf-8")
    hat = cosinor_age(Decimal("30"), Decimal("20"), Decimal("3.5"), Decimal("60"))
    assert "58.52" in text
    assert hat is not None
    partial = tmp_path / "part.txt"
    partial.write_text("MESOR,30\nacrophase,3.5\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "p", 60, None, None, partial).read_text(encoding="utf-8")
    assert "不用 0 填" in bare
    assert "58.52" not in bare
    assert "76026" not in text
