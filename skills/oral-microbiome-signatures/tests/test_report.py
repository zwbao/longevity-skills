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

def test_counts_and_omaa(tmp_path: Path):
    assert TOTAL_N == DISCOVERY_N + VALIDATION_N == 4675
    assert GENERA == 64 and EXTERNAL_GENERA == 37
    assert DISC_RHO == 0.44 and DISC_MAE == 8.69
    assert EXT_MAE == 12.63 and MORT_HR == 1.05
    assert STOMATOBACULUM_EDF == 5.17
    assert CLOP_DISC_USERS == 43 and CLOP_VAL_NONUSERS == 2614
    assert len(AGE_GENERA) == GENERA == 64
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nomaa,0.4\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("氯吡格雷\n阿司匹林肠溶片\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meds, None, meas).read_text(encoding="utf-8")
    assert "大于 0" in text
    assert "不能据此停" in text
    assert "阿司匹林肠溶片：名单里没有这个名字" in text
    assert "标题不写" not in text
    assert "43" not in text



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

