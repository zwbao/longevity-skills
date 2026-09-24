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

def test_partial_mean_is_not_the_clock(tmp_path: Path):
    assert INSPIRE_N == 1014 and DNAM_N == 933 and CPGS == 91 and ALPHA == 0.9
    assert IC_CORRELATION == 0.61 and MORTALITY_HR == 1.38 and FHS_MORTALITY_N == 1680
    assert WEIGHTS_PRESENT is True
    assert len(CPG_COEF) == CPGS
    assert IC_INTERCEPT == 0.7852837523517947
    meas = tmp_path / "m.csv"
    meas.write_text("item,value\nmmse,30\nsppb,12\nphq9,0\nvision,3\nhearing,2\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "平均是 1.00" in text
    assert "不是论文的 IC" in text
    assert "1.38" not in text
    assert "标题不写" not in text



def test_zero_betas_equal_intercept(tmp_path: Path):
    lines = ["item,value"] + [f"{site},0" for site in CPG_COEF]
    meas = tmp_path / "m.csv"
    meas.write_text("\n".join(lines) + "\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert f"{IC_INTERCEPT:.6f}" in text
    assert "甲基化内在能力" in text
    assert "1.38" not in text


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

