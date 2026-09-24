import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, ORGANS


def test_gap_is_predicted_minus_chronological():
    assert personal_report.age_gap(70, 60) == 10
    assert personal_report.age_gap(55.5, 60) == -4.5
    assert sum(loci for _key, _label, loci, _h2 in ORGANS) == 393
    heritability = {key: h2 for key, _label, _loci, h2 in ORGANS}
    assert heritability["brain"] == 0.47
    assert heritability["immune"] == 0.21
    assert heritability["eye"] == 0.38


def test_labs_do_not_change_the_nine_organs(tmp_path: Path):
    predicted = tmp_path / "pred.csv"
    predicted.write_text("organ,predicted_age\ncardiovascular,70\nnot-an-organ,80\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("氨氯地平\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n肌酐,130,µmol/L\n", encoding="utf-8")
    full = personal_report.write_report(tmp_path / "full", predicted, 60, meds, labs)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "体检不增删" in text
    assert "2444" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "氨氯地平" in text
    assert "肌酐 130 µmol/L" in text
    assert "心血管：预测年龄 70 岁，年龄差 10.00 岁" in text
    assert "不加入方法名单" in text
    assert "not-an-organ" not in personal_report.method_section(text)
    bare = personal_report.write_report(tmp_path / "bare", predicted, 60, None, None)
    assert personal_report.method_section(bare.read_text(encoding="utf-8")) == personal_report.method_section(text)
    empty = personal_report.write_report(tmp_path / "empty", None, 60, None, None)
    empty_text = empty.read_text(encoding="utf-8")
    assert "没有这些器官的预测年龄" in empty_text
    assert "心血管" not in personal_report.method_section(empty_text)
    assert "建议停" not in text
    assert "该开始" not in text


def test_skill_metadata():
    root = Path(__file__).resolve().parents[1]
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    assert "disable-model-invocation" not in skill
    description = skill.split("description:", 1)[1].split("---", 1)[0]
    assert len(description) < 1024
    examples = (root / "examples.md").read_text(encoding="utf-8").strip()
    assert "personal_report.py" in examples
