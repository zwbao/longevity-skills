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
    assert _opening(text) == "套索系数是给标准化甲基化用的，训练均值和标准差不在表里。这次没有对上时钟位点，也没有成对的父本与母本甲基化，所以没有算出甲基化年龄。"


from presets import CLOCK, CLOCK_INTERCEPT, N_CLOCK_CPG, TEST_MEDAE, TRAIN_MEDAE, absolute_error, clock_age


def test_error_and_diras3(tmp_path: Path):
    assert absolute_error(60, 55) == 5
    assert TRAIN_MEDAE == 2.22
    assert TEST_MEDAE == 2.43
    meas = tmp_path / "measurements.csv"
    meas.write_text(
        "item,value,locus,paternal,maternal\n"
        "methylation_age,60,,,\n"
        "age,55,,,\n"
        ",,DIRAS3,0.80,0.20\n",
        encoding="utf-8",
    )
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "绝对误差是 5.00 年" in text
    assert "0.6000" in text
    assert "2.43" in text
    assert "2.22" not in text
    assert "没有给这个差值切点" in text
    assert "1373" not in text


def test_one_standardized_site(tmp_path: Path):
    assert N_CLOCK_CPG == 1373
    assert len(CLOCK) == 1373
    assert CLOCK_INTERCEPT == 48.573726207
    assert CLOCK["chr14_33962739_33962739"] == 0.034842023
    age, used = clock_age({"chr14_33962739_33962739": 1.0})
    assert used == 1
    assert abs(age - (48.573726207 + 0.034842023)) < 1e-9
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nchr14_33962739_33962739,1\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "甲基化年龄是 48.61 岁" in text
    assert "原始比例没有重缩放" in text
    assert "1373" not in text
    assert "2.22" not in text
