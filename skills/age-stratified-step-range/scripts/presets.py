"""Printed constants: Results/Figure 3 and Appendix Figure S2c (p19)."""
AGE_SPLIT_YEARS = 60
OLDER_RANGE = (6000, 8000)
YOUNGER_RANGE = (8000, 10000)
# Engineering input guards, NOT cohort limits or clinical thresholds.
AGE_INPUT_RANGE = (18, 130)
STEP_INPUT_RANGE = (0, 100000)
COUNT_UNIT = "1"  # Count in a fixed daily window; displayed as 步/日.
TITLE = "按年龄比较日均步数"
BOUNDARY = "这是观察性人群研究中日均步数与死亡的关联范围，不是个人死亡风险、因果效应或运动处方；高于范围不表示有害或应减少步数，也不能据此开始或停止任何药物。"
LABELS = {"below": "低于论文所述平台范围", "within": "落在论文所述平台范围内", "above": "高于论文所述平台范围"}


def reference_range(age):
    return OLDER_RANGE if age >= AGE_SPLIT_YEARS else YOUNGER_RANGE


def evaluate(age, steps):
    low, high = reference_range(age)
    return {
        "daily_steps": steps,
        "age_group": "ge_60" if age >= AGE_SPLIT_YEARS else "under_60",
        "reference_low_daily_steps": low,
        "reference_high_daily_steps": high,
        "step_position": "below" if steps < low else "above" if steps > high else "within",
        "difference_from_low_daily_steps": steps - low,
        "difference_from_high_daily_steps": steps - high,
    }
