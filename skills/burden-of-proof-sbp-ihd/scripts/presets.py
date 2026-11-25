"""Frozen published readout, Razo et al., Nature Medicine 28 (2022).

Table 4, Supplementary Information pp. 8–9. The reference UI is normalized
to zero width as stated in Discussion, limitations of the modeling approach.
No fitted spline coefficients are inferred here.
"""
import csv
from pathlib import Path

INPUT_KEY = "sbp_mmhg"
INPUT_UNIT = "mmHg"
PLAUSIBLE_RANGE = (50, 300)  # Input sanity check, NOT a clinical cutoff.
TABLE_RANGE = (100, 200)
REFERENCE_SBP = 100
DENSE_RANGE = (107.5, 165)
TITLE = "收缩压与缺血性心脏病相对风险查算"
BOUNDARY = (
    "这是把你的收缩压放到已发表人群曲线上的查算，不是个人发病概率、诊断或治疗建议；"
    "目标值对比不代表个人降压治疗的获益，不能据此开始、停用或调整药物。"
)
TABLE_PATH = Path(__file__).resolve().parents[1] / "data/supplementary_table_4.csv"
with TABLE_PATH.open(encoding="utf-8", newline="") as stream:
    TABLE = tuple({key: float(value) for key, value in row.items()}
                  for row in csv.DictReader(stream))
RR_KEYS = ("ihd_rr", "ihd_rr_ui_lower", "ihd_rr_ui_upper")
