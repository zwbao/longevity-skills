"""LinAge against the paper's own printed numbers, and the inputs skill.json declares.

Expected values come only from the paper's supplementary files:
- linAge_Example.xls (MOESM6), sheet example_males: NHANES IV SEQN 10, chronAge 43.1666 years,
  sum(beta_i*para_i) 7.389850952344081, DeltaAge 5.370465592344081, bioAge 48.537065592344085.
- The data matrix with LinAge (MOESM9): SEQN 10 (male, chronAge 43, delAge 5.40705095234407,
  linAge 48.4070509523441) and SEQN 24 (female, chronAge 53, delAge 3.91880108714463,
  linAge 56.9188010871446).
The measured inputs are the raw values of the same subjects in MOESM8 (NHANES SI units);
the comorbidity, self-health and healthcare-use indices are the ones MOESM9 prints
(fs1Score, fs2Score, fs3Score) and the urine ACR is MOESM9's crAlbRat.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import COMORBIDITIES, PARAMS, SELF_HEALTH_KEYS

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
TOL = 1e-9

# MOESM8 row SEQN 10 (male), in the order of the NHANES columns.
SEQN10 = {
    "pulse_per_min": 58, "sbp_mmhg": 142, "dbp_mmhg": 95, "bmi_kg_m2": 30.94, "iron_umol_l": 14.86,
    "tibc_umol_l": 52.98, "tsat_pct": 28, "ferritin_ug_l": 32, "folate_nmol_l": 30.6, "b12_pmol_l": 281.92,
    "cotinine_ng_ml": 374.58, "tc_mmol_l": 3.62, "hdl_mmol_l": 1.31, "wbc_10e9_l": 4.6, "lymph_pct": 41.3,
    "mono_pct": 10.5, "neut_pct": 43.8, "eos_pct": 3.4, "baso_pct": 1, "lymph_10e9_l": 1.9, "mono_10e9_l": 0.5,
    "neut_10e9_l": 2, "baso_10e9_l": 0, "rbc_10e12_l": 5, "hgb_g_dl": 15.4, "hct_pct": 46.2, "mcv_fl": 92.3,
    "mch_pg": 30.9, "mchc_g_dl": 33.5, "rdw_pct": 13.7, "plt_10e9_l": 167, "mpv_fl": 9.4, "crp_mg_dl": 0.12,
    "fibrinogen_g_l": 3.13, "hba1c_pct": 5.5, "ntprobnp_pg_ml": 39.28, "albumin_g_l": 42, "alt_u_l": 20,
    "ast_u_l": 26, "alp_u_l": 86, "urea_mmol_l": 4.6, "calcium_mmol_l": 2.35, "bicarbonate_mmol_l": 21,
    "ggt_u_l": 25, "glucose_mmol_l": 4.829, "ldh_u_l": 201, "phosphorus_mmol_l": 0.969, "tbil_umol_l": 6.8,
    "total_protein_g_l": 76, "tg_mmol_l": 0.474, "uric_acid_umol_l": 356.9, "creatinine_umol_l": 79.6,
    "sodium_mmol_l": 140.9, "potassium_mmol_l": 4.28, "chloride_mmol_l": 106.3, "globulin_g_l": 34,
    "acr_mg_g": 3.97850648787598,
    # fs1Score 0.0909090909090909 = 2/22, fs2Score 0, fs3Score 3.
    "hypertension": 1, "arthritis": 1, "huq050": 3,
}

# MOESM8 row SEQN 24 (female).
SEQN24 = {
    "pulse_per_min": 82, "sbp_mmhg": 114, "dbp_mmhg": 71, "bmi_kg_m2": 25.93, "iron_umol_l": 17.54,
    "tibc_umol_l": 66.77, "tsat_pct": 26.3, "ferritin_ug_l": 127, "folate_nmol_l": 22.2, "b12_pmol_l": 479.7,
    "cotinine_ng_ml": 255.19, "tc_mmol_l": 5.66, "hdl_mmol_l": 2.72, "wbc_10e9_l": 9.4, "lymph_pct": 39.1,
    "mono_pct": 7.4, "neut_pct": 51.6, "eos_pct": 1.5, "baso_pct": 0.6, "lymph_10e9_l": 3.7, "mono_10e9_l": 0.7,
    "neut_10e9_l": 4.9, "baso_10e9_l": 0.1, "rbc_10e12_l": 4.34, "hgb_g_dl": 14.7, "hct_pct": 42, "mcv_fl": 96.7,
    "mch_pg": 30.8, "mchc_g_dl": 31.8, "rdw_pct": 12.7, "plt_10e9_l": 331, "mpv_fl": 8.7, "crp_mg_dl": 0.08,
    "fibrinogen_g_l": 2.81, "hba1c_pct": 5.3, "ntprobnp_pg_ml": 15.27, "albumin_g_l": 47, "alt_u_l": 20,
    "ast_u_l": 18, "alp_u_l": 114, "urea_mmol_l": 3.6, "calcium_mmol_l": 2.45, "bicarbonate_mmol_l": 24,
    "ggt_u_l": 57, "glucose_mmol_l": 4.718, "ldh_u_l": 135, "phosphorus_mmol_l": 1.227, "tbil_umol_l": 6.8,
    "total_protein_g_l": 76, "tg_mmol_l": 0.847, "uric_acid_umol_l": 226, "creatinine_umol_l": 53,
    "sodium_mmol_l": 136.9, "potassium_mmol_l": 4.39, "chloride_mmol_l": 100.3, "globulin_g_l": 29,
    "acr_mg_g": 6.44030770298765,
    # fs1Score 0.227272727272727 = 5/22; fs2Score 1 = fair x 2 x (1 - 0.5 better); fs3Score 2.
    "hypertension": 1, "asthma": 1, "arthritis": 1, "thyroid_disease": 1, "osteoporosis": 1,
    "fair_general_health": 1, "better_current_health": 1, "huq050": 2,
}


def _csv(path: Path, values: dict, units: dict | None = None) -> Path:
    units = units or {}
    rows = [f"{key},{value!r},{units.get(key, '')}" for key, value in values.items()]
    path.write_text("item,value,unit\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, values: dict, age, sex, units=None, name="out"):
    out = tmp_path / name
    code = personal_report.main(["--measurements", str(_csv(tmp_path / f"{name}.csv", values, units)),
                                 "--age", str(age), "--sex", sex, "--out", str(out)])
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    return code, {key: item["value"] for key, item in result.items()}, out


def test_paper_example_male_seqn10_spreadsheet(tmp_path: Path):
    code, result, _out = _run(tmp_path, SEQN10, 43.1666, "male")
    assert code == 0
    assert result["missing_count"] == 0
    assert result["linage_delta_years"] == pytest.approx(5.370465592344081, abs=TOL)
    assert result["linage_years"] == pytest.approx(48.537065592344085, abs=TOL)
    terms = result["linage_delta_years"] - 7.46 + 0.0183 * 43.1666 * 12
    assert terms == pytest.approx(7.389850952344081, abs=TOL)


def test_paper_example_male_seqn10_matrix(tmp_path: Path):
    code, result, _out = _run(tmp_path, SEQN10, 43, "男")
    assert code == 0
    assert result["linage_delta_years"] == pytest.approx(5.40705095234407, abs=TOL)
    assert result["linage_years"] == pytest.approx(48.4070509523441, abs=TOL)
    assert result["comorbidity_index"] == pytest.approx(0.0909090909090909, abs=TOL)
    assert result["ldl_mmol_l"] == pytest.approx(2.2152, abs=TOL)


def test_paper_example_female_seqn24_matrix(tmp_path: Path):
    code, result, _out = _run(tmp_path, SEQN24, 53, "female")
    assert code == 0
    assert result["linage_delta_years"] == pytest.approx(3.91880108714463, abs=TOL)
    assert result["linage_years"] == pytest.approx(56.9188010871446, abs=TOL)
    assert result["comorbidity_index"] == pytest.approx(0.227272727272727, abs=TOL)
    assert result["self_health_index"] == 1
    assert result["healthcare_use_code"] == 2
    assert result["ldl_mmol_l"] == pytest.approx(2.7706, abs=TOL)


def test_command_line_reads_the_same_file(tmp_path: Path):
    path = _csv(tmp_path / "m.csv", SEQN24)
    out = tmp_path / "cli"
    done = subprocess.run([sys.executable, str(ROOT / "scripts" / "personal_report.py"), "--measurements", str(path),
                           "--age", "53", "--sex", "女", "--out", str(out)], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["linage_years"]["value"] == pytest.approx(56.9188010871446, abs=TOL)


def test_other_units_and_lab_names_give_the_same_linage(tmp_path: Path):
    values = dict(SEQN24)
    names = {"tc_mmol_l": "总胆固醇", "hdl_mmol_l": "HDL-C", "tg_mmol_l": "甘油三酯", "glucose_mmol_l": "血糖",
             "crp_mg_dl": "超敏C反应蛋白", "hgb_g_dl": "血红蛋白", "albumin_g_l": "ALB", "creatinine_umol_l": "肌酐"}
    converted = dict(values)
    units = {}
    converted["tc_mmol_l"] = values["tc_mmol_l"] / 0.02586; units["tc_mmol_l"] = "mg/dL"
    converted["crp_mg_dl"] = values["crp_mg_dl"] * 10; units["crp_mg_dl"] = "mg/L"
    converted["hgb_g_dl"] = values["hgb_g_dl"] * 10; units["hgb_g_dl"] = "g/L"
    renamed = {names.get(key, key): value for key, value in converted.items()}
    renamed_units = {names.get(key, key): unit for key, unit in units.items()}
    renamed_units.update({"甘油三酯": "mmol/L"})
    code, result, _out = _run(tmp_path, renamed, 53, "female", renamed_units)
    assert code == 0
    assert result["linage_years"] == pytest.approx(56.9188010871446, abs=1e-6)


def test_manifest_matches_the_script():
    keys = [spec["key"] for spec in skillkit.input_specs(MANIFEST)]
    model = [key for _code, key, _t, _m, _f in PARAMS
             if key not in ("comorbidity_index", "self_health_index", "healthcare_use_code", "ldl_mmol_l")]
    assert keys[: len(model)] == model
    assert keys[len(model): len(model) + 22] == [key for key, _label, _item in COMORBIDITIES]
    assert keys[len(model) + 22:] == [*SELF_HEALTH_KEYS, "huq050", "healthcare_visits_past_year"]
    assert len(PARAMS) == 61
    profile = {spec["key"]: spec for spec in skillkit.input_specs(MANIFEST, "profile")}
    assert profile["age"]["required"] and profile["sex"]["required"]
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["entry"]["sex_flag"] == "--sex"
    assert {item["key"] for item in MANIFEST["outputs"]} >= {"linage_years", "linage_delta_years", "missing_count"}


@pytest.mark.parametrize("change, units, age, sex, kind", [
    ({"crp_mg_dl": 1.2}, {"crp_mg_dl": "mmol/L"}, 53, "female", "unit"),
    ({"tc_mmol_l": 220}, {}, 53, "female", "range"),
    ({"hypertension": 2}, {}, 53, "female", "range"),
    ({"poor_general_health": 1}, {}, 53, "female", "parse"),
    ({}, {}, None, "female", "missing"),
    ({}, {}, 53, "", "missing"),
    ({}, {}, 30, "female", "range"),
])
def test_wrong_or_missing_input_exits_3(tmp_path: Path, change, units, age, sex, kind):
    values = dict(SEQN24, **change)
    path = _csv(tmp_path / "bad.csv", values, units)
    argv = ["--measurements", str(path), "--sex", sex, "--out", str(tmp_path / "bad")]
    if age is not None:
        argv += ["--age", str(age)]
    assert personal_report.main(argv) == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((tmp_path / "bad" / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert kind in {item["kind"] for item in problems}
    result = json.loads((tmp_path / "bad" / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["linage_years"]["value"] is None


def test_crp_needs_a_unit_when_named_by_label(tmp_path: Path):
    values = {("C反应蛋白" if key == "crp_mg_dl" else key): value for key, value in SEQN24.items()}
    code, _result, out = _run(tmp_path, values, 53, "female")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert {item["kind"] for item in problems} == {"unit_missing"}


def test_no_lab_at_all_exits_3(tmp_path: Path):
    path = _csv(tmp_path / "q.csv", {"hypertension": 1})
    assert personal_report.main(["--measurements", str(path), "--age", "60", "--sex", "male",
                                 "--out", str(tmp_path / "q")]) == skillkit.EXIT_INPUT_PROBLEM


def test_missing_items_count_zero_and_are_reported(tmp_path: Path):
    values = {key: value for key, value in SEQN10.items() if key not in ("ntprobnp_pg_ml", "fibrinogen_g_l")}
    code, result, out = _run(tmp_path, values, 43.1666, "male")
    assert code == 0
    assert result["missing_count"] == 2
    # Weights of the two missing parameters for men, Supplementary Table 7: SSBNP 1.7226, LBDFBSI 1.0257.
    assert result["missing_weight_years"] == pytest.approx(1.7226 + 1.0257)
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "N端脑钠肽前体" in text and "纤维蛋白原" in text
