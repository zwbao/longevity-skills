import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import ARRAYEXPRESS, BOUNDARY, MOUSE_PHARM_FINDINGS, PATHWAY_NODES

SAMPLE = """name,value
endothelial_cebpb,有
endothelial_aep,有
nampt_cleavage,有
nad_level,无
"""


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\nNMN\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    meas = tmp_path / "measurements.csv"
    meas.write_text(SAMPLE, encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas, 70)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 70)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(
        bare.read_text(encoding="utf-8"), "## 方法算出的名单"
    )
    assert "该开始" not in text
    assert "建议停" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    for name in PATHWAY_NODES:
        assert name in text
    assert MOUSE_PHARM_FINDINGS[0] in text
    assert "你标的是存在/偏高" in text
    assert "你标的是缺失/偏低" in text
    assert ARRAYEXPRESS not in _section(text, "## 方法算出的名单")
    assert ARRAYEXPRESS == "E-MTAB-17006"
    assert "## 论文卡片" in text
    assert "10.1126/sciadv.aed1961" in text
