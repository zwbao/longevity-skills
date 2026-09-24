import math
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, PHENOAGE_BIOMARKERS


FIXTURE = {
    "albumin_gL": 45,
    "creat_umol": 80,
    "glucose_mmol": 5.0,
    "crp_mg_dl": 0.2,
    "lymph_pct": 32,
    "mcv_fl": 90,
    "rdw_pct": 13.2,
    "alp_u_l": 70,
    "wbc_10e3": 6.5,
    "age": 58,
}


def _biomarkers(path: Path) -> Path:
    rows = ["marker,value"]
    for key, _label, _unit in PHENOAGE_BIOMARKERS:
        rows.append(f"{key},{FIXTURE[key]}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


def test_phenotypic_age_matches_phenoage_calc_orig():
    age = personal_report.phenotypic_age(FIXTURE, "ln")
    assert age == pytest.approx(50.475248839667486)
    assert personal_report.age_advance(age, FIXTURE["age"]) == pytest.approx(-7.524751160332514)
    assert personal_report.phenotypic_age(FIXTURE, "log1p") == pytest.approx(52.37039480753462)
    assert age != pytest.approx(FIXTURE["age"])
    assert math.isfinite(age)


def test_printed_cutoffs():
    assert personal_report.bmi_class(24) == "体重正常或偏低"
    assert personal_report.bmi_class(25) == "超重"
    assert personal_report.bmi_class(30) == "肥胖"
    assert personal_report.body_mass_index(None, 1.7, 85) == pytest.approx(85 / 1.7**2)
    assert personal_report.childhood_score([0, 0, 0, 0, 0]) == 2
    assert personal_report.childhood_score([4, 4, 4, 4, 4]) == 3


def test_missing_marker_does_not_invent_an_age(tmp_path: Path):
    path = tmp_path / "bio.csv"
    _biomarkers(path)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("albumin_gL,45\n", ""), encoding="utf-8")
    report = personal_report.write_report(tmp_path / "out", path, 58, "女", None, None, None)
    body = report.read_text(encoding="utf-8")
    assert "没有表型年龄" in body
    assert "KDM" not in body
    assert "1.113" not in body
    assert "50.48" not in body


def test_report_boundary_medicines_and_labs(tmp_path: Path):
    bio = _biomarkers(tmp_path / "bio.csv")
    meds = tmp_path / "meds.txt"
    meds.write_text("二甲双胍\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    phq = tmp_path / "phq.txt"
    phq.write_text("1\n2\n0\n0\n", encoding="utf-8")
    report = personal_report.write_report(tmp_path / "out", bio, 58, "女", meds, labs, phq)
    text = report.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "体检不增删" in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "二甲双胍" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert "前两项达到抑郁筛查线" in text
    assert "合计没有达到筛查线" in text
    assert "表型年龄减去实足年龄是 -7.52 岁" in text
    assert "残差没有计算" in text
    assert "建议停" not in text
    assert "该开始" not in text
    bare = personal_report.write_report(tmp_path / "bare", bio, 58, None, None, None, None)
    bare_age = [line for line in bare.read_text(encoding="utf-8").splitlines() if line.startswith("实足年龄")]
    full_age = [line for line in text.splitlines() if line.startswith("实足年龄")]
    assert bare_age == full_age
    bare_list = [line for line in bare.read_text(encoding="utf-8").splitlines() if line.startswith("- 白蛋白")]
    full_list = [line for line in text.splitlines() if line.startswith("- 白蛋白")]
    assert bare_list == full_list
    phq9 = tmp_path / "phq9.txt"
    phq9.write_text("1 0 0 0 0 0 0 0 0\n", encoding="utf-8")
    gad7 = tmp_path / "gad7.txt"
    gad7.write_text("3 3 3 3 0 0 0\n", encoding="utf-8")
    childhood = tmp_path / "cts.txt"
    childhood.write_text("never rarely sometimes often veryoften\n", encoding="utf-8")
    extra = personal_report.write_report(
        tmp_path / "extra",
        bio,
        58,
        "女",
        None,
        labs,
        None,
        bmi=31,
        alcohol_g=20,
        moderate_min=0,
        vigorous_min=0,
        mixed_min=0,
        sbp=150,
        phq9=phq9,
        gad7=gad7,
        childhood=childhood,
    )
    extra_text = extra.read_text(encoding="utf-8")
    extra_age = [line for line in extra_text.splitlines() if line.startswith("实足年龄")]
    assert extra_age == bare_age
    assert "属于肥胖" in extra_text
    assert "不算健康饮酒" in extra_text
    assert "不算健康活动" in extra_text
    assert "达到论文写出的 140 mmHg" in extra_text
    assert "抑郁九项合计 1：合计没有达到症状线" in extra_text
    assert "自杀意念" in extra_text
    assert "焦虑七项合计 12：合计达到症状线" in extra_text
    assert "童年逆境五项合计 3" in extra_text
    assert "谷丙转氨酶 80 U/L" in extra_text


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
