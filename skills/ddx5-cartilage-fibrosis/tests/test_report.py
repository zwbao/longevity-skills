import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, COHORT_PROTEINS


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    meas = tmp_path / "measurements.csv"
    meas.write_text("name,value\nFN1_delta_psi,0.25\nFN1_fdr,1e-9\nCOL1A1,5\n", encoding="utf-8")
    bare = personal_report.write_report(tmp_path / "bare", meas, meds, None, 50)
    full = personal_report.write_report(tmp_path / "full", meas, meds, labs, 50)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "不存在的药" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    section = personal_report.method_section(text)
    assert section == personal_report.method_section(bare.read_text(encoding="utf-8"))
    assert "FN1" in section
    assert "COL1A1" not in section
    assert str(COHORT_PROTEINS) not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "该开始" not in text
    assert "建议停" not in text


def test_skill_metadata():
    root = Path(__file__).resolve().parents[1]
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    assert "disable-model-invocation" not in skill
    assert len(skill.splitlines()) < 200
    description = skill.split("description:", 1)[1].split("---", 1)[0]
    assert len(description) < 1024
    examples = (root / "examples.md").read_text(encoding="utf-8").strip()
    assert examples.startswith("```bash")
    assert "personal_report.py" in examples
    assert "GEO" not in examples
