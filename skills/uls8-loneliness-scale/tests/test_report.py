"""Report wording: score only, no invented bands, hotline always, no diagnosis."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
from presets import BOUNDARY, KEYS, REVERSED

MIXED = {key: 3 for key in KEYS}


def _report(tmp_path: Path, answers: dict) -> str:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "m.csv"
    path.write_text("item,value,unit\n" + "".join(f"{k},{v},\n" for k, v in answers.items()), encoding="utf-8")
    personal_report.main(["--measurements", str(path), "--out", str(tmp_path / "out")])
    return (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


def test_score_without_invented_bands(tmp_path: Path):
    text = _report(tmp_path, MIXED)
    assert text.splitlines()[0] == "# ULS-8 孤独感量表"
    assert "## 论文卡片" in text
    assert "没有找到这个量表公认的分档切点" in text
    for label in ("低度孤独", "中度孤独", "高度孤独", "重度孤独", "Moderate", "Severe", "0-100", "邓巴"):
        assert label not in text
    assert "反向计分" in text
    assert text.rstrip().splitlines()[-1] == f"边界: {BOUNDARY}"


def test_hotline_and_concrete_steps_in_every_report(tmp_path: Path):
    least = {key: (4 if key in REVERSED else 1) for key in KEYS}
    for name, answers in (("low", least), ("mixed", MIXED)):
        text = _report(tmp_path / name, answers)
        assert "12356" in text and "400-161-9995" in text and "120 或 110" in text
        assert "主动联系" in text
        assert "你患有" not in text and "诊断为" not in text
        assert "剂量" not in text


def test_lowest_score_is_celebrated(tmp_path: Path):
    least = {key: (4 if key in REVERSED else 1) for key in KEYS}
    text = _report(tmp_path, least)
    assert "最低分" in text and "很好的状态" in text


def test_item_two_gets_a_tailored_step(tmp_path: Path):
    text = _report(tmp_path, dict(MIXED, uls8_item2=4))
    assert "第 2 题（有没有可以求助的人）" in text
