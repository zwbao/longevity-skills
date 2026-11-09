"""Report wording: paper card first, cohort numbers kept apart, boundary kept."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report  # noqa: E402
from presets import BOUNDARY  # noqa: E402

ROWS = "marker,value,unit\nMMSE,25,\nCDR,0.5,\nCDRSB,3,\nADAS11,16.67,\nADAS13,26,\nFAQ,9,\n"


def _report(tmp_path: Path, meds: str = "", labs: str = "") -> str:
    scores = tmp_path / "s.csv"
    scores.write_text(ROWS, encoding="utf-8")
    args = ["--scores", str(scores), "--out", str(tmp_path / "out")]
    if meds:
        (tmp_path / "m.txt").write_text(meds, encoding="utf-8")
        args += ["--medications", str(tmp_path / "m.txt")]
    if labs:
        (tmp_path / "l.csv").write_text(labs, encoding="utf-8")
        args += ["--labs", str(tmp_path / "l.csv")]
    assert personal_report.main(args) == 0
    return (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


def test_paper_card_precedes_result(tmp_path: Path):
    text = _report(tmp_path)
    card = text.index("## 论文卡片")
    result = text.index("## 结果")
    assert card < result
    head = text[card:result]
    assert "10.1007/s11357-026-02551-x" in head
    assert "Simkhada" in head and "GeroScience" in head and "2026" in head


def test_result_and_cohort_sections(tmp_path: Path):
    text = _report(tmp_path)
    result = text.split("## 结果", 1)[1].split("## 队列里的表现", 1)[0]
    assert "校准概率是 83.7%" in result
    assert "高于模型切点" in result
    assert "81.99" not in result and "4.73" not in result
    cohort = text.split("## 队列里的表现（不是你的结果）", 1)[1]
    assert "81.99" in cohort and "4.73" in cohort
    assert "323 项 FreeSurfer" in text


def test_unusual_scores_are_flagged(tmp_path: Path):
    text = _report(tmp_path)
    assert "功能活动问卷（FAQ） 9" not in text
    assert "临床痴呆评定各项之和（CDR-SB） 3：" not in text
    scores = tmp_path / "far.csv"
    scores.write_text("marker,value,unit\nMMSE,20,\nCDR,1,\nCDRSB,6,\nADAS11,25,\nADAS13,38,\nFAQ,20,\n", encoding="utf-8")
    assert personal_report.main(["--scores", str(scores), "--out", str(tmp_path / "far")]) == 0
    far = (tmp_path / "far" / "report.md").read_text(encoding="utf-8")
    assert "训练人群里少见的数" in far and "功能活动问卷（FAQ） 20" in far


def test_boundary_and_medicines(tmp_path: Path):
    text = _report(tmp_path, meds="多奈哌齐\n", labs="项目,结果,单位\n总胆固醇,5.2,mmol/L\n")
    assert f"边界: {BOUNDARY}" in text
    assert "多奈哌齐：药物不是这个模型的输入，不改变上面的概率。不能据此开始或停止。" in text
    assert "总胆固醇 5.2 mmol/L" in text
    assert "体检不增删方法算出的结果" in text
    for word in ("建议服用", "建议停用", "mg/天", "剂量"):
        assert word not in text
