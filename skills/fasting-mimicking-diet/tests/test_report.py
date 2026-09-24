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


from presets import *

def test_delta_and_trial_counts(tmp_path: Path):
    assert NHANES_N == 10519 and COMPLETERS == 52 and CONTROL_N == 19
    assert MEDIAN_DECREASE_NEARLY == 2.5 and CONTROL_MEAN_INCREASE == 0.78
    assert POOLED_N == 86 and AT_RISK_BASELINE == 43.3 and AT_RISK_FOLLOWUP == 40.4
    assert len(BIOMARKERS) == 7 and WEIGHTS_PRESENT is True
    assert S_BA_PUBLISHED is False
    assert len(KDM) == 7
    meas = tmp_path / "m.csv"
    meas.write_text("item,value\nbiological_age_baseline,50\nbiological_age_followup,47.5\nglucose,110\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "-2.5 年" in text
    assert "空腹血糖是 110" in text
    assert "仿断食" not in text
    assert "标题不写" not in text



def test_change_equation(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("item,value\nbiological_age_baseline,45\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas, 50).read_text(encoding="utf-8")
    change = CHANGE_INTERCEPT + CHANGE_ON_BIOAGE * 45 + CHANGE_ON_AGE * 50
    assert f"{change:.4f}" in text
    assert "仿断食" not in text


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
    first = _opening(bare.read_text(encoding="utf-8"))
    assert first.endswith("。")
    assert "标题不写" not in first
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

