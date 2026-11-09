"""English report names, pasted panels and the prompt hook."""

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.lk import aliases, panel  # noqa: E402
from tools.lk.cli import main  # noqa: E402
from tools.lk.library import Library  # noqa: E402
from tools.lk.run import run  # noqa: E402

LIB = Library(ROOT)
NHANES_STYLE = (
    "Demographic information: 55-year-old male.\n"
    "Blood panel: Albumin (g/dL) 4.30; Alkaline phosphatase (U/L) 70.00; Creatinine (mg/dL) 0.90; "
    "Serum glucose (mg/dL) 98.00; C-reactive protein (mg/dL) 0.21; White blood cell count (1000 cells/uL) 6.20; "
    "Mean cell volume (fL) 90.00; Red cell distribution width (%) 13.10; Lymphocyte percent (%) 30.00; "
    "Vitamin E (umol/L) 19.97."
)
SAME_IN_CHINESE = [
    {"item": "白蛋白", "value": "43", "unit": "g/L"}, {"item": "碱性磷酸酶", "value": "70", "unit": "U/L"},
    {"item": "肌酐", "value": "79.56", "unit": "umol/L"}, {"item": "葡萄糖", "value": "5.439", "unit": "mmol/L"},
    {"item": "crp", "value": "0.21", "unit": "mg/dL"}, {"item": "白细胞计数", "value": "6.2", "unit": "10^9/L"},
    {"item": "mcv", "value": "90", "unit": "fL"}, {"item": "rdw", "value": "13.1", "unit": "%"},
    {"item": "lymph%", "value": "30", "unit": "%"},
]


def test_english_names_word_order_and_parentheses():
    for name, analyte in [("Glucose, serum", "glucose"), ("Serum glucose", "glucose"), ("Glucose (mg/dL)", "glucose"),
                          ("Glycohemoglobin (%)", "hba1c"), ("Segmented neutrophils percent", "neutrophil_pct"),
                          ("Direct HDL-Cholesterol", "hdl"), ("Iron, frozen serum", "iron"),
                          ("Mean corpuscular hemoglobin", "mch"), ("Mean corpuscular hemoglobin concentration", "mchc")]:
        assert aliases.analyte_of(name) == analyte, name
    assert aliases.analyte_of("Protein") is None and aliases.analyte_of("Vitamin E") is None
    assert not aliases._AMBIGUOUS, "every English name points to one analyte"
    assert aliases.unit_of("1000 cells/uL") == "10^3/uL" and aliases.unit_of("mg/dL") == "mg/dL"


def test_panel_parsing_reads_age_sex_and_values():
    [person] = panel.parse_panel(NHANES_STYLE)
    assert person["age"] == 55 and person["sex"] == "male"
    rows = {r["item"]: (r["value"], r["unit"]) for r in person["rows"]}
    assert rows["White blood cell count"] == ("6.20", "1000 cells/uL")
    assert rows["Albumin"] == ("4.30", "g/dL") and rows["Vitamin E"] == ("19.97", "umol/L")
    [p] = panel.parse_panel("White blood cell count (1000 cells/uL) 6.9. 82-year-old female")
    assert p["rows"][0]["value"] == "6.9", "a full stop after the value is not part of it"
    two = panel.parse_panel("Participant A:\n70-year-old male. Albumin (g/dL) 4.1\nParticipant B:\n64-year-old female. Albumin (g/L) 41")
    assert [(p["label"], p["age"], p["sex"]) for p in two] == [("A", 70, "male"), ("B", 64, "female")]
    [cn] = panel.parse_panel("男，62岁。肌酐 78 umol/L；白蛋白 43 g/L")
    assert cn["age"] == 62 and cn["sex"] == "male" and {r["item"] for r in cn["rows"]} == {"肌酐", "白蛋白"}


