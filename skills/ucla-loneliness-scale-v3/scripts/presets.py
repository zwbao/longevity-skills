"""Scoring constants transcribed from Russell (1996), Table 1, p. 23.

There are no fitted coefficients in the sum score. Factor loadings in Table 8
are not scoring weights. Range endpoints below follow from summing item scores.
"""

ITEM_NUMBERS = tuple(range(1, 21))
REVERSE_ITEMS = frozenset((1, 5, 6, 9, 10, 15, 16, 19, 20))
REVERSE_POINTS = {1: 4, 2: 3, 3: 2, 4: 1}
RESPONSE_LABELS = {1: "从不（Never）", 2: "很少（Rarely）",
                   3: "有时（Sometimes）", 4: "总是（Always）"}
MEASUREMENTS = {f"ucla_v3_item_{i:02d}_response_score": ("score", (1, 4))
                for i in ITEM_NUMBERS}
TOTAL_RANGE = (len(ITEM_NUMBERS) * min(REVERSE_POINTS),
               len(ITEM_NUMBERS) * max(REVERSE_POINTS))
BOUNDARY = (
    "本结果仅描述自报的孤独感，不是精神疾病诊断，不提供轻中重分档、个人疾病风险或寿命预测；"
    "不能据此开始、停用或调整药物。"
)
LANGUAGE_NOTE = (
    "本论文验证的是英文量表；未经本论文验证的中文译本不能直接视为与英文原版等效。"
    "请确认使用第三版完整问卷及其题序；本报告的中文说明不是经验证的中文问卷。"
)
