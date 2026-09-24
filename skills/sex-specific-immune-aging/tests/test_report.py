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


from presets import BOUNDARY, DONORS, FEATURES_BOTH, FULL_TEXT_READ, LEAD, MEASUREMENT


def test_weights_are_not_applied(tmp_path: Path):
    assert FULL_TEXT_READ is True
    assert DONORS == 1828
    assert FEATURES_BOTH == 6322
    measurements = tmp_path / "m.csv"
    measurements.write_text("name,value\n示例指标,1\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n血小板,90,10^9/L\n", encoding="utf-8")
    full = personal_report.write_report(tmp_path / "full", measurements, meds, labs)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert _opening(text) == LEAD
    assert "手头没有全文" not in text
    assert MEASUREMENT in personal_report.method_section(text)
    assert "1828" not in text
    assert "6322" not in text
    assert "不能据此停" in text
    assert "不存在的药" in text
    assert "血小板 90" in text
    assert "不增删" in text
    assert "示例指标" not in personal_report.method_section(text)
    assert personal_report.method_section(text).strip().endswith("名单是空的。")
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    bare = personal_report.write_report(tmp_path / "bare", measurements, None, None)
    assert personal_report.method_section(bare.read_text(encoding="utf-8")) == personal_report.method_section(text)
    assert "建议停" not in text
    assert "该开始" not in text


def test_skill_metadata():
    root = Path(__file__).resolve().parents[1]
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    assert "disable-model-invocation" not in skill
    description = skill.split("description:", 1)[1].split("---", 1)[0]
    assert len(description) < 1024
    examples = (root / "examples.md").read_text(encoding="utf-8").strip()
    assert examples.startswith("```bash")
    assert "personal_report.py" in examples
    assert "GEO" not in examples
