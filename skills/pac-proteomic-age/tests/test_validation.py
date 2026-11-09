"""Case-by-case agreement with two independent implementations of PAC.

The paper (Zhavoronkov et al., Nat Biotechnol 2026) prints PAC predictions for
42 trial participants in Supplementary Table 2, but their Olink NPX are in
OMIX008341, which is controlled access, so no printed example can be rerun.
Instead seven synthetic NPX profiles (tests/fixtures/synthetic_npx.csv, not
real people; syn_7 is all zeros) were run on 2026-11-09 through:

1. kuo-lab-uchc/PAC pac_proteomic_age.R (commit e15edb66800f876a928cec9c8856500048c46fea), Rscript.
2. Insilico-org/proteoclock GompertzClock with kuo_2024 weights, scaling=None
   (commit d078b246c9a834bb1eaa54a79381b6c6c14245f7) - the library the paper used.

The expected numbers below are those programs' printed outputs.
"""

import json

import pytest

import personal_report
from conftest import synthetic_subjects, write_rows

SUBJECTS = ["syn_1", "syn_2", "syn_3", "syn_4", "syn_5", "syn_6", "syn_7"]

# Rscript pac_proteomic_age.R output, rounded to 6 decimals.
R_PAC = [52.803729, 42.734027, 37.191619, 60.479266, 47.886142, 62.90474, 52.721563]

# proteoclock GompertzClock.predict_age output (float32), 6 decimals.
PROTEOCLOCK_PAC = [52.821877, 42.752174, 37.209766, 60.497413, 47.904291, 62.922887, 52.739711]


def _run(tmp_path, subject):
    age, rows = synthetic_subjects()[subject]
    path = write_rows(tmp_path / f"{subject}.csv", rows)
    out = tmp_path / f"out_{subject}"
    assert personal_report.main(["--measurements", str(path), "--age", str(age), "--out", str(out)]) == 0
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    return result["outputs"]["pac_age"]["value"]


def test_matches_original_pac_r_code(tmp_path):
    for subject, expected in zip(SUBJECTS, R_PAC):
        assert _run(tmp_path, subject) == pytest.approx(expected, abs=1e-5), subject


def test_matches_proteoclock_kuo_2024(tmp_path):
    # proteoclock stores the Gompertz rate rounded to 2.32E-04; that shifts PAC by
    # log(2.32e-4 / 0.000231560557596016) / 0.1087932 = +0.0175 years.
    shift = __import__("math").log(2.32e-4 / 0.000231560557596016) / 0.1087932
    for subject, expected in zip(SUBJECTS, PROTEOCLOCK_PAC):
        mine = _run(tmp_path, subject)
        assert mine == pytest.approx(expected, abs=0.03), subject
        assert mine + shift == pytest.approx(expected, abs=1e-3), subject
