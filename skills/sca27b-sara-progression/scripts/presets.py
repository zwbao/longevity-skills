"""Constants printed in the SCA27B multicentre SARA progression study.

[P] Traschütz A, Hilgers R-D, Erdlenbruch F, et al. Longitudinal progression,
    metrics, age-dependence, and modifiers of ataxia severity in SCA27B: a
    multicentre study of 219 patients. eBioMedicine. 2026;131:106437.
    doi:10.1016/j.ebiom.2026.106437 (CC BY 4.0). Full text: Europe PMC
    PMC13503081; Supplementary Material (mmc1.docx, Tables S1, S3, S4, S5)
    from the Europe PMC supplementaryFiles endpoint.

Every number below names the place it is printed. Nothing is fitted or
reconstructed. Table S4 covariates are centred in the SAS model and the
centring constants are not printed, so only contrasts between two people who
differ in one covariate are computed (they do not depend on centring).
"""

from __future__ import annotations

# Methods "Study cohort": SARA items and their scoring ranges; total 0-40.
SARA_ITEMS = (
    # key, label_zh, maximum
    ("sara_gait_score", "步态", 8),
    ("sara_stance_score", "站姿", 6),
    ("sara_sitting_score", "坐姿", 4),
    ("sara_speech_score", "言语", 6),
    ("sara_finger_chase_score", "手指追踪", 4),
    ("sara_nose_finger_score", "指鼻试验", 4),
    ("sara_fast_alternating_score", "快速轮替动作", 4),
    ("sara_heel_shin_score", "跟膝胫试验", 4),
)
SARA_MAX = 40

# Methods "Statistics": ambulatory sub-cohort = SARA gait item <= 3.
AMBULATORY_GAIT_MAX = 3

# Results "Progression modelling ...": annual SARA progression (LMEM), points/year [95% CI].
PROGRESSION_OVERALL = (0.54, 0.37, 0.71)
PROGRESSION_AMBULATORY = (0.40, 0.26, 0.55)

# Table S4 (LMEM, SARA total score): unrounded estimates [lower, upper 95% CI].
S4_TIME = (0.5412, 0.3678, 0.7145)                      # "Time since baseline (years)"
S4_TIME_X_SHORT = (0.004802, 0.001941, 0.007663)        # "Time since baseline x GAA repeat size on shorter allele" (per repeat)

# Table 1: median GAA repeats on the shorter allele (IQR 9-53). Used as the
# reference person for the per-repeat contrast; it is a printed cohort value.
SHORT_ALLELE_MEDIAN = 16

# Results "Modification of progression ...": dichotomised short-allele thresholds,
# SARA points/year faster above than below [95% CI], separate LMEMs.
SHORT_ALLELE_GT180 = (1.6, 0.9, 2.2)    # (GAA) > 180
SHORT_ALLELE_GE250 = (3.2, 1.4, 5.0)    # (GAA) >= 250
SHORT_THRESHOLD_LOW = 180
PATHOGENIC_THRESHOLD = 250              # Methods "Genotyping": >= 250 uninterrupted repeats on the longer allele

# Table S5 (item-level LMEM): overall progression (points/year) and
# "Progression x Repeat size on short allele (per 100 repeats)", estimate [95% CI].
S5_ITEMS = {
    "sara_gait_score": {"overall": 0.202, "short_per100": (0.158, 0.094, 0.224)},
    "sara_stance_score": {"overall": 0.158, "short_per100": (0.074, 0.025, 0.124)},
    "sara_sitting_score": {"overall": 0.036, "short_per100": (0.053, 0.020, 0.086)},
    "sara_speech_score": {"overall": 0.035, "short_per100": (0.061, 0.011, 0.110)},
    "sara_finger_chase_score": {"overall": 0.039, "short_per100": (0.031, -0.002, 0.064)},
    "sara_nose_finger_score": {"overall": 0.043, "short_per100": (0.026, -0.008, 0.059)},
    "sara_fast_alternating_score": {"overall": 0.036, "short_per100": (0.008, -0.024, 0.041)},
    "sara_heel_shin_score": {"overall": 0.026, "short_per100": (0.055, 0.022, 0.088)},
}

# Results "SARA scores in SCA27B relative to healthy controls across age groups".
# Decade -> (SCA27B median, IQR low, IQR high); only the decades printed in the text.
SCA27B_DECADE_MEDIAN = {
    40: (2.5, 1.5, 11),
    50: (6, 3.5, 12),
    60: (6, 4, 10),
    70: (8.5, 5, 12.5),
}
# Healthy controls (n = 390): 90th percentile of SARA total per decade, printed for 50-80 only.
CONTROL_P90 = {50: 1, 60: 2.5, 70: 5}
# Healthy control medians printed in the text (40-50 and 70-80 only).
CONTROL_MEDIAN = {40: 0, 70: 1.25}
# AUC SCA27B vs controls by decade (Results and Fig. 3 legend).
AUC_BY_DECADE = {50: 0.97, 60: 0.95, 70: 0.91}

COHORT = {
    "patients": 219,
    "assessments": 661,
    "female": 101,
    "controls": 390,
    "controls_age": (18, 79),
    "longitudinal": 116,
    "centres": 9,
    "excluded_comorbidity": 14,
    "age_range": (24, 86),
}

BOUNDARY = (
    "这是 SCA27B 患者队列的人群平均进展和关联，不是你个人的病程预测，也不是诊断；"
    "SARA 必须由受过训练的医生评分，其他疾病、跌倒或手术后状态也会让分数升高。"
    "是否开始、调整或停止任何治疗，请和你的神经科医生商量。"
)
