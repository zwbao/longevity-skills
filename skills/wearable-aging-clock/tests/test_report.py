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
    # Missing PpgAge or age is now refused with exit code 3 (tests/test_manifest.py),
    # so the medicine, lab and boundary sections are checked on a computed report.
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value,unit\nppgage,70,岁\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas, 64)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 64)
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
    assert _opening(text).startswith(f"这次算出脉搏波年龄减去实足年龄是 {ppg_gap(70, 64):.1f} 年。")


from presets import (
    AGE_MAX,
    CODE_AGE_MAX,
    CODE_TRAIN_FRACTION,
    HEALTHY_N,
    MAE_HEALTHY_FEMALE,
    MAE_HEALTHY_MALE,
    MAE_POOLED,
    TRAIN_FRACTION_PAPER,
    TRAIN_N,
    WEIGHTS_PRESENT,
    ppg_gap,
)


def test_public_counts():
    assert HEALTHY_N == 6728
    assert TRAIN_N == 5355
    assert TRAIN_FRACTION_PAPER == 0.80
    assert CODE_TRAIN_FRACTION == 0.75
    assert AGE_MAX == 85
    assert CODE_AGE_MAX == 90
    assert MAE_POOLED == 2.43
    assert MAE_HEALTHY_MALE == 2.42
    assert MAE_HEALTHY_FEMALE == 2.45
    assert WEIGHTS_PRESENT is False
    assert ppg_gap(70, 64) == 6


def test_gap_when_ppgage_supplied(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nppgage,70\nage,64\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "6.0 年" in text
    assert "2.43" in text
    assert "6728" not in text
    assert "建议停" not in text


def test_no_invented_age(tmp_path: Path):
    text = personal_report.report(tmp_path / "out", None, None, None).read_text(encoding="utf-8")
    assert "没有算出年龄差" in text
    assert "2.43" not in text
