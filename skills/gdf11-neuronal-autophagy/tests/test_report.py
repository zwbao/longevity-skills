import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, FIRST_WAVE_N, MEDIAN_CONTROL_PG_ML, MEDIAN_MDD_PG_ML


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_public_counts():
    assert FIRST_WAVE_N == 1560
    assert MEDIAN_CONTROL_PG_ML == 22.69
    assert MEDIAN_MDD_PG_ML == 11.66


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("name,value\nserum_gdf11_pg_ml,12.5\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("舍曲林\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas, 50)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 50)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "舍曲林" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(
        bare.read_text(encoding="utf-8"), "## 方法算出的名单"
    )
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "12.5" in text
    assert "1560" not in text
    assert "22.69" not in text
    assert "11.66" not in text
    assert "mg/kg" not in text
    assert "建议停" not in text
    assert "该开始" not in text
