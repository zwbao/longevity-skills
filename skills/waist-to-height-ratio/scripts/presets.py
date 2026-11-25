"""Ashwell et al., Obesity Reviews 13 (2012), pp. 275–286.

Formula: p. 284, biological plausibility section (waist divided by height).
Boundary: p. 284, practical considerations. No fitted coefficients.
Input ranges are engineering guards, not paper-derived diagnostic cutoffs.
"""

SCREENING_BOUNDARY = 0.5
MEASUREMENT_UNITS = {"waist_cm": "cm", "height_cm": "cm"}
TITLE = "成人腰围身高比筛查报告"
BOUNDARY = "腰围身高比仅用于成人心代谢风险初筛，不是诊断、个人患病概率或寿命预测；不能据此开始、停止或调整药物。"
TARGET_NOTE = "目标由你提供；变化只表示腰围改变、身高保持不变时的算术结果，不代表患病概率或干预获益，也不是减重处方。身高敏感度仅用于理解测量误差。"
CATEGORY_LABELS = {
    "below_boundary": "低于筛查界值",
    "at_or_above_boundary": "达到或超过筛查界值",
}
