import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import (
    BOUNDARY,
    FIG2_REGULONS,
    N_EREGULONS_PD,
    N_TRAITS,
    THETA,

)


def test_public_counts():
    assert N_EREGULONS_PD == 77
    assert N_TRAITS == 31
    assert THETA == 0.5
    assert FIG2_REGULONS[2] == "FOXO1"



def test_formula(tmp_path: Path):
    got = personal_report.trait_regulon_score(0, 2)
    assert abs(got - (2 - 2 ** 0.5)) < 1e-12
    assert personal_report.trait_regulon_score(2, 2) == 4
    meas = tmp_path / "measurements.csv"
    meas.write_text("regulon,cts,grs\nFOXO1,2,2\nZEB1,0,2\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert text.index("FOXO1") < text.index("ZEB1")



def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text('regulon,cts,grs\nFOXO1,2,2\nZEB1,0,2\n', encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text('不存在的药\n', encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas)
    full = personal_report.report(tmp_path / "full", meds, labs, meas)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert '不存在的药' in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(bare.read_text(encoding="utf-8"), "## 方法算出的名单")
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert text.index("FOXO1") < text.index("ZEB1")

