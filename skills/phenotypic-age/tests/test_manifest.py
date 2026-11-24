"""Engineering checks, NOT reproduction of a printed patient example.

The article, correction, Tables 1–4, Figures 1–7 and all eight supplements
contain no complete personal panel paired with a Phenotypic Age result.
Synthetic inputs below exercise the printed corrected equation and the CLI.
No calculated value is frozen as if it had been printed in the paper.
"""
import json
import math
import subprocess
import sys
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as pr
import presets as p
import skillkit

MANIFEST = json.loads((ROOT / "skill.json").read_text())
ROWS = [
    ("白蛋白", "45", "g/L"), ("肌酐", "80", "umol/L"),
    ("空腹血糖", "5", "mmol/L"), ("超敏C反应蛋白", "1", "mg/L"),
    ("淋巴细胞百分比", "30", "%"), ("MCV", "90", "fL"),
    ("RDW-CV", "13", "%"), ("ALP", "70", "U/L"),
    ("白细胞计数", "6", "×10⁹/L"),
]


def csv(path, rows):
    path.write_text("marker,value,unit\n" + "\n".join(",".join(r) for r in rows) + "\n")
    return path


def run(tmp_path, rows=ROWS, age="40", targets=None):
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(csv(tmp_path / "labs.csv", rows)), "--out", str(out)]
    if age is not None:
        args += ["--age", age]
    if targets is not None:
        args += ["--targets", str(csv(tmp_path / "targets.csv", targets))]
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc, out


def decimal_equation(values):
    """Literal three-stage equation from Correction, evaluated independently.

    This checks numerical algebra, not scientific validation. Values supplied
    to this helper are synthetic; there is no printed expected patient age.
    """
    with localcontext() as ctx:
        ctx.prec = 70
        d = {k: Decimal(str(v)) for k, v in values.items()}
        xb = (Decimal("-19.907") - Decimal("0.0336") * d["albumin_g_l"]
              + Decimal("0.0095") * d["creatinine_umol_l"]
              + Decimal("0.1953") * d["glucose_mmol_l"]
              + Decimal("0.0954") * d["crp_mg_dl"].ln()
              - Decimal("0.0120") * d["lymphocyte_pct"]
              + Decimal("0.0268") * d["mcv_fl"]
              + Decimal("0.3306") * d["rdw_pct"]
              + Decimal("0.00188") * d["alp_u_l"]
              + Decimal("0.0554") * d["wbc_10e9_l"]
              + Decimal("0.0804") * d["age"])
        m = 1 - (-Decimal("1.51714") * xb.exp() / Decimal("0.0076927")).exp()
        return float(Decimal("141.50") + (-Decimal("0.00553") * (1-m).ln()).ln()
                     / Decimal("0.09165"))


def test_manifest_units_and_corrected_coefficients():
    specs = {s["key"]: s for s in MANIFEST["inputs"]}
    assert set(specs) == set(p.COEFFICIENTS) | {"sex"}
    for key, unit in p.UNITS.items():
        assert specs[key]["unit"] == unit
    # Correction, xb equation: original article misprints these coefficients.
    assert p.COEFFICIENTS["glucose_mmol_l"] == 0.1953
    assert p.COEFFICIENTS["rdw_pct"] == 0.3306
    assert p.COEFFICIENTS["alp_u_l"] == 0.00188
    assert MANIFEST["validation"]["status"] == "draft"
    assert MANIFEST["inputs_status"] == "draft"


def test_result_agrees_with_literal_corrected_equation(tmp_path):
    proc, out = run(tmp_path)
    assert proc.returncode == 0, proc.stderr
    values = skillkit.collect_file(tmp_path / "labs.csv", MANIFEST).values
    expected = decimal_equation({**values, "age": 40})
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["phenoage"]["value"] == pytest.approx(expected, abs=1e-10)
    assert result["phenoage_difference"]["value"] == pytest.approx(expected - 40)
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "仍在验证" in report and "PhenoAgeAccel" in report
    assert "边界:" in report and "10.1371/journal.pmed.1002760" in report


