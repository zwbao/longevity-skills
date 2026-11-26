"""Dai et al. 2026, Table 3 (p. 984): frozen printed RR and 95% UI.

UI includes between-study heterogeneity. These are mean RRs, not the BPRF.
Reference RR=1 follows the paper's definition (current versus no alcohol).
"""
import csv
from pathlib import Path

ALCOHOL_INPUT = ("alcohol_g_day", "每日纯酒精摄入量", "g/d")
MIN_EXPOSURE = 0
MAX_EXPOSURE = 100
GRAMS_PER_PAPER_DRINK = 10
GRID = tuple(range(MIN_EXPOSURE, MAX_EXPOSURE + 1, GRAMS_PER_PAPER_DRINK))
REFERENCE_RR = 1.0
TABLE_PATH = Path(__file__).resolve().parents[1] / "data" / "table3.csv"

OUTCOMES = (
    ("breast_cancer", "乳腺癌（女性研究）"),
    ("colorectal_cancer", "结直肠癌"),
    ("oesophageal_cancer", "食管癌"),
    ("laryngeal_cancer", "喉癌"),
    ("lip_oral_cavity_cancer", "唇及口腔癌"),
    ("liver_cancer", "肝癌"),
    ("pancreatic_cancer", "胰腺癌"),
    ("other_pharyngeal_cancer", "其他咽癌（不含鼻咽癌）"),
    ("prostate_cancer", "前列腺癌（男性研究）"),
    ("stomach_cancer", "胃癌"),
    ("atrial_fibrillation_flutter", "心房颤动及扑动"),
    ("ischaemic_heart_disease", "缺血性心脏病"),
    ("ischaemic_stroke", "缺血性卒中"),
    ("haemorrhagic_stroke", "出血性卒中"),
    ("alzheimers_other_dementias", "阿尔茨海默病及其他痴呆"),
    ("cirrhosis_chronic_liver_diseases", "肝硬化及其他慢性肝病"),
    ("type_2_diabetes", "2 型糖尿病"),
    ("lower_respiratory_infections", "下呼吸道感染"),
    ("pancreatitis", "胰腺炎"),
    ("tuberculosis", "结核病"),
)


def load_table():
    table = {}
    with TABLE_PATH.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            table[(row["outcome"], int(row["alcohol_g_day"]))] = (
                float(row["rr"]), float(row["ui_low"]), float(row["ui_high"])
            )
    expected = {(key, g) for key, _ in OUTCOMES for g in GRID if g > 0}
    if set(table) != expected:
        raise ValueError("Frozen Table 3 is incomplete")
    return table


TABLE = load_table()
