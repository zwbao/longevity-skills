"""Published MitoAge coefficients: Supplementary Data 1, MitoAge sheet.

Table 2 (PDF p. 5) labels the sex coefficient Sex (Male).
No centering, rescaling or response inverse transform is inferred.
"""
import csv
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'
with (DATA / 'coefficients.csv').open(encoding='utf-8') as f:
    PROTEINS = list(csv.DictReader(f))
CONSTANTS = json.loads((DATA / 'constants.json').read_text())
INTERCEPT = CONSTANTS['intercept']
SEX_MALE_WEIGHT = CONSTANTS['sex_male_weight']
WEIGHTS = {p['key']: float(p['weight']) for p in PROTEINS}
INPUT_UNIT = '1'
# Broad engineering guard for ln(RFU), not a clinical interval from the paper.
INPUT_RANGE = (-20, 30)
DERIVATION_AGES = (22, 92)
PREPROCESSING = 'somascan-1.3k-ln-qc'
