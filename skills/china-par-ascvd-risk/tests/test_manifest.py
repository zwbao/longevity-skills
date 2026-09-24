"""China-PAR against the paper's own numbers, for men and women.

Expectations come only from the paper (Supplemental Tables 1-2, Table 2) and
the 2019 guideline's worked example. Two constants are derived from printed
numbers (see presets.py); these tests show why and check the derivation.
"""

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import (EXAMPLE, EXAMPLE_MEN_SUM, EXAMPLE_MEN_TERMS, EXAMPLE_WOMEN_SUM, GUIDELINE_EXAMPLE,
                     GUIDELINE_EXAMPLE_RISK, MEAN_MEN, MEAN_WOMEN, MEN, MEN_PRINTED, MEN_TERM_VALUES, MMOL_TO_MG_DL,
                     S10_MEN, S10_WOMEN, S10_WOMEN_PRINTED, TABLE2)

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
MEN_FLAGS = ["--treated", "no", "--smoker", "no", "--diabetes", "yes", "--north", "yes", "--urban", "yes", "--family-history", "no"]
EXAMPLE_ROWS = [("收缩压", "130", "mmHg"), ("总胆固醇", "210", "mg/dL"), ("高密度脂蛋白胆固醇", "55", "mg/dL"), ("腰围", "80", "cm")]


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _men_sum(age, coefficients=None):
    e = EXAMPLE
    if coefficients is None:
        return sum(personal_report.terms_men(age, e["sbp"], e["treated"], e["tc"], e["hdl"], e["waist"], e["smoker"],
                                             e["diabetes"], e["north"], e["urban"], e["family_history"]))
    la, ls = math.log(age), math.log(e["sbp"])
    c = coefficients
    return (c["ln_age"] * la + c["ln_sbp_untreated"] * ls + c["ln_tc"] * math.log(e["tc"]) + c["ln_hdl"] * math.log(e["hdl"])
            + c["ln_waist"] * math.log(e["waist"]) + c["diabetes"] + c["north"] + c["urban"] + c["ln_age_x_ln_sbp_untreated"] * la * ls)


def _women_sum(age):
    e = EXAMPLE
    return personal_report.sum_women(age, e["sbp"], e["treated"], e["tc"], e["hdl"], e["waist"], e["smoker"], e["diabetes"], e["north"])


def test_derived_men_coefficients_round_to_the_printed_ones():
    for key in MEN_TERM_VALUES:
        assert round(MEN[key], 2) == pytest.approx(MEN_PRINTED[key]), key
    for key in set(MEN_PRINTED) - set(MEN_TERM_VALUES):
        assert MEN[key] == MEN_PRINTED[key]


def test_per_term_values_and_sum_match_the_paper():
    terms = personal_report.terms_men(60, 130, False, 210, 55, 80, False, True, True, True, False)
    for ours, printed in zip(terms[:9], EXAMPLE_MEN_TERMS):
        assert ours == pytest.approx(printed, abs=0.006)
    assert sum(terms) == pytest.approx(EXAMPLE_MEN_SUM, abs=0.015)
    assert personal_report.risk_men(EXAMPLE_MEN_SUM) == pytest.approx(11.0, abs=0.1)


@pytest.mark.parametrize("age", [40, 50, 60, 70])
def test_men_table2(age):
    assert personal_report.risk_men(_men_sum(age)) == pytest.approx(TABLE2["men"][age], rel=0.02)


def test_printed_two_decimal_coefficients_run_high():
    # Why the continuous coefficients are derived: printed ones put the paper's own example about 6% high.
    assert personal_report.risk_men(_men_sum(60, MEN_PRINTED)) > TABLE2["men"][60] * 1.05


def test_women_baseline_survival_is_solved_from_the_worked_example():
    solved = (1 - 0.101) ** (1 / math.exp(EXAMPLE_WOMEN_SUM - MEAN_WOMEN))
    assert S10_WOMEN == pytest.approx(solved, abs=1e-4)
    assert _women_sum(60) == pytest.approx(EXAMPLE_WOMEN_SUM, abs=0.01)
    printed = 100 * (1 - S10_WOMEN_PRINTED ** math.exp(_women_sum(60) - MEAN_WOMEN))
    assert printed < TABLE2["women"][60] * 0.75, "the printed 0.99 puts the paper's own example about a third low"


