import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


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
    bare = personal_report.report(tmp_path / "bare", 60, meds, None, None)
    assert _list_section(text) == _list_section(bare.read_text(encoding="utf-8"))


def test_age_gap_and_mean(tmp_path: Path):
    from presets import age_gap
    assert age_gap(70, 60) == 10
    meas = tmp_path / "m.txt"
    meas.write_text(
        "brain 70\nheart 65\nbody 60\nkidney 80\nliver 62\npancreas 61\neye 59\nbrain_gm 72\n",
        encoding="utf-8",
    )
    text = personal_report.report(tmp_path / "o", 60, None, None, meas).read_text(encoding="utf-8")
    assert "年龄差 10" in text
    assert "七个器官的年龄差平均" in text
    assert "偏差校正的截距没有印在正文里" in text
    assert "脑" in text or "brain" in text
    bare = personal_report.report(tmp_path / "b", 60, None, None, None).read_text(encoding="utf-8")
    assert "七个器官的年龄差平均" not in bare
