"""Items, coding rules and cut points of the 32-item frailty index (CHARLS) used by
Zhang et al., Frailty trajectories and cardiovascular disease in adults with CKM
stages 0-3. GeroScience (2026). doi:10.1007/s11357-026-02559-3.

Sources (all opened; see references/contract.md):
- Methods, "Assessment of frailty status": 32 deficits, sum of deficit scores / 32,
  cut points robust FI <= 0.12, pre-frail 0.12 < FI <= 0.25, frail FI > 0.25.
- ESM 1 (11357_2026_2559_MOESM1_ESM.docx), Supplementary Table 2 "Components of the
  32-item frailty index": item list, coding rule and value range of every item, and
  the table notes repeating the formula and the cut points.
- Results, "Baseline frailty status and time to incident CVD" (Table 3, Model 2):
  hazard ratios of incident CVD by baseline frailty status.
"""

from __future__ import annotations

# Supplementary Table 2 notes: "The frailty index is calculated as the total sum of
# scores divided by 32."
N_ITEMS = 32
# Methods and Supplementary Table 2 notes: robust FI <= 0.12, pre-frail 0.12 < FI <= 0.25,
# frail FI > 0.25.
ROBUST_MAX = 0.12
PREFRAIL_MAX = 0.25
# Supplementary Table 2, item 31: "CESD-10 >10 = 1, <=10 = 0".
CESD10_CUT = 10

STATUS_ZH = {"robust": "强健", "prefrail": "衰弱前期", "frail": "衰弱"}
STATUS_EN = {"robust": "robust", "prefrail": "pre-frail", "frail": "frail"}
UNDETERMINED_ZH = "不能确定"

# Supplementary Table 2, items 1-30 (binary, Yes = 1, No = 0; item 13 Poor or fair = 1,
# excellent/very good/good = 0). Tuple: (No, key, domain, label_zh, paper wording, aliases).
BINARY_ITEMS = (
    (1, "hypertension_dx_yn", "共病", "高血压（医生诊断）", "self-reported physician-diagnosed hypertension",
     ["高血压", "hypertension", "确诊高血压"]),
    (2, "diabetes_dx_yn", "共病", "糖尿病（医生诊断）", "self-reported physician-diagnosed diabetes",
     ["糖尿病", "diabetes", "确诊糖尿病", "血糖高（医生诊断）"]),
    (3, "heart_disease_dx_yn", "共病", "心脏病（医生诊断）", "self-reported physician-diagnosed heart disease",
     ["心脏病", "heart disease", "冠心病", "心梗", "心绞痛", "心衰"]),
    (4, "stroke_dx_yn", "共病", "中风（医生诊断）", "self-reported physician-diagnosed stroke",
     ["中风", "脑卒中", "卒中", "stroke"]),
    (5, "cancer_dx_yn", "共病", "癌症（医生诊断）", "self-reported physician-diagnosed cancer",
     ["癌症", "恶性肿瘤", "cancer"]),
    (6, "arthritis_dx_yn", "共病", "关节炎或风湿病（医生诊断）", "self-reported physician-diagnosed arthritis",
     ["关节炎", "风湿", "arthritis"]),
    (7, "chronic_lung_disease_dx_yn", "共病", "慢性肺部疾病（医生诊断）",
     "self-reported physician-diagnosed chronic lung disease",
     ["慢性肺病", "慢阻肺", "慢性支气管炎", "肺气肿", "chronic lung disease", "COPD"]),
    (8, "asthma_dx_yn", "共病", "哮喘（医生诊断）", "self-reported physician-diagnosed asthma",
     ["哮喘", "asthma"]),
    (9, "psychiatric_dx_yn", "共病", "情感、神经或精神问题（医生诊断）",
     "self-reported physician-diagnosed emotional, nervous, or psychiatric problems",
     ["精神问题", "情感或精神问题", "psychiatric problems", "emotional nervous psychiatric problems"]),
    (10, "memory_disease_dx_yn", "共病", "与记忆相关的疾病（医生诊断）",
     "self-reported physician-diagnosed memory-related disease",
     ["记忆相关疾病", "老年痴呆", "痴呆", "memory-related disease"]),
    (11, "vision_problem_yn", "共病", "自报视力问题", "self-reported vision problems",
     ["视力问题", "视力差", "vision problems"]),
    (12, "hearing_problem_yn", "共病", "自报听力问题", "self-reported hearing problems",
     ["听力问题", "听力差", "hearing problems"]),
    (13, "self_rated_health_poor_yn", "共病", "自评健康一般或差", "self-reported general health status",
     ["自评健康", "自评健康状况", "self-rated health", "general health status"]),
    (14, "difficulty_dressing_yn", "躯体功能", "穿衣有困难", "difficulty with dressing",
     ["穿衣困难", "dressing"]),
    (15, "difficulty_bathing_yn", "躯体功能", "洗澡有困难", "difficulty with bathing or showering",
     ["洗澡困难", "bathing", "showering"]),
    (16, "difficulty_eating_yn", "躯体功能", "吃饭有困难", "difficulty with eating",
     ["吃饭困难", "eating"]),
    (17, "difficulty_bed_yn", "躯体功能", "上下床有困难", "difficulty with getting in and out of bed",
     ["上下床困难", "getting in and out of bed"]),
    (18, "difficulty_toilet_yn", "躯体功能", "上厕所有困难", "difficulty with using the toilet",
     ["上厕所困难", "using the toilet", "toileting"]),
    (19, "difficulty_money_yn", "躯体功能", "管钱有困难", "difficulty with managing money",
     ["管钱困难", "managing money"]),
    (20, "difficulty_medications_yn", "躯体功能", "自己吃药有困难", "difficulty with taking medications",
     ["吃药困难", "按时吃药困难", "taking medications"]),
    (21, "difficulty_shopping_yn", "躯体功能", "买东西有困难", "difficulty with shopping for groceries",
     ["买东西困难", "购物困难", "shopping for groceries"]),
    (22, "difficulty_meals_yn", "躯体功能", "做饭有困难", "difficulty with preparing meals",
     ["做饭困难", "preparing meals"]),
    (23, "difficulty_housework_yn", "躯体功能", "做家务有困难", "difficulty with doing housework",
     ["做家务困难", "doing housework"]),
    (24, "difficulty_walk_100yd_yn", "失能（活动）", "走 100 码（约 100 米）有困难", "mobility difficulty with walking 100 yards",
     ["走100米困难", "走一百米困难", "walking 100 yards"]),
    (25, "difficulty_rise_chair_yn", "失能（活动）", "久坐后从椅子上站起来有困难",
     "mobility difficulty with getting up from a chair after sitting for long periods",
     ["久坐后起身困难", "从椅子站起困难", "getting up from a chair"]),
    (26, "difficulty_stairs_yn", "失能（活动）", "不休息连续爬几层楼有困难",
     "mobility difficulty with climbing several flights of stairs without resting",
     ["爬楼困难", "连续爬几层楼困难", "climbing several flights of stairs"]),
    (27, "difficulty_lift_10jin_yn", "失能（活动）", "提或搬 10 斤重物有困难",
     "mobility difficulty with lifting or carrying weights over 10 pounds/jins",
     ["提10斤重物困难", "搬重物困难", "lifting or carrying weights"]),
    (28, "difficulty_pick_coin_yn", "失能（活动）", "从桌上捡起一枚硬币有困难",
     "mobility difficulty with picking up a coin from the table",
     ["捡硬币困难", "picking up a coin"]),
    (29, "difficulty_stoop_yn", "失能（活动）", "弯腰、屈膝或下蹲有困难",
     "mobility difficulty with stooping, kneeling, or crouching",
     ["弯腰下蹲困难", "stooping kneeling or crouching"]),
    (30, "difficulty_reach_yn", "失能（活动）", "手臂向上伸过肩膀有困难",
     "mobility difficulty with reaching arms above shoulder level",
     ["手臂上举困难", "reaching arms above shoulder level"]),
)

