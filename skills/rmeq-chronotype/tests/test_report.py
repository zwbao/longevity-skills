"""Report wording: a preference category, cross-references, no DLMO and no schedule prescriptions."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
from presets import BOUNDARY


def _report(tmp_path: Path, answers: dict) -> str:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "m.csv"
    path.write_text("item,value,unit\n" + "".join(f"{k},{v},\n" for k, v in answers.items()), encoding="utf-8")
    personal_report.main(["--measurements", str(path), "--out", str(tmp_path / "out")])
    return (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


EVENING = {"rmeq_item1": 1, "rmeq_item2": 1, "rmeq_item3": 1, "rmeq_item4": 2, "rmeq_item5": 0}  # 5
MORNING = {"rmeq_item1": 5, "rmeq_item2": 4, "rmeq_item3": 5, "rmeq_item4": 5, "rmeq_item5": 6}  # 25


def test_evening_and_morning_reports(tmp_path: Path):
    evening = _report(tmp_path / "e", EVENING)
    morning = _report(tmp_path / "m", MORNING)
    assert "得分是 **5**" in evening and "「明确夜型」" in evening
    assert "得分是 **25**" in morning and "「明确晨型」" in morning
    for text in (evening, morning):
        assert text.splitlines()[0] == "# rMEQ 晨型夜型问卷"
        assert "## 论文卡片" in text
        assert "不是病" in text
        assert "实际的休息和活动节律" in text
        assert "wearable-circadian-aging-biomarker" not in text  # skill names stay in SKILL.md
        assert text.rstrip().splitlines()[-1] == f"边界: {BOUNDARY}"


def test_no_dlmo_and_no_schedule_prescriptions(tmp_path: Path):
    text = _report(tmp_path, EVENING)
    for word in ("DLMO", "褪黑素", "lux", "光照疗法", "进食窗口", "16:8", "应该在", "点睡觉"):
        assert word not in text
    assert "你患有" not in text and "诊断为" not in text
