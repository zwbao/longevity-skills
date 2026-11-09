"""Plasma pTau217 cut-offs against the numbers Martino-Adami et al. (Nat Commun 2026) print.

The reproduction tests recompute every printed GMM cut-off from the mixture
parameters printed in Supplementary Tables 2 and 3 (two components, equal
variance, natural-log scale): single cut-off = posterior 0.5; two cut-offs =
posterior 1-t and t. Expected values are the printed cut-offs from the Results
text and Table 2. Both parameters and cut-offs are printed to two decimals, so the
tolerance is 0.01 (one unit of the last printed digit). All inputs are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
from presets import ASHTON_TWO, SINGLE_CUTOFF, TWO_CUTOFFS

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
TOL = 0.01


def _check(marker, cohort, single, pairs):
    assert pr.cutoffs_from_gmm(marker, cohort)[0] == pytest.approx(single, abs=TOL)
    for prob, (lower, upper) in pairs.items():
        lo, up = pr.cutoffs_from_gmm(marker, cohort, prob)
        assert lo == pytest.approx(lower, abs=TOL), (marker, cohort, prob, "lower", lo)
        assert up == pytest.approx(upper, abs=TOL), (marker, cohort, prob, "upper", up)
        assert TWO_CUTOFFS[(marker, cohort, prob)] == (lower, upper)


def test_paper_example_brazil_ptau217():
    # Results (Cog-Aging-Study-Brazil): single 0.63 pg/mL; >=0.80: 0.52/0.76; >=0.85: 0.50/0.79; >=0.90: 0.47/0.84.
    _check("ptau217", "brazil", 0.63, {0.80: (0.52, 0.76), 0.85: (0.50, 0.79), 0.90: (0.47, 0.84)})


def test_paper_example_argentina_ptau217():
    # Results (GeNED.ar-Argentina): single 0.63 pg/mL; >=0.80: 0.52/0.77; >=0.85: 0.50/0.81; >=0.90: 0.47/0.86.
    _check("ptau217", "argentina", 0.63, {0.80: (0.52, 0.77), 0.85: (0.50, 0.81), 0.90: (0.47, 0.86)})


def test_paper_example_ratio():
    # Table 2 (Brazil): >=0.12; 0.09/0.16; 0.08/0.17; 0.07/0.19.
    _check("ratio", "brazil", 0.12, {0.80: (0.09, 0.16), 0.85: (0.08, 0.17), 0.90: (0.07, 0.19)})
    # Results (Argentina): single 0.12; 0.10/0.14; 0.097/0.15; 0.09/0.16.
    _check("ratio", "argentina", 0.12, {0.80: (0.10, 0.14), 0.85: (0.097, 0.15), 0.90: (0.09, 0.16)})


def test_natural_log_not_log10():
    # The log base is not stated; log10 would put the single cut-off far from 0.63.
    import math
    g = pr.GMM[("ptau217", "brazil")]
    mid10 = 10 ** ((g["means"][0] + g["means"][1]) / 2)
    assert abs(mid10 - 0.63) > 0.2


def test_table2_convention_at_boundaries():
    lo, up = TWO_CUTOFFS[("ptau217", "brazil", 0.85)]
    assert pr.two_cutoff_category(lo, lo, up) == "negative"      # "≤0.50"
    assert pr.two_cutoff_category(up, lo, up) == "positive"      # "≥0.79"
    assert pr.two_cutoff_category(0.65, lo, up) == "indeterminate"
    assert pr.single_status(SINGLE_CUTOFF["ptau217"], SINGLE_CUTOFF["ptau217"]) == "positive"  # "≥0.63"
    assert pr.ashton_two_category(ASHTON_TWO[0]) == "indeterminate"  # "<0.40" is strict
    assert pr.ashton_two_category(ASHTON_TWO[1]) == "indeterminate"  # ">0.63" is strict


def test_posterior_matches_grey_zone():
    lo, up = pr.cutoffs_from_gmm("ptau217", "brazil", 0.85)
    assert pr.abnormal_probability(lo, "ptau217", "brazil") == pytest.approx(0.15)
    assert pr.abnormal_probability(up, "ptau217", "brazil") == pytest.approx(0.85)


def test_manifest_matches_presets():
    keys = {spec["key"]: spec for spec in MANIFEST["inputs"]}
    assert keys["ptau217_pg_ml"]["unit"] == "pg/mL" and keys["abeta42_pg_ml"]["unit"] == "pg/mL"
    assert keys["assay"]["required"] is True
    outs = {spec["key"] for spec in MANIFEST["outputs"]}
    assert {"ptau217_two_cutoff_category", "ptau217_single_cutoff_status", "ptau217_abeta42_ratio",
            "ratio_two_cutoff_category", "ptau217_abnormal_class_probability"} <= outs


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(r) for r in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path, rows, extra=("--assay", "simoa-alzpath"), name="out"):
    m = _csv(tmp_path / f"{name}.csv", rows)
    out = tmp_path / name
    code = pr.main(["--measurements", str(m), "--out", str(out), *extra])
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


@pytest.mark.parametrize("value,expected", [("0.40", "negative"), ("0.65", "indeterminate"), ("1.20", "positive")])
def test_report_end_to_end(tmp_path, value, expected):
    code, result, report, _ = _run(tmp_path, [("pTau217", value, "pg/mL")], name=f"r{value}")
    assert code == 0
    assert result["ptau217_two_cutoff_category"]["value"] == expected
    assert result["cutoff_set"]["value"] == "brazil_0.85"
    assert result["ptau217_abeta42_ratio"]["value"] is None
    assert report.startswith(f"# {pr.TITLE}")
    assert "## 论文卡片" in report and "边界:" in report and "doi.org/10.1038/s41467-026-76434-2" in report
    assert "剂量" in report  # boundary sentence keeps the no-dose line
    assert "≤0.50 阴性，≥0.79 阳性" in report and "<0.40 阴性，>0.63 阳性" in report


def test_ratio_and_ng_per_l(tmp_path):
    code, result, report, _ = _run(tmp_path, [("p-tau217", "0.9", "ng/L"), ("Aβ42", "5.0", "pg/mL")])
    assert code == 0
    assert result["ptau217_abeta42_ratio"]["value"] == pytest.approx(0.18)
    assert result["ratio_two_cutoff_category"]["value"] == "positive"     # >= 0.17
    assert result["ratio_single_cutoff_status"]["value"] == "positive"    # >= 0.12
    assert result["ptau217_two_cutoff_category"]["value"] == "positive"   # >= 0.79


def test_argentina_set(tmp_path):
    code, result, _, _ = _run(tmp_path, [("pTau217", "0.80", "pg/mL")],
                              extra=("--assay", "simoa-alzpath", "--cohort", "argentina"))
    assert code == 0
    assert result["ptau217_two_cutoff_category"]["value"] == "indeterminate"  # < 0.81 in Argentina
    assert result["cutoff_set"]["value"] == "argentina_0.85"


def test_wrong_unit_exits_3(tmp_path):
    code, result, report, out = _run(tmp_path, [("pTau217", "0.6", "ng/mL")])
    assert code == 3 and (out / "problems.json").exists()
    assert result["ptau217_two_cutoff_category"]["value"] is None
    assert "阳性" not in report.split("## 输入没有通过检查")[1].split("边界:")[0]


def test_out_of_range_exits_3(tmp_path):
    code, result, _, out = _run(tmp_path, [("pTau217", "600", "pg/mL")])
    assert code == 3 and (out / "problems.json").exists()
    assert result["ptau217_two_cutoff_category"]["value"] is None


@pytest.mark.parametrize("extra", [(), ("--assay", "lumipulse")])
def test_assay_must_be_simoa_alzpath(tmp_path, extra):
    code, result, report, _ = _run(tmp_path, [("pTau217", "0.6", "pg/mL")], extra=extra, name="a" + str(len(extra)))
    assert code == 3
    assert result["ptau217_two_cutoff_category"]["value"] is None
    assert "Simoa" in report


def test_bad_probability_exits_3(tmp_path):
    code, _, _, _ = _run(tmp_path, [("pTau217", "0.6", "pg/mL")], extra=("--assay", "simoa", "--probability", "0.7"))
    assert code == 3


def test_missing_ptau217_exits_3(tmp_path):
    code, _, report, _ = _run(tmp_path, [("Aβ42", "5", "pg/mL")])
    assert code == 3 and "pTau217" in report
