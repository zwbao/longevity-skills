"""Malmstrom & Morley 2013: Table 1 and p. 531, third body paragraph."""

MEASUREMENTS = {
    "strength_score": ("score", (0, 2)),
    "walking_score": ("score", (0, 2)),
    "chair_score": ("score", (0, 2)),
    "stairs_score": ("score", (0, 2)),
    # 1000 is an application input guard, not a published clinical threshold.
    "falls_past_year_count": ("1", (0, 1000)),
}
DIRECT_SCORE_KEYS = tuple(key for key in MEASUREMENTS if key.endswith("_score"))
FALLS_HIGH_THRESHOLD = 4
FALLS_POINTS = (0, 1, 2)
POSITIVE_CUTOFF = 4
MAX_SCORE = 10
LABELS = {
    "strength_score": "提起并搬运10磅物品",
    "walking_score": "步行穿过房间",
    "chair_score": "从椅子或床转移",
    "stairs_score": "上10级台阶",
    "falls_score": "过去一年跌倒",
}
ANSWER_LABELS = {
    "strength_score": ("无困难", "有些困难", "很困难或无法完成"),
    "walking_score": ("无困难", "有些困难", "很困难、使用辅助器具或无法完成"),
    "chair_score": ("无困难", "有些困难", "很困难或不借助他人无法完成"),
    "stairs_score": ("无困难", "有些困难", "很困难或无法完成"),
}
CATEGORY_ZH = {
    "screen_positive": "达到筛查界值（提示肌少症风险）",
    "below_cutoff": "低于筛查界值（不能排除肌少症）",
}
BOUNDARY = (
    "SARC-F 是肌少症风险筛查问卷，不能单独确诊或排除肌少症，不能估计个人患病概率或预期寿命；"
    "本文仅描述初步研究，未报告完整验证样本与诊断准确度；不能据此开始、停止或调整药物。"
)