@pytest.mark.parametrize("index,value,unit", [
    (0, "4.5", "g/L"), (0, "500", "g/L"), (3, "1", ""),
    (3, "0", "mg/L"), (3, "<0.1", "mg/L"), (3, "nan", "mg/L"),
    (4, "1.8", "10^9/L"), (6, "42", "fL"),
])
def test_invalid_measurement_exits_three_without_results(tmp_path, index, value, unit):
    rows = list(ROWS)
    rows[index] = (rows[index][0], value, unit)
    proc, out = run(tmp_path, rows)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert all(v["value"] is None for v in json.loads((out / "result.json").read_text())["outputs"].values())
    assert not (out / "levers.json").exists()
    text = (out / "report.md").read_text()
    assert "## 论文卡片" in text and "这次没有计算" in text and "边界:" in text


@pytest.mark.parametrize("age", [None, "bad", "nan", "inf", "19", "85"])
def test_invalid_or_outside_supported_age(tmp_path, age):
    proc, out = run(tmp_path, age=age)
    assert proc.returncode == 3, proc.stderr
    assert (out / "problems.json").exists()


def test_missing_and_duplicate_inputs(tmp_path):
    for rows in [ROWS[:-1], ROWS + [("ALB", "46", "g/L")]]:
        proc, out = run(tmp_path, rows)
        assert proc.returncode == 3, proc.stderr
        assert (out / "problems.json").exists()


def test_equivalent_units(tmp_path):
    rows = list(ROWS)
    rows[0] = ("Albumin", "4.5", "g/dL")
    rows[1] = ("Creatinine", "1", "mg/dL")
    rows[2] = ("Glucose", "100", "mg/dL")
    proc, _ = run(tmp_path, rows)
    assert proc.returncode == 0, proc.stderr
    v = skillkit.collect_file(tmp_path / "labs.csv", MANIFEST).values
    assert v["albumin_g_l"] == 45
    assert v["creatinine_umol_l"] == pytest.approx(88.4)
    assert v["glucose_mmol_l"] == pytest.approx(5.55)
    assert v["crp_mg_dl"] == pytest.approx(0.1)


def test_targets_and_analytic_sensitivity(tmp_path):
    proc, out = run(tmp_path, targets=[("空腹血糖", "4.5", "mmol/L"), ("CRP", "0.5", "mg/L")])
    assert proc.returncode == 0, proc.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    slopes = {x["key"]: x["years_per_unit"] for x in levers["sensitivity"]}
    assert slopes["glucose_mmol_l"] == pytest.approx(0.1953 / 0.09165)
    assert slopes["crp_mg_dl"] == pytest.approx(0.0954 / (0.09165 * 0.1))
    assert slopes["age"] == pytest.approx(0.0804 / 0.09165)
    expected_delta = (-0.5 * 0.1953 + 0.0954 * math.log(0.5)) / 0.09165
    assert levers["targets"]["phenoage_delta"] == pytest.approx(expected_delta)
    assert sum(x["phenoage_delta"] for x in levers["levers"]) == pytest.approx(expected_delta)
    assert "因果" in levers["note_zh"]


@pytest.mark.parametrize("targets", [[], [("age", "30", "a")], [("CRP", "0", "mg/L")], [("typo", "5", "")]])
def test_bad_targets_clear_stale_results(tmp_path, targets):
    assert run(tmp_path)[0].returncode == 0
    proc, out = run(tmp_path, targets=targets)
    assert proc.returncode == 3, proc.stderr
    assert not (out / "levers.json").exists()
    assert all(x["value"] is None for x in json.loads((out / "result.json").read_text())["outputs"].values())


def test_extreme_valid_panel_remains_finite():
    values = {s["key"]: s["range"][1] for s in MANIFEST["inputs"] if "range" in s}
    # Stable algebra must not take log(1-M) after M rounds to one.
    assert math.isfinite(pr.phenotypic_age(values))
