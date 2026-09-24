import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report

def _opening(text: str) -> str:
    lines = text.splitlines()
    try:
        start = lines.index("## 论文卡片")
    except ValueError:
        return lines[2]
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            j = i - 1
            while j > start and lines[j] == "":
                j -= 1
            return lines[j]
    return lines[2]


from presets import BOUNDARY


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, None)
    full = personal_report.report(tmp_path / "full", meds, labs, None)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "不存在的药" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(
        bare.read_text(encoding="utf-8"), "## 方法算出的名单"
    )
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "标题不写" not in text
    assert "这篇论文的个人读出" not in text
    assert _opening(text) == "没有提供睡眠小时数，所以这次没有分组。"

from presets import (
    BRAIN_MIN_HOURS_FEMALE,
    MORTALITY_SHORT_HR,
    N_BAGS,
    N_SIGNIFICANT_NONLINEAR,
    sleep_bin,
)


def test_public_counts():
    assert N_BAGS == 23
    assert N_SIGNIFICANT_NONLINEAR == 9
    assert BRAIN_MIN_HOURS_FEMALE == 7.82
    assert MORTALITY_SHORT_HR == 1.50
    assert sleep_bin(5.9) == "短"
    assert sleep_bin(6) == "正常"
    assert sleep_bin(8) == "正常"
    assert sleep_bin(8.1) == "长"


def test_bin_not_curve_minimum(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nsleep_hours,7.82\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "「正常」" in text
    assert "1.50" not in text
    assert "7.82" not in text
