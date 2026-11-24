"""Table S12, medRxiv v3, supplement p. 19; exact discrete lookup only."""

import csv
from pathlib import Path

AGE_UNIT = "a"
LATENCY_UNIT = "ms"
# Broad input plausibility guards, not diagnostic thresholds. The narrower
# published grid is enforced separately and is never rounded to.
AGE_RANGE_YEARS = (20, 84)
LATENCY_RANGE_MS = (0.5, 3)
AGE_GRID = (45, 55, 65, 75)
LATENCY_GRID_MS = (1, 1.2667, 1.4, 1.48, 1.83)
OUTPUT_KEYS = (
    "ws_reference_pct", "ws_mean_se_pp", "ws_mean_ci_lower_pct", "ws_mean_ci_upper_pct",
    "ps_reference_pct", "ps_mean_se_pp", "ps_mean_ci_lower_pct", "ps_mean_ci_upper_pct",
)
TITLE = "年龄与听觉潜伏期的言语识别原表参考"
BOUNDARY = (
    "预印本，未经同行评审；结果仅为原表中其他连续协变量取中心化零值、"
    "性别取男性参考设定时的模型均值，不是你的实测言语得分、个人预测区间、"
    "诊断或干预效果，不能据此开始或停止用药。"
)

TABLE = {}
with (Path(__file__).resolve().parents[1] / "data/table_s12.csv").open(encoding="utf-8", newline="") as handle:
    for row in csv.DictReader(handle):
        key = (int(row["age_years"]), float(row["w1_latency_ms"]))
        if key in TABLE:
            raise ValueError("Duplicate Table S12 row")
        TABLE[key] = {name: float(row[name]) for name in OUTPUT_KEYS}

