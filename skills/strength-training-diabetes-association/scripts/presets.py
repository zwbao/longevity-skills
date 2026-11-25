"""Momma et al., BJSM 2022, Table 1, diabetes linear dose-response row."""

INCREMENT_MIN_WEEK = 10.0
RR_PER_INCREMENT = 0.98
CI_LOWER_PER_INCREMENT = 0.97
CI_UPPER_PER_INCREMENT = 0.99
INPUT_KEY = "strength_min_week"
INPUT_UNIT = "min"
# Arithmetic input guard: minutes in a week, not a validated exposure limit.
INPUT_RANGE = (0, 10080)
AGE_RANGE = (18, 120)  # Adult eligibility plus administrative plausibility bound.
STUDY_AGE_RANGE = (36, 97.8)  # Appendix Table 6, the three dose-response studies.
TITLE = "每周力量训练时长与糖尿病的线性关联"
BOUNDARY = (
    "这是成人观察性队列荟萃分析的群体线性关联换算，不是你的糖尿病发病概率、"
    "因果效果或训练处方。论文同时观察到非线性关系，不能据此推断训练越多越好；"
    "不能据此开始、停止或调整药物。"
)
