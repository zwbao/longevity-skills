"""Definitions from Hosseini et al., PNAS 2026; source map in contract.md.

No fitted regression coefficients or clinical thresholds are used.
"""
CYCLE_BINS = 25  # Main text: Normalization of Segmented Data.
JOINTS = ("hip", "knee", "ankle", "midfoot")
FRAME_KEYS = ("time_s",) + tuple(f"{j}_{axis}_cm" for j in JOINTS for axis in ("x", "y"))
ANGLE_TRIPLES = {"knee": ("hip", "knee", "ankle"), "ankle": ("knee", "ankle", "midfoot")}
TITLE = "个人步态运动学读出"
BOUNDARY = "本报告描述已标注步态周期的二维运动学，不测量地面反作用力或肌力，不判断衰弱、跌倒风险或生物年龄，也不能据此调整药物。"
