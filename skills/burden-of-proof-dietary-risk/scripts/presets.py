"""Haile et al., Nature Medicine 31 (2025), Tables S13–S16.

Only the column INCLUDING between-study heterogeneity is used.
Zero is the mathematical reference RR=1 (Methods: TMREL=0), not a fitted row.
"""
import csv
from pathlib import Path

INPUT_UNITS = {"processed_meat_g_d": "g/d", "ssb_g_d": "g/d", "tfa_energy_pct": "%"}
INPUT_LABELS = {"processed_meat_g_d": "加工肉", "ssb_g_d": "含糖饮料", "tfa_energy_pct": "反式脂肪供能占比"}
# pair: input key, display name, supplementary table, evidence stars,
#       data-dense exposure range (15th–85th percentiles, rounded in abstract).
PAIRS = {
    "meat_t2d": ("processed_meat_g_d", "加工肉—2 型糖尿病", 13, 2, (0.6, 57)),
    "meat_crc": ("processed_meat_g_d", "加工肉—结直肠癌", 13, 2, (0.78, 55)),
    "meat_ihd": ("processed_meat_g_d", "加工肉—缺血性心脏病", 14, 1, None),
    "ssb_t2d": ("ssb_g_d", "含糖饮料—2 型糖尿病", 15, 2, (1.5, 390)),
    "ssb_ihd": ("ssb_g_d", "含糖饮料—缺血性心脏病", 15, 2, (0, 365)),
    "tfa_ihd": ("tfa_energy_pct", "反式脂肪—缺血性心脏病", 16, 2, (0.25, 2.56)),
}
with (Path(__file__).resolve().parents[1] / "data/risk_table.csv").open(encoding="utf-8", newline="") as f:
    TABLE_ROWS = list(csv.DictReader(f))
TABLES = {pair: {} for pair in PAIRS}
for row in TABLE_ROWS:
    TABLES[row["pair"]][float(row["intake"])] = tuple(float(row[k]) for k in ("rr", "ui_lower", "ui_upper"))
GRIDS = {key: sorted({0.0} | {x for pair, details in PAIRS.items() if details[0] == key for x in TABLES[pair]})
         for key in INPUT_UNITS}

TITLE = "饮食摄入量对应的已发表相对风险"
BOUNDARY = "这是对成年人前瞻性队列研究（每组食物—结局 6–19 项研究）做荟萃回归得到的群体关联查表，不是个人绝对发病概率、诊断或改变饮食后的因果预测；不能相乘或相加为总风险，不能据此开始或停用药物。"
LEVER_NOTE = "仅比较用户给定摄入量在同一张已发表表格中的读数，不推荐摄入量。这些离散表格不提供连续曲线的局部导数；相邻表格点的割线差值不是导数或干预效果。"
