"""Bastien et al., Sleep Medicine 2 (2001), Fig. 1, p.299.

All scoring constants are printed in Fig. 1; no fitted weights.
"""

ITEM_LABELS = {
    "sleep_onset_score": "入睡困难",
    "sleep_maintenance_score": "睡眠维持困难",
    "early_awakening_score": "早醒",
    "sleep_dissatisfaction_score": "对睡眠的不满意程度",
    "daily_interference_score": "日间功能干扰",
    "noticeability_score": "自觉他人能察觉的生活质量影响",
    "sleep_distress_score": "对睡眠问题的担忧或苦恼",
}
ITEM_MIN, ITEM_MAX = 0, 4
ITEM_COUNT = 7
TOTAL_MAX = 28
MEASUREMENTS = {key: ("score", (ITEM_MIN, ITEM_MAX)) for key in ITEM_LABELS}
BANDS = (
    (0, 7, "no_clinically_significant_insomnia", "未达临床显著失眠分档"),
    (8, 14, "subthreshold_insomnia", "阈下失眠分档"),
    (15, 21, "moderate_insomnia", "中度失眠分档"),
    (22, 28, "severe_insomnia", "重度失眠分档"),
)
CATEGORY_ZH = {code: label for _, _, code, label in BANDS}
# Study 1 p.298; Study 2 p.301. These are observed ages, not score cutoffs.
STUDY_AGES = ((17, 82), (55, 84))
BOUNDARY = (
    "本结果仅量化过去两周自觉失眠严重程度，分档不等于临床诊断，不能判断失眠病因、"
    "个人治疗获益或寿命；不能据此开始、停用或调整药物。"
)
