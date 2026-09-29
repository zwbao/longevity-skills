"""CKD-EPI 2021 eGFR against the paper's own numbers, and KDIGO 2024 staging.

Expected eGFR values come only from Inker et al. 2021, Supplementary Appendix
Table S11 (simulated patients, printed as whole numbers). The table was not
generated with the rounded coefficients of Table 2: every cell is within 1
ml/min/1.73 m2 of our value, but neither half-up rounding nor truncation matches
all 48 cells (largest gap 0.96, i.e. under 1%), so the tolerance is 1.
Category boundaries come from KDIGO 2024 Tables 2 and 3. All inputs are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import (CR_2021, CR_CYS_2021, MONITORING_PER_YEAR, S11_CR, S11_CR_CYS, S11_SCR, UMOL_L_PER_MG_DL)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, age="50", sex="male", name="out"):
    m = _csv(tmp_path / f"{name}.csv", rows)
    out = tmp_path / name
    args = ["--measurements", str(m), "--out", str(out)]
    if age is not None:
        args += ["--age", age]
    if sex is not None:
        args += ["--sex", sex]
    code = pr.main(args)
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


def test_coefficients_are_table2_as_printed():
    assert (CR_2021["mu"], CR_2021["a2"], CR_2021["age"], CR_2021["female"]) == (142, -1.200, 0.9938, 1.012)
    assert CR_2021["kappa"] == {"female": 0.7, "male": 0.9}
    assert CR_2021["a1"] == {"female": -0.241, "male": -0.302}
    c = CR_CYS_2021
    assert (c["mu"], c["a2"], c["b1"], c["b2"], c["age"], c["female"], c["cys_knot"]) == (135, -0.544, -0.323, -0.778, 0.9961, 0.963, 0.8)
    assert c["a1"] == {"female": -0.219, "male": -0.144}
    assert UMOL_L_PER_MG_DL == 88.4


@pytest.mark.parametrize("key", sorted(S11_CR))
def test_table_s11_creatinine(key):
    sex, age = key
    for scr, printed in zip(S11_SCR, S11_CR[key]):
        assert pr.egfr_cr(scr, age, sex) == pytest.approx(printed, abs=1.0), (key, scr)


@pytest.mark.parametrize("key", sorted(S11_CR_CYS))
def test_table_s11_creatinine_cystatin(key):
    cys, sex, age = key
    for scr, printed in zip(S11_SCR, S11_CR_CYS[key]):
        assert pr.egfr_cr_cys(scr, cys, age, sex) == pytest.approx(printed, abs=1.0), (key, scr)


def test_units_convert_and_report_end_to_end(tmp_path: Path):
    # Table S11: man, 50 years, Scr 1 mg/dL -> eGFRcr 92; with cystatin C 1 mg/L -> eGFRcr-cys 88.
    code, result, report, _ = _run(tmp_path, [("肌酐", "1.0", "mg/dL"), ("胱抑素C", "1.0", "mg/L")], name="mgdl")
    assert code == 0
    assert result["egfr_cr"]["value"] == pytest.approx(92, abs=1)
    assert result["egfr_cr_cys"]["value"] == pytest.approx(88, abs=1)
    assert result["gfr_category"]["value"] == "G2"
    assert result["gfr_category_equation"]["value"] == "eGFRcr-cys"
    assert result["albuminuria_category"]["value"] is None
    assert result["doctor_visit"]["value"] == pr.VISIT_NONE
    code2, result2, _, _ = _run(tmp_path, [("血肌酐", str(UMOL_L_PER_MG_DL), "µmol/L"), ("Cys-C", "1.0", "mg/L")], name="umol")
    assert code2 == 0
    assert result2["egfr_cr"]["value"] == result["egfr_cr"]["value"]
    assert result2["egfr_cr_cys"]["value"] == result["egfr_cr_cys"]["value"]
    assert report.startswith(f"# {pr.TITLE}")
    assert "## 论文卡片" in report and "边界:" in report and "doi.org/10.1056/nejmoa2102953" in report


def test_creatinine_only_stages_on_egfr_cr(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("creatinine_umol_l", str(0.6 * UMOL_L_PER_MG_DL), "")], age="50", sex="female")
    assert code == 0
    assert result["egfr_cr"]["value"] == pytest.approx(109, abs=1)  # Table S11: woman, 50, Scr 0.6
    assert result["egfr_cr_cys"]["value"] is None
    assert result["gfr_category_equation"]["value"] == "eGFRcr"
    assert result["gfr_category"]["value"] == "G1"
    assert "好消息" not in report  # no albuminuria result, so not both halves normal
    assert "1.1.1.1" in report


def test_low_egfr_says_see_a_doctor_with_kdigo_retest(tmp_path: Path):
    # Table S11: woman, 75, Scr 1.5 -> 36 (G3b).
    code, result, report, _ = _run(tmp_path, [("Scr", "1.5", "mg/dL"), ("UACR", "12", "mg/g")], age="75", sex="female")
    assert code == 0
    assert result["gfr_category"]["value"] == "G3b"
    assert result["albuminuria_category"]["value"] == "A1"
    assert result["doctor_visit"]["value"] == pr.VISIT_SEE
    assert result["kdigo_checks_per_year"]["value"] == MONITORING_PER_YEAR["G3b"][0] == "2"
    assert "肾内科或内科" in report and "3 个月" in report and "1.1.1.2" in report
    assert "你患有" not in report


def test_egfr_below_30_is_referral(tmp_path: Path):
    # Table S11: woman, 75, Scr 2 -> 26 (G4); KDIGO Figure 48 lists eGFR <30 for specialist referral.
    code, result, report, _ = _run(tmp_path, [("Scr", "2.0", "mg/dL")], age="75", sex="female")
    assert code == 0
    assert result["gfr_category"]["value"] == "G4"
    assert result["doctor_visit"]["value"] == pr.VISIT_SOON
    assert result["kdigo_checks_per_year"]["value"] is None  # no ACR, so no Figure 13 cell
    assert "尽快到肾内科" in report and "图 48" in report


@pytest.mark.parametrize("value,unit,expected", [
    (29.9, "mg/g", "A1"), (30, "mg/g", "A2"), (300, "mg/g", "A2"), (300.1, "mg/g", "A3"),
    (2.9, "mg/mmol", "A1"), (3.0, "mg/mmol", "A2"), (30, "mg/mmol", "A2"), (30.5, "mg/mmol", "A3"),
])
def test_kdigo_table3_boundaries(value, unit, expected):
    assert pr.albuminuria_category(value, unit) == expected


def test_acr_is_staged_in_the_unit_the_lab_printed(tmp_path: Path):
    # 3.2 mg/mmol is A2 by the mg/mmol column; converted (28.3 mg/g) it would read A1.
    code, result, report, _ = _run(tmp_path, [("肌酐", "80", "umol/L"), ("尿微量白蛋白/肌酐", "3.2", "mg/mmol")], age="45")
    assert code == 0
    assert 3.2 * 8.84 < 30
    assert result["albuminuria_category"]["value"] == "A2"
    assert result["doctor_visit"]["value"] == pr.VISIT_SEE
    assert "晨" in report and "1.3.1.2" in report
    code3, result3, _, _ = _run(tmp_path, [("肌酐", "80", "umol/L"), ("UACR", "3.0", "mg/mmol")], age="45", name="edge")
    assert result3["albuminuria_category"]["value"] == "A2"


def test_severe_albuminuria_is_seen_soon(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("肌酐", "70", "umol/L"), ("ACR", "450", "mg/g")], age="45")
    assert code == 0
    assert result["albuminuria_category"]["value"] == "A3"
    assert result["doctor_visit"]["value"] == pr.VISIT_SOON
    assert result["kdigo_checks_per_year"]["value"] == MONITORING_PER_YEAR[result["gfr_category"]["value"]][2]


@pytest.mark.parametrize("raw,whole,category", [(89.5, 90, "G1"), (89.4, 89, "G2"), (59.5, 60, "G2"), (59.4, 59, "G3a"),
                                                (44.5, 45, "G3a"), (29.5, 30, "G3b"), (14.5, 15, "G4"), (14.4, 14, "G5")])
def test_kdigo_table11_rounding_then_table2(raw, whole, category):
    assert pr.reported(raw) == whole
    assert pr.gfr_category(whole)[0] == category


def test_acr_without_unit_is_refused(tmp_path: Path):
    code, result, report, out = _run(tmp_path, [("肌酐", "80", "umol/L"), ("UACR", "5", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("uacr_mg_g", "unit_missing") in {(p["key"], p["kind"]) for p in problems}
    assert all(item["value"] is None for item in result.values())


def test_creatinine_in_mg_dl_without_unit_is_caught_by_range(tmp_path: Path):
    code, result, report, out = _run(tmp_path, [("肌酐", "1.1", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "creatinine_umol_l" and problems[0]["kind"] == "range"
    assert "mg/dL" in problems[0]["message_zh"]
    assert result["egfr_cr"]["value"] is None


def test_unknown_unit_is_refused(tmp_path: Path):
    code, _, _, out = _run(tmp_path, [("肌酐", "80", "mmol/L")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["kind"] == "unit"


@pytest.mark.parametrize("age,sex,key", [("16", "male", "age"), (None, "male", "age"), ("50", None, "sex"), ("50", "x", "sex")])
def test_children_and_missing_profile_are_refused(tmp_path: Path, age, sex, key):
    code, _, report, out = _run(tmp_path, [("肌酐", "80", "umol/L")], age=age, sex=sex)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert key in {p["key"] for p in problems}
    assert "eGFR（肌酐方程）" not in report


def test_missing_creatinine_is_refused(tmp_path: Path):
    code, _, _, out = _run(tmp_path, [("胱抑素C", "1.0", "mg/L")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("creatinine_umol_l", "missing") in {(p["key"], p["kind"]) for p in problems}


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == ["creatinine_umol_l", "cystatin_c_mg_l", "uacr_mg_g", "age", "sex"]
    creat = skillkit.spec_by_key(MANIFEST, "creatinine_umol_l")
    assert creat["accept"]["mg/dL"] == UMOL_L_PER_MG_DL
    assert skillkit.spec_by_key(MANIFEST, "uacr_mg_g")["unit_required"] is True
    assert MANIFEST["inputs_status"] == "verified"
    assert [o["key"] for o in MANIFEST["outputs"]] == ["egfr_cr", "egfr_cr_cys", "gfr_category", "gfr_category_equation",
                                                      "albuminuria_category", "kdigo_checks_per_year", "doctor_visit"]
