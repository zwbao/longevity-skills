import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, FIG1_OLD_FEMALE_CELLS, GENES, MEAN_SD_PRESENT


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_gene_table():
    assert FIG1_OLD_FEMALE_CELLS == 160
    assert MEAN_SD_PRESENT is False
    assert GENES[0] == ("LAMP2", 1, 2)
    assert len(GENES) == 18
    assert sum(weight for _gene, _direction, weight in GENES) == 19


def test_percent():
    assert personal_report.as_float("10") == 10
    kv = {"kdendralamp1puncta": "10", "lamp1puncta": "40"}
    assert "25.0%" in personal_report.competence(kv)


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("name,value\nkdendra_lamp1_puncta,10\nlamp1_puncta,40\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas, 50)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 50)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "阿司匹林" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(
        bare.read_text(encoding="utf-8"), "## 方法算出的名单"
    )
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "25.0%" in text
    assert "160" not in text
    assert "均值列" in text
    assert "建议停" not in text
    assert "该开始" not in text
