import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, COHORT_RISK_RATIO, FLY_FOOD_UM, FLY_N, MOUSE_EARLY_PPM, MOUSE_LATE_PPM

MEAS = "name,value\ngfp_area,4\ntotal_area,8\n"

def _section(text, heading):
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])

def test_public_counts():
    assert FLY_N == 400
    assert FLY_FOOD_UM == 200
    assert MOUSE_EARLY_PPM == 14
    assert MOUSE_LATE_PPM == 42
    assert COHORT_RISK_RATIO == 0.4309059

def test_turnover_ratio():
    assert personal_report.turnover_ratio(4, 8) == 0.5

def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text(MEAS, encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("没有这种药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meds, None, meas, 60)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 60)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80" in text
    assert "肠上皮更新比例是 0.5" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    assert _section(text, "## 方法算出的名单") == _section(bare.read_text(encoding="utf-8"), "## 方法算出的名单")
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert str(FLY_N) not in text
    assert "0.4309059" not in text
    assert "不是给你的用法" in text