@pytest.mark.parametrize("age", [40, 50, 60, 70])
def test_women_table2(age):
    assert personal_report.risk_women(_women_sum(age)) == pytest.approx(TABLE2["women"][age], rel=0.02)


def test_guideline_example_stays_low_risk():
    g = GUIDELINE_EXAMPLE
    total = sum(personal_report.terms_men(g["age"], g["sbp"], g["treated"], g["tc_mmol"] * MMOL_TO_MG_DL, g["hdl_mmol"] * MMOL_TO_MG_DL,
                                          g["waist"], g["smoker"], g["diabetes"], g["north"], g["urban"], g["family_history"]))
    risk = personal_report.risk_men(total)
    assert risk == pytest.approx(GUIDELINE_EXAMPLE_RISK, abs=0.2)
    assert personal_report.category(risk) == "低危"


@pytest.mark.parametrize("sex", ["male", "female"])
def test_report_result_and_levers(tmp_path: Path, sex):
    m = _csv(tmp_path / "m.csv", EXAMPLE_ROWS)
    t = _csv(tmp_path / "t.csv", [("收缩压", "120", "mmHg")])
    flags = MEN_FLAGS if sex == "male" else MEN_FLAGS[:8]
    code = personal_report.main(["--measurements", str(m), "--age", "60", "--sex", sex, *flags, "--targets", str(t), "--out", str(tmp_path / "out")])
    assert code == 0
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    expected = TABLE2["men" if sex == "male" else "women"][60]
    risk = result["outputs"]["risk_10y_pct"]["value"]
    assert risk == pytest.approx(expected, rel=0.02)
    assert result["outputs"]["risk_category"]["value"] == "高危"
    levers = json.loads((tmp_path / "out" / "levers.json").read_text(encoding="utf-8"))
    assert levers["current"]["risk_pct"] == pytest.approx(risk)
    assert levers["levers"][0]["key"] == "sbp_mmhg" and levers["levers"][0]["risk_delta_pct"] < 0
    assert levers["targets"]["risk_pct"] < risk
    assert levers["current"]["category"] == "高危"
    assert levers["targets"]["category"] == personal_report.category(levers["targets"]["risk_pct"])
    report = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "边界" in report and "模型估计" in report


def test_mmol_units_convert(tmp_path: Path):
    m = _csv(tmp_path / "m.csv", [("收缩压", "130", "mmHg"), ("总胆固醇", str(210 / MMOL_TO_MG_DL), "mmol/L"),
                                  ("HDL-C", str(55 / MMOL_TO_MG_DL), "mmol/L"), ("腰围", "80", "cm")])
    code = personal_report.main(["--measurements", str(m), "--age", "60", "--sex", "male", *MEN_FLAGS, "--out", str(tmp_path / "out")])
    assert code == 0
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    assert result["outputs"]["risk_10y_pct"]["value"] == pytest.approx(personal_report.risk_men(_men_sum(60)), rel=1e-6)


def test_cholesterol_without_unit_and_missing_flags_are_refused(tmp_path: Path):
    m = _csv(tmp_path / "m.csv", [("收缩压", "130", "mmHg"), ("总胆固醇", "5.4", ""), ("HDL-C", "1.4", "mmol/L"), ("腰围", "80", "cm")])
    code = personal_report.main(["--measurements", str(m), "--age", "60", "--sex", "male", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))["problems"]
    kinds = {(item["key"], item["kind"]) for item in problems}
    assert ("tc_mg_dl", "unit_missing") in kinds
    assert ("smoker", "missing") in kinds
    assert json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))["outputs"]["risk_10y_pct"]["value"] is None


def test_women_do_not_need_the_men_only_flags(tmp_path: Path):
    m = _csv(tmp_path / "m.csv", EXAMPLE_ROWS)
    code = personal_report.main(["--measurements", str(m), "--age", "60", "--sex", "female", "--treated", "no", "--smoker", "no",
                                 "--diabetes", "yes", "--north", "yes", "--out", str(tmp_path / "out")])
    assert code == 0


def test_manifest():
    assert MANIFEST["inputs_status"] == "verified"
    assert S10_MEN == 0.9707 and MEAN_MEN == 140.68
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys[:4] == ["sbp_mmhg", "tc_mg_dl", "hdl_mg_dl", "waist_cm"]
    optional = {item["key"] for item in MANIFEST["inputs"] if not item["required"]}
    assert {"urban", "family_history"} <= optional
