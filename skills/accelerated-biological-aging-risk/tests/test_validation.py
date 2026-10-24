"""Phenotypic age checked against two independent implementations.

Levine 2018 prints the formula and its coefficients but no person's inputs
with the resulting phenotypic age, so nothing here reproduces a printed
example. Instead the script is compared case by case with:

1. BioAge (dayoonkwon/BioAge at b1f9fc0, GPL-3): `phenoage0` as stored in its
   `data/NHANES3.rda` (SHA-256 c1b940fc...0b92), computed by
   `R/phenoage_calc.R` with the unrounded weights and BioAge's
   `lncrp = log(1 + crp)`. Rows are NHANES III participants (US public-domain
   data); every 743rd of the 8,924 rows that carry `phenoage0`. On all 8,924
   rows the script's log1p mode agrees to 6.1e-08 years.
2. FALCONAge (bhagesh-h/FALCONAge at 86db10d, GPL-3):
   `python/src/falconage/models/clinical.py::phenoage(crp_transform="log",
   coefficients="bioage")`, run on synthetic inputs (made up, not people).
   The case with mortality rounding to 1 is left out: this script refuses it,
   FALCONAge clips it.

Both must agree within 0.01 years. Provenance and run notes are in
references/contract.md.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import personal_report

KEYS = ("age", "albumin_gL", "creat_umol", "glucose_mmol", "crp_mg_dl", "lymph_pct", "mcv_fl", "rdw_pct", "alp_u_l", "wbc_10e3")
TOLERANCE_YEARS = 0.01

# sampleID, age, albumin g/L, creatinine umol/L, glucose mmol/L, CRP mg/dL, lymphocyte %, MCV fL, RDW %, ALP U/L,
# WBC 10^3/uL, BioAge phenoage0
BIOAGE_NHANES3 = [
    ("1991_9", 48, 40, 51.62659381, 6.0495, 0.2099999934, 32.34999847, 92.40000153, 12.05000019, 59, 4.949999809, 39.8804215),
    ("1991_3818", 47, 41.99999809, 68.5997192, 6.8265, 0.2099999934, 22.29999924, 98.59999847, 12.64999962, 98, 6.949999809, 49.13248253),
    ("1991_7681", 33, 43.00000191, 60.11315398, 4.551, 0.2099999934, 28.04999924, 90.65000153, 12.89999962, 85, 9.050000191, 29.27231108),
    ("1991_11752", 37, 44.00000095, 51.62659381, 6.216, 0.4399999976, 33.84999847, 81.84999847, 13.69999981, 77, 5.449999809, 32.53121607),
    ("1991_15618", 29, 39.00000095, 68.5997192, 4.884, 0.2099999934, 32.90000153, 85.40000153, 13.39999962, 62, 8.399999619, 27.56731106),
    ("1991_19307", 81, 41.99999809, 68.5997192, 6.0495, 0.2099999934, 28.70000076, 95.65000153, 12.5, 77, 7.900000095, 75.62082723),
    ("1991_32928", 34, 40.99999905, 68.5997192, 4.773, 0.2099999934, 38.25, 87.84999847, 12.05000019, 38, 6.099999905, 24.19145663),
    ("1991_36182", 52, 39.00000095, 60.11315398, 5.0505, 1.700000048, 30.64999962, 82.90000153, 14.44999981, 97, 10.60000038, 53.86461496),
    ("1991_39588", 84, 40, 85.57284965, 6.216, 0.3000000119, 27.60000038, 82.65000153, 14, 60, 6.5, 81.84046351),
    ("1991_43203", 69, 40, 68.5997192, 5.0505, 0.400000006, 30.95000076, 86.05000305, 13.25, 71, 7.949999809, 63.16938939),
    ("1991_46591", 64, 41.99999809, 77.08628442, 6.438, 1.100000024, 45.75, 85.55000305, 13.89999962, 91, 5.349999905, 61.37922301),
    ("1991_50072", 58, 41.99999809, 77.08628442, 5.883, 0.6999999881, 33.15000153, 85.94999695, 13.35000038, 99, 6.550000191, 55.28870703),
]

# Synthetic. age, albumin, creatinine, glucose, CRP, lymphocyte %, MCV, RDW, ALP, WBC, FALCONAge phenoage
FALCONAGE_SYNTHETIC = [
    (58, 45, 80, 5.0, 0.2, 32, 90, 13.2, 70, 6.5, 50.475252),
    (40, 45, 80, 5.0, 0.1, 30, 90, 13.0, 70, 6.0, 32.926277),
    (25, 48, 62, 4.6, 0.03, 38, 88, 12.1, 55, 5.1, 8.580437),
    (72, 41, 110, 7.8, 0.9, 22, 95, 15.4, 110, 8.9, 88.447796),
    (50, 43, 70, 5.6, 0.35, 28, 92, 13.8, 85, 7.2, 48.995517),
    (33, 50, 55, 4.9, 0.05, 41, 86, 11.8, 48, 4.4, 12.748544),
    (66, 44, 95, 6.3, 0.6, 25, 97, 14.6, 92, 9.8, 74.164352),
]


@pytest.mark.parametrize("row", BIOAGE_NHANES3, ids=[row[0] for row in BIOAGE_NHANES3])
def test_matches_bioage_phenoage0_on_nhanes3(row):
    values = dict(zip(KEYS, row[1:11]))
    assert personal_report.phenotypic_age(values, "log1p") == pytest.approx(row[11], abs=TOLERANCE_YEARS)


@pytest.mark.parametrize("row", FALCONAGE_SYNTHETIC)
def test_matches_falconage_phenoage(row):
    values = dict(zip(KEYS, row[:10]))
    assert personal_report.phenotypic_age(values, "ln") == pytest.approx(row[10], abs=TOLERANCE_YEARS)
