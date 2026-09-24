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

def test_counts_days_and_z(tmp_path: Path):
    assert UKB_N == 43616 and TRAIN_N == 30536
    assert ENRICHED_PROTEINS == 418 and BRAIN_ENRICHED == 117
    assert ORGANISMAL_PROTEINS == 240 and HEART_PROTEINS == 5
    assert ORGANISMAL_R == 0.94 and BRAIN_R == 0.78
    assert CROSS_COHORT_R == (0.98, 0.93)
    assert CODE_TEST_SIZE == 0.3 and CODE_RANDOM_STATE == 1996
    assert len(ORGANS) == 11
    assert len(ORGAN_CLOCK_PROTEINS["heart"]) == HEART_PROTEINS == 5
    assert ORGAN_CLOCK_PROTEINS["heart"][0] == ("BMP10", "Bone morphogenetic protein 10")
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\ndays,36525\norgan_skip,0\n", encoding="utf-8")
    # days via item,value; z via a second file shape
    meas.write_text("organ,z,days\nbrain,1.8,36525\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "100.0000" in text
    assert "高于 1.5 个标准差" in text
    assert "标题不写" not in text



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

