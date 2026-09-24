import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BIOPROJECT, BOUNDARY, LNHR_HUMAN_LIFESPAN


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


def test_public_numbers():
    assert personal_report.nhej_frequency(10, 4) == 2.5
    assert LNHR_HUMAN_LIFESPAN == -0.31
    assert BIOPROJECT == "PRJNA1314725"


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("name,value\nspecies,bowhead\ngfp,10\nd sred,4\n".replace("d sred", "dsred"), encoding="utf-8")
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
    assert "体检不增删" in text
    assert listed(text) == listed(bare.read_text(encoding="utf-8"))
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert BIOPROJECT not in text
    assert "-0.31" not in text
    assert "2.5" in text
    assert "TP53" in text
