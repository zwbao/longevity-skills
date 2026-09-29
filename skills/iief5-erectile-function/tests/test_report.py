"""Report wording: refer at 21 or less with a cardiovascular check, no diagnosis, no medicine advice."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
from presets import BOUNDARY, KEYS


def _report(tmp_path: Path, per_item: int, *flags: str) -> str:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "m.csv"
    path.write_text("item,value,unit\n" + "".join(f"{k},{per_item},\n" for k in KEYS), encoding="utf-8")
    personal_report.main(["--measurements", str(path), "--sex", "male", *flags, "--out", str(tmp_path / "out")])
    return (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


def test_no_ed_band_is_good_news_without_referral(tmp_path: Path):
    text = _report(tmp_path, 5, "--age", "50")
    assert "得分是 **25**" in text and "好消息" in text
    assert "为什么也要查心血管" not in text
    assert text.rstrip().splitlines()[-1] == f"边界: {BOUNDARY}"


def test_low_score_refers_to_doctor_and_cardiovascular_check(tmp_path: Path):
    text = _report(tmp_path, 3, "--age", "50")  # 15, mild to moderate
    assert "「轻到中度」" in text
    assert "提示可能存在轻到中度勃起功能障碍，请男科或泌尿外科医生评估" in text
    assert "心血管风险评估" in text and "2 到 5 年" in text
    assert "China-PAR" in text and "10 年心血管病风险" in text
    assert "china-par-ascvd-risk" not in text  # plain words for the person, the skill name is in SKILL.md
    assert "不要因为这个结果自己停药或换药" in text
    for word in ("你患有", "诊断为", "西地那非", "他达拉非", "sildenafil", "tadalafil", "剂量"):
        assert word not in text


def test_age_outside_china_par_is_named(tmp_path: Path):
    text = _report(tmp_path, 2, "--age", "30")
    assert "35–74 岁" in text and "请医生评估" in text


def test_scope_and_copyright_notes(tmp_path: Path):
    text = _report(tmp_path, 4)
    assert "过去 6 个月尝试过性交的男性" in text
    assert "Mapi Research Trust" in text
    assert "## 论文卡片" in text and "doi.org/10.1038/sj.ijir.3900472" in text
