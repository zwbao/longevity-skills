import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, FIG5A, FIG5B_SYMBOLS, N_FIG5A, N_FIG5B, PWAS_BONFERRONI_P


def test_fig5_counts_match_source_data():
    assert len(FIG5A) == N_FIG5A == 109
    assert len(FIG5B_SYMBOLS) == N_FIG5B == 75
    symbol, odds, p_value = FIG5A[0]
    assert symbol == "GDF15"
    assert odds == 1.56040666060851
    assert p_value < PWAS_BONFERRONI_P
    assert all(p_value < PWAS_BONFERRONI_P for _s, _o, p_value in FIG5A)


def test_cohort_odds_are_not_a_personal_score():
    from presets import DIRECT_OR_ONE_COPY, DIRECT_OR_TWO_COPIES, H2_LIABILITY

    assert H2_LIABILITY == 0.029
    assert DIRECT_OR_ONE_COPY == 1.14
    assert DIRECT_OR_TWO_COPIES == 1.29


def test_epsilon4_count_is_only_unambiguous():
    assert "2" in personal_report.epsilon4_count({"rs429358": "C/C", "rs7412": "C/C"})
    assert "1" in personal_report.epsilon4_count({"rs429358": "T/C", "rs7412": "C/C"})
    assert "0" in personal_report.epsilon4_count({"rs429358": "T/T", "rs7412": "C/C"})
    assert "相位不确定" in personal_report.epsilon4_count({"rs429358": "T/C", "rs7412": "C/T"})


def test_report_does_not_let_labs_or_extra_proteins_edit_the_list(tmp_path: Path):
    proteins = tmp_path / "proteins.csv"
    proteins.write_text("protein,value\nGDF15,1.2\nNOT_IN_PAPER,9\n", encoding="utf-8")
    genotypes = tmp_path / "gt.csv"
    genotypes.write_text("rsid,genotype\nrs429358,T/C\nrs7412,C/C\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("喹硫平\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n血红蛋白,90,g/L\n", encoding="utf-8")
    full = personal_report.write_report(tmp_path / "full", proteins, genotypes, meds, labs)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "喹硫平" in text
    assert "血红蛋白 90" in text
    assert "体检不增删" in text
    assert "NOT_IN_PAPER" not in personal_report.method_section(text)
    assert "GDF15" in personal_report.method_section(text)
    assert "你的表里记为 1.2" in personal_report.method_section(text)
    assert "32652" not in text
    assert "0.029" not in text
    assert "1.14" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    bare = personal_report.write_report(tmp_path / "bare", proteins, genotypes, None, None)
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
    assert "personal_report.py" in examples
    assert examples.count("```") == 2
