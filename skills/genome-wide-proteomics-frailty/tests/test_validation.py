"""HFRS checked against two independent implementations.

Neither this paper nor Gilbert et al. (Lancet 2018) prints a person's codes
with the resulting score, so nothing here reproduces a printed example. The
script (reading a one-column code list, as a user would hand it in) is
compared on synthetic diagnosis lists (random draws, not people;
random.Random(20261024)) with:

1. comorbidipy 0.8.0 (PyPI, MIT): comorbidipy.hfrs. It counts each distinct
   full code, so a list with two codes in the same three-character group
   (G81.8 and G81.4) scores that group twice. HFRS counts a group once, so
   comorbidipy is compared only on lists without such repeats.
2. m4 (hannesill/m4 at 5f6688a, MIT):
   src/m4/skills/clinical/hfrs/scripts/calculate_hfrs.py, calculate_hfrs(codes,
   icd_version=10), on every list. Run from a reviewed copy (standard library
   only).

Scores are sums of one-decimal weights; both must agree within 1e-9.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import personal_report

TOLERANCE = 1e-9

# codes, comorbidipy score (None where a group repeats), m4 score
CASES = [
    (['Z96.6', 'M54.5', 'F10.8', 'R31', 'E05.8', 'Z22.8'], 6.3, 6.3),
    (['J69', 'R11', 'I10', 'R44', 'K59.3', 'G31.0', 'R55.4', 'Z87.4', 'Z60', 'M54.5'], 11.0, 11.0),
    (['M41', 'K21.0', 'S51', 'G31', 'F05.0', 'M79.8', 'J45', 'R56', 'A04.0', 'H91.3', 'Y95'], 12.7, 12.7),
    (['W01', 'R79', 'K21.0', 'E83.7', 'T83.5', 'Z96.6', 'A04', 'R02', 'G20', 'M81', 'K59.1'], 11.4, 11.4),
    (['E53.7', 'Y84', 'Z73.0', 'I10', 'F32.1', 'W18', 'R26', 'M54.5'], 8.4, 8.4),
    (['I10', 'G30', 'N19', 'G20'], 7.4, 7.4),
    (['S72', 'J45', 'Y95', 'M54.5'], 2.6, 2.6),
    (['L97.0', 'Z96.6', 'I95.6', 'M54.5', 'N19.9', 'E53', 'R11'], 7.0, 7.0),
    (['E11.9', 'M25', 'J45', 'R40.0', 'M25.8'], None, 4.8),
    (['E16', 'S09.8', 'I10', 'L03.9', 'S09', 'Z22', 'M54.5', 'K59.9'], None, 8.1),
    (['Z96.6', 'J69.2', 'F01', 'R41', 'G81.8', 'G81.4', 'A09.8'], None, 11.2),
    (['Z60', 'W18', 'B95', 'G20.8', 'E05.5', 'Z50', 'I63', 'Z96.6', 'Y95', 'B95.8', 'H91.9', 'T83.9'], None, 15.7),
]


def _score(tmp_path: Path, codes) -> float:
    path = tmp_path / "codes.csv"
    path.write_text("\n".join(codes) + "\n", encoding="utf-8")
    rows, problems = personal_report.collect_inputs(path)
    assert problems == []
    return personal_report.scores(rows)["hfrs_score"]


@pytest.mark.parametrize("case", [case for case in CASES if case[1] is not None])
def test_matches_comorbidipy_hfrs(tmp_path: Path, case):
    assert _score(tmp_path, case[0]) == pytest.approx(case[1], abs=TOLERANCE)


@pytest.mark.parametrize("case", CASES)
def test_matches_m4_calculate_hfrs(tmp_path: Path, case):
    assert _score(tmp_path, case[0]) == pytest.approx(case[2], abs=TOLERANCE)
