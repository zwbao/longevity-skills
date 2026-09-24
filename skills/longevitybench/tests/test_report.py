import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import drugage
import personal_report
from control_laws import control_law_analysis
from drugage import DrugStudy, load_drugage, rank_compounds, score_compound
from presets import (
    AGE_50_CONTROL_COST,
    AGE_50_SEQUENCE,
    BOUNDARY,
    DRUGAGE_COMPOUNDS,
    DRUGAGE_DATA_ROWS,
    DRUGAGE_ITP_COMPOUNDS,
    DRUGAGE_RANKED_MIN2,
    RAPAMYCIN_MEAN_CHANGE,
    RAPAMYCIN_SCORE,
    RAPAMYCIN_SPECIES,
    RAPAMYCIN_STUDIES,
)


def test_snapshot_counts_match_longeclaw_file():
    studies = load_drugage(personal_report.bundled_drugage())
    assert len(studies) == DRUGAGE_DATA_ROWS
    assert drugage.count_compounds(studies) == DRUGAGE_COMPOUNDS
    assert drugage.count_itp_compounds(studies) == DRUGAGE_ITP_COMPOUNDS
    ranked = rank_compounds(studies)
    assert len(ranked) == DRUGAGE_RANKED_MIN2
    rapamycin = next(item for item in ranked if item.compound == "Rapamycin")
    assert rapamycin.longevity_score == RAPAMYCIN_SCORE
    assert rapamycin.n_studies == RAPAMYCIN_STUDIES
    assert rapamycin.n_species == RAPAMYCIN_SPECIES
    assert rapamycin.mean_lifespan_change == RAPAMYCIN_MEAN_CHANGE


def test_score_formula_on_a_hand_built_compound():
    studies = [
        DrugStudy("Example", "Mus musculus", "", "", 50.0, None, "", "", "", False, ""),
        DrugStudy("Example", "Mus musculus", "", "", 50.0, None, "", "", "", False, ""),
    ]
    score = score_compound("Example", studies)
    assert score is not None
    assert score.longevity_score == 0.65
    assert score.n_species == 1
    assert score.itp_validated is False


def test_age_50_vector_field_matches_longeclaw():
    analysis = control_law_analysis(50)
    assert analysis["initial_biological_age"] == pytest.approx(AGE_50_CONTROL_COST)
    assert analysis["optimal_sequence"] == AGE_50_SEQUENCE
    keys = [row["key"] for row in analysis["intervention_rankings"]]
    assert keys[0] == "caloric_restriction"
    assert "metformin" in keys
    assert "fisetin" in keys


def test_report_keeps_boundary_and_does_not_drop_compounds(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林肠溶片\n不存在的药\n二甲双胍\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    out = tmp_path / "out"
    path = personal_report.report(out, 50, meds, labs, None, 10)
    text = path.read_text(encoding="utf-8")
    assert f"边界: {BOUNDARY}" in text
    assert "阿司匹林" in text
    assert "不能据此停药" in text
    assert "名次不是继续或停用的理由" in text
    assert "这不是停用的理由" in text
    assert "不增删化合物" in text
    assert "谷丙转氨酶 80" in text
    bare = personal_report.report(tmp_path / "bare", 50, None, None, None, 10)
    bare_top = [line for line in bare.read_text(encoding="utf-8").splitlines() if line.startswith("1. ")]
    full_top = [line for line in text.splitlines() if line.startswith("1. ")]
    assert bare_top[0] == full_top[0]
    assert "该开始" not in text
    assert "建议停" not in text
