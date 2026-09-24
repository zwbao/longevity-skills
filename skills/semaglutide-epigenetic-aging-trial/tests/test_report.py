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
    assert _opening(text) == "没有同时提供某个时钟的基线和第 32 周数值，所以这次没有算出变化。组间差别不是个人权重。"
    assert "-4.9" not in text


from presets import GROUP_EFFECTS, week32_delta


def test_delta_is_not_the_group_effect(tmp_path: Path):
    assert week32_delta(54, 50) == -4
    assert GROUP_EFFECTS["PhenoAge"]["estimate"] == -4.9
    assert GROUP_EFFECTS["DunedinPACE"]["unit"] == "units"
    meas = tmp_path / "measurements.csv"
    meas.write_text("clock,baseline,week32\nPhenoAge,54,50\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("司美格鲁肽\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meds, None, meas).read_text(encoding="utf-8")
    assert "32 周变化是 -4.0" in text
    assert "-4.9 years/year" in text
    assert "司美格鲁肽：名单里没有这个名字。不能据此停。" in text
    assert "45" not in text
    assert "39" not in text
    assert "建议停" not in text
