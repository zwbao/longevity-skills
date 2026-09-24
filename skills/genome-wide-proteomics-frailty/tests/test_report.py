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
    assert _opening(text) == "没有对上诊断编码，也没有现成的医院衰弱风险分，所以这次没有分组。"


from presets import DEMENTIA_CODES, HFRS_ITEMS, hfrs_bin


def test_bins():
    assert len(HFRS_ITEMS) == 109
    assert HFRS_ITEMS[0][0] == "F00"
    assert HFRS_ITEMS[0][1] == 7.1
    assert HFRS_ITEMS[-1][0] == "R50"
    assert HFRS_ITEMS[-1][1] == 0.1
    assert abs(sum(weight for _code, weight, _zh, _desc in HFRS_ITEMS) - 173.2) < 1e-9
    assert DEMENTIA_CODES == frozenset({"F00", "F01", "F03", "G30"})
    assert hfrs_bin(4.9) == "低"
    assert hfrs_bin(5) == "中间"
    assert hfrs_bin(15) == "中间"
    assert hfrs_bin(15.01) == "高"


def test_icd_sum(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nF00.1,1\nG81,1\nI50,1\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "11.5" in text
    assert "4.4" in text
    assert "阿尔茨海默病所致痴呆" in text
    assert "偏瘫" in text
    assert "「中间」" in text
    assert "「低」" in text
    assert "109" not in text
    assert "Supplementary" not in text


def test_supplied_score_not_icd_sum(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nhfrs,5\nI50,1\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "「中间」" in text
    assert "Supplementary" not in text
    assert "109" not in text