# Item 31 (Depression): CES-D-10 total score, dichotomised at > 10.
CESD_ITEM = (31, "cesd10_score", "抑郁", "CES-D-10 抑郁量表总分", "CESD-10 questionnaire",
             ["CES-D-10", "CESD-10", "CESD10", "CES-D 10 项", "抑郁量表", "CES-D-10 总分", "流调中心抑郁量表"])
# Item 32 (Cognition): "cognition score derived from memory test score and orientation test
# score", "continuous deficit score", value range 0 to 1. The paper does not print how the
# memory and orientation scores are scaled into the 0-1 deficit, so this skill reads the
# deficit itself and never derives it from raw test scores.
COGNITION_ITEM = (32, "cognition_deficit_0_1", "认知", "认知缺损分（0–1）",
                  "cognition score derived from memory test score and orientation test score",
                  ["认知缺损分", "cognition deficit", "cognitive deficit score", "认知缺陷分"])

ALL_KEYS = tuple(item[1] for item in BINARY_ITEMS) + (CESD_ITEM[1], COGNITION_ITEM[1])

# Text answers read as the item's coding (Supplementary Table 2 coding rules).
YES_WORDS = ("是", "有", "yes", "y", "true", "困难", "有困难", "确诊")
NO_WORDS = ("否", "无", "没有", "no", "n", "false", "没困难", "无困难", "不困难")
# Item 13: "Poor or fair = 1, excellent/very good/good = 0".
SELF_RATED_POOR = ("一般", "不好", "差", "很差", "很不好", "poor", "fair")
SELF_RATED_GOOD = ("极好", "很好", "好", "excellent", "very good", "good")

# Results, "Baseline frailty status and time to incident CVD" (Table 3, Model 2,
# reference robust): HR (95% CI) per outcome.
HR_MODEL2 = {
    "prefrail": {
        "total_cvd": (1.61, 1.33, 1.95),
        "heart_disease": (1.61, 1.29, 2.02),
        "stroke": (1.75, 1.24, 2.48),
    },
    "frail": {
        "total_cvd": (1.63, 1.23, 2.17),
        "heart_disease": (1.49, 1.06, 2.09),
        "stroke": (2.09, 1.28, 3.42),
    },
}
OUTCOME_ZH = {"total_cvd": "心血管病（心脏病或中风）", "heart_disease": "心脏病", "stroke": "中风"}

# Abstract, Methods and Results: cohort description.
COHORT = {
    "n": 4219,
    "cvd_events": 541,
    "min_age": 45,
    "median_age": 57.0,
    "female_pct": 53.8,
    # Results: median baseline (wave 1) FI of the three trajectory groups.
    "trajectory_median_fi": {"low-stable": 0.06, "moderate-gradual increase": 0.17, "high-rapid rise": 0.30},
    "trajectory_pct": {"low-stable": 68.0, "moderate-gradual increase": 26.2, "high-rapid rise": 5.7},
}

BOUNDARY = (
    "衰弱指数是 32 项健康缺陷的累计比例，分档沿用论文切点；它不是诊断，也不是你个人的心血管病概率。"
    "论文里的风险比是中国 45 岁及以上、基线没有心血管病和癌症的人群关联，不能说明因果。"
    "有不舒服或功能明显下降，请找医生评估；不要据此自行开始或停用任何药物。"
)
