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

def test_public_counts_and_z_rule(tmp_path: Path):
    assert UKB_N == 44498
    assert PROTEINS == 2916
    assert TRAIN_N == 23140 and TEST_N == 21358
    assert LASSO_PERFORMANCE == 0.95
    assert EXTREME_Z == 1.5
    assert AD_AGED_HR == 3.1 and AD_YOUTHFUL_HR == 0.26
    assert MORT_HR["2-4"] == 2.3 and MORT_HR["8+"] == 8.3
    assert len(ORGANS) == 11
    assert WEIGHTS_PRESENT is True
    assert NONZERO_COEFS["heart"] == 2
    assert MODEL_COEF["heart"]["ntprobnp"] == 2.3395380862837505
    assert MODEL_INTERCEPT["heart"] == 57.09454940056831
    meas = tmp_path / "measurements.csv"
    meas.write_text("organ,z\nbrain,1.6\nimmune,-1.6\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas, 60).read_text(encoding="utf-8")
    assert "脑" in text and "免疫" in text
    assert "3.1" in text
    assert "0.58" not in text
    assert "标题不写" not in text
    assert text.splitlines()[0].find("3.1") < 0



def test_heart_linear_combination(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nntprobnp,1\nbmp10,1\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas, 60).read_text(encoding="utf-8")
    expected = MODEL_INTERCEPT["heart"] + MODEL_COEF["heart"]["ntprobnp"] + MODEL_COEF["heart"]["bmp10"]
    assert f"{expected:.4f}" in text
    assert "心脏" in text
    assert "3.1" not in text


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