def test_english_panel_gives_the_same_phenoage_as_the_chinese_report():
    english = run(LIB, "accelerated-biological-aging-risk", {"panel_text": NHANES_STYLE})
    chinese = run(LIB, "accelerated-biological-aging-risk", {"age": 55, "measurements": SAME_IN_CHINESE})
    assert english["status"] == "ok" and chinese["status"] == "ok", (english.get("problems"), chinese.get("problems"))
    a, b = english["outputs"]["phenoage"]["value"], chinese["outputs"]["phenoage"]["value"]
    assert abs(a - b) < 0.01, (a, b)
    checked = english["checked_by_engine"]
    assert checked["translated_names"]["Serum glucose"] == "glucose"
    assert "Vitamin E" in checked["unmatched"] and checked["read_from_panel_text"]["age"] == 55


def test_panel_with_two_people_is_run_one_at_a_time():
    text = "Participant A:\n70-year-old male. Albumin (g/dL) 4.1\nParticipant B:\n64-year-old female. Albumin (g/L) 41"
    try:
        run(LIB, "accelerated-biological-aging-risk", {"panel_text": text})
    except Exception as exc:  # noqa: BLE001
        assert "2 people" in str(exc)
    else:
        raise AssertionError("a two-person panel must be refused")


def test_hook_speaks_only_when_a_method_applies(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"prompt": NHANES_STYLE})))
    assert main(["--library", str(ROOT), "detect", "--hook"]) == 0
    out = json.loads(capsys.readouterr().out)
    context = out["hookSpecificOutput"]["additionalContext"]
    assert "accelerated-biological-aging-risk" in context and "mortality_10y_pct" in context
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"prompt": "what does NMN do?"})))
    assert main(["--library", str(ROOT), "detect", "--hook"]) == 0
    assert capsys.readouterr().out == ""
    monkeypatch.setattr(sys, "stdin", io.StringIO("not json at all {"))
    assert main(["--library", str(ROOT), "detect", "--hook"]) == 0, "a hook never fails the prompt"


def _cli(capsys, *argv):
    main(["--library", str(ROOT), *argv])
    return json.loads(capsys.readouterr().out)


def test_change_accepts_english_marker_names(capsys):
    english = _cli(capsys, "change", "--marker", "Glycohemoglobin (%)", "--before", "5.9", "--after", "6.3")
    chinese = _cli(capsys, "change", "--marker", "糖化血红蛋白", "--before", "5.9", "--after", "6.3")
    assert english["verdict"] == chinese["verdict"] != "no_noise_model"
    assert english["band_pct"] == chinese["band_pct"]


def test_trend_first_to_last_uses_the_retest_interval(capsys):
    out = _cli(capsys, "trend", "--marker", "糖化血红蛋白", "--series", "2026-06-10:6.2", "2026-08-05:6.0", "2026-10-01:5.8")
    assert out["baseline_vs_latest"]["verdict"] == "too_close"
    assert out["summary_verdict"] == "not_judged", "no comparison passed the interval rule, so nothing is judged"


def test_specific_form_also_shows_broader_human_rows_labelled(capsys):
    out = _cli(capsys, "evidence", "维生素D3")["results"][0]
    if out["counts"]["human"] == 0 and "broader_name" in out:
        assert out["broader_name"]["query"] == "维生素D" and "不专指" in out["broader_name"]["label_zh"]
    b12 = _cli(capsys, "evidence", "维生素B12")["results"][0]
    assert "broader_name" not in b12, "a two-digit form (B12) is never cut: 维生素B1 is a different vitamin"


def test_evidence_search_keeps_combinations_and_english_trial_names(capsys):
    out = _cli(capsys, "evidence", "dasatinib")["results"][0]
    human = [r["entity"] for r in (out.get("human") or {}).get("rows", [])]
    assert any("quercetin" in e for e in human), "a combination row is found even when other rows are named exactly dasatinib"
    for q in ("time-restricted eating", "16:8 fasting"):
        res = _cli(capsys, "evidence", q)["results"][0]
        assert len(res.get("trial_effects", [])) >= 1, q
