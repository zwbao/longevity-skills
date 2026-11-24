"""Original CSHA Clinical Frailty Scale, Rockwood et al. 2005, Box 1.

These are whole clinical descriptors, not independently additive symptoms.
The 0/1 selection format is an interface encoding, not a paper coefficient.
"""

SELECTION_UNIT = "1"
SELECTION_RANGE = (0, 1)
BOUNDARY = "本报告仅把临床人员确认的描述对应到 2005 年原版七级临床衰弱量表，不替代临床评估，不预测个人死亡或入住照护机构的概率，也不用于决定开始或停止药物。"

DESCRIPTORS = {
    "very_fit_selected": {
        "grade": 1, "label_zh": "非常健壮", "label_en": "Very fit",
        "description_zh": "精力和体能充沛、积极主动，通常规律锻炼，属于同龄人中体能最好的群体。",
    },
    "well_selected": {
        "grade": 2, "label_zh": "健康", "label_en": "Well",
        "description_zh": "没有活动性疾病，但体能不及非常健壮的人。",
    },
    "well_treated_comorbidity_selected": {
        "grade": 3, "label_zh": "健康但有已治疗的合并疾病",
        "label_en": "Well, with treated comorbid disease",
        "description_zh": "合并疾病的症状控制良好，较看似易受损的状态控制得更好。",
    },
    "apparently_vulnerable_selected": {
        "grade": 4, "label_zh": "看似易受损", "label_en": "Apparently vulnerable",
        "description_zh": "尚无明显依赖，但常觉得行动变慢，或存在疾病症状。",
    },
    "mildly_frail_selected": {
        "grade": 5, "label_zh": "轻度衰弱", "label_en": "Mildly frail",
        "description_zh": "在工具性日常生活活动方面有限度地依赖他人。",
    },
    "moderately_frail_selected": {
        "grade": 6, "label_zh": "中度衰弱", "label_en": "Moderately frail",
        "description_zh": "工具性及非工具性日常生活活动都需要他人帮助。",
    },
    "severely_frail_selected": {
        "grade": 7, "label_zh": "重度衰弱", "label_en": "Severely frail",
        "description_zh": "日常生活活动完全依赖他人，或处于终末期疾病状态。",
    },
}
