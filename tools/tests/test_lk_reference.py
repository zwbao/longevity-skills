"""NHANES age reference model: stdlib inference, units, bands, refusals."""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.lk import reference  # noqa: E402
from tools.lk.library import Library  # noqa: E402

LIB = Library(ROOT)
MODEL = json.loads((ROOT / reference.MODEL_FILE).read_text(encoding="utf-8"))
INVERSE = {"none": lambda x: x, "log": math.exp, "log1p": lambda x: math.expm1(x), "logcrp": math.exp}
UNITS = {"albumin": "g/L", "creatinine": "umol/L", "glucose": "mmol/L", "wbc": "10^9/L", "mcv": "fL", "rdw": "%",
         "hdl": "mmol/L", "hba1c": "%", "alkaline_phosphatase": "U/L", "lymphocyte_pct": "%", "uric_acid": "umol/L",
         "total_cholesterol": "mmol/L", "bmi": "kg/m2"}


def person_at(age, sex="female"):
    """Rows whose values are the model's own means at this age (the posterior should centre near it)."""
    m = MODEL["model"][sex]
    i = age - MODEL["ages"][0]
    return [{"item": k, "value": f"{INVERSE[MODEL['features'][k]['transform']](m['mean'][k][i]):.6g}", "unit": u}
            for k, u in UNITS.items()]


def test_older_reference_profiles_read_older():
    """Mid-life curves are flat, so a mean profile is not pinned to its age; it must still rank ages and cover them."""
    for sex in ("male", "female"):
        estimates = []
        for age in (25, 45, 65, 78):
            out = reference.estimate_age(LIB, person_at(age, sex), sex)
            assert out["status"] == "ok", out
            lo, hi = out["outputs"]["interval_90"]
            assert lo <= age <= hi, (sex, age, out["outputs"])
            estimates.append(out["outputs"]["age_estimate"])
        assert estimates == sorted(estimates), (sex, estimates)


def test_units_on_the_report_do_not_change_the_answer():
    si = [{"item": "白蛋白", "value": "43", "unit": "g/L"}, {"item": "肌酐", "value": "70", "unit": "umol/L"},
          {"item": "葡萄糖", "value": "5.2", "unit": "mmol/L"}, {"item": "糖化血红蛋白", "value": "5.6", "unit": "%"},
          {"item": "红细胞分布宽度", "value": "13.4", "unit": "%"}]
    us = [{"item": "Albumin", "value": "4.3", "unit": "g/dL"}, {"item": "Creatinine", "value": f"{70 / 88.4:.6f}", "unit": "mg/dL"},
          {"item": "Serum glucose", "value": f"{5.2 / 0.0555:.6f}", "unit": "mg/dL"}, {"item": "Glycohemoglobin", "value": "5.6", "unit": "%"},
          {"item": "Red cell distribution width", "value": "13.4", "unit": "%"}]
    a = reference.estimate_age(LIB, si, "male")["outputs"]
    b = reference.estimate_age(LIB, us, "male")["outputs"]
    assert abs(a["age_estimate"] - b["age_estimate"]) < 0.05 and a["n_values_used"] == b["n_values_used"] == 5


def test_refusals_and_problems_are_explicit():
    rows = person_at(50)
    assert reference.estimate_age(LIB, rows, None)["status"] == "input_problem", "sex is required"
    assert reference.estimate_age(LIB, rows[:2], "female")["status"] == "input_problem", "fewer than three values"
    wrong = rows + [{"item": "C-reactive protein", "value": "5", "unit": "g/L"}]
    out = reference.estimate_age(LIB, wrong, "female")
    assert out["status"] == "ok" and any("单位" in p["message_zh"] for p in out["problems"]), "an unknown unit is reported, not guessed"
    huge = [r if r["item"] != "glucose" else {**r, "value": "95"} for r in rows]  # 95 mmol/L: a mg/dL value typed as mmol/L
    out = reference.estimate_age(LIB, huge, "female")
    assert "glucose" not in out["used"] and any("单位" in p["message_zh"] for p in out["problems"])


def test_bands_shared_edges_and_two_people():
    bands = reference.parse_bands("18-30,30-45,45-60,60-75,75+")
    assert reference.band_of(45, bands) == "45-60" and reference.band_of(44, bands) == "30-45", "a shared edge goes up"
    assert reference.band_of(80, bands) == "75+" and reference.band_of(17, bands) is None
    out = reference.estimate_age(LIB, person_at(68), "female", "18-30,30-45,45-60,60-75,75+")
    probs = out["outputs"]["band_probability"]
    assert list(probs) == ["18-30", "30-45", "45-60", "60-75", "75+"] and abs(sum(probs.values()) - 1) < 0.01
    assert out["outputs"]["most_likely_band"] == "60-75"
    text = ("Participant A:\n70-year-old male. Albumin (g/dL) 3.9; Creatinine (mg/dL) 1.3; Red cell distribution width (%) 14.6; "
            "Glycohemoglobin (%) 6.1; Mean cell volume (fL) 94\nParticipant B:\nmale. Albumin (g/dL) 4.9; Creatinine (mg/dL) 0.9; "
            "Red cell distribution width (%) 12.4; Glycohemoglobin (%) 5.0; Mean cell volume (fL) 87")
    two = reference.estimate_from_payload(LIB, {"panel_text": text})
    assert two["status"] == "per_person" and [p["label"] for p in two["people"]] == ["A", "B"]
    a, b = (p["outputs"]["age_estimate"] for p in two["people"])
    assert a > b
