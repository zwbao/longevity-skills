import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, P8_GERM_CELLS


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


def test_formula():
    from presets import canonical_stage

    assert personal_report.reserve(100, 5, 100, 1.5) == (100 / 5) * 100 / 1.5
    assert canonical_stage("P8") == "p8"
    assert canonical_stage("P15") == "p15"


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text(
        "name,value\nstage,P8\nraw_count,100\nsections_counted,5\ntotal_sections,100\n",
        encoding="utf-8",
    )
    meds = tmp_path / "meds.txt"
    meds.write_text("布洛芬\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meds, None, meas)
    full = personal_report.report(tmp_path / "full", meds, labs, meas)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "布洛芬" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert listed(text) == listed(bare.read_text(encoding="utf-8"))
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert str(P8_GERM_CELLS) not in text
    assert "1333.33" in text
    assert "校正因子：1.5" in text
