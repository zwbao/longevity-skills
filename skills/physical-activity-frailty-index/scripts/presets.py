"""Constants from Ji, GeroScience 2026 (doi:10.1007/s11357-026-02480-9), CHARLS 2011 baseline, age >= 60.

Every number below is copied from the article page (Methods, Tables 1, 2, 4, 5; Figures 6, 7)
or from Supplementary file 1 (11357_2026_2480_MOESM1_ESM.docx, Supplementary Tables 1 and 2).
Operational choices the paper does not fix are marked OPERATIONAL and explained in
references/contract.md.
"""

from __future__ import annotations

PAPER = "Ji, GeroScience 2026, doi:10.1007/s11357-026-02480-9"

# Methods, "Physical activity assessment": Total PA = (2 x HPA) + MPA + (0.5 x LPA), minutes/week.
PA_WEIGHTS = {"hpa": 2.0, "mpa": 1.0, "lpa": 0.5}
# Methods: >= 150 min/week guideline (WHO); categories 0, 1-149, 150-299, >= 300 min/week.
PA_GUIDELINE_MIN = 150.0
PA_CATEGORY_LABELS = ("0 分钟/周", "1–149 分钟/周", "150–299 分钟/周", "≥300 分钟/周")
PA_DOMAINS = ("total", "hpa", "mpa", "lpa")
PA_DOMAIN_ZH = {"total": "总活动量（加权）", "hpa": "高强度活动", "mpa": "中等强度活动", "lpa": "低强度活动"}

# Methods, "Frailty index assessment" and Results "Associations of frailty score ...":
# FI > 0.10 frailty syndrome; healthy FI <= 0.10, pre-frail 0.10 < FI <= 0.21, frail FI > 0.21.
FI_ITEMS_TOTAL = 48
FI_HEALTHY_MAX = 0.10
FI_PREFRAIL_MAX = 0.21
# FP: score > 1 frailty syndrome; healthy FP <= 1, pre-frail 1 < FP <= 2, frail FP > 2.
FP_HEALTHY_MAX = 1
FP_PREFRAIL_MAX = 2

# Table 1 / Table 2 item 12: BMI < 18.5 or >= 25 kg/m2 = 1.
BMI_LOW, BMI_HIGH = 18.5, 25.0

# Table 2, item scores by answer kind. Answer codes are what the person types (see skill.json note_zh).
# adl4: No = 0; a little = 0.33; need help = 0.67; Yes (cannot do it) = 1.
# cesd_neg: seldom or never = 0; often = 0.33; sometimes = 0.67; always = 1   (OPERATIONAL day ranges)
# cesd_pos: seldom or never = 1; often = 0.67; sometimes = 0.33; always = 0   (OPERATIONAL day ranges)
# srh5 / ls5: 0, 0.25, 0.5, 0.75, 1.
SCORES = {
    "adl4": {1: 0.0, 2: 0.33, 3: 0.67, 4: 1.0},
    "yesno": {0: 0.0, 1: 1.0},
    "cesd_neg": {1: 0.0, 2: 0.33, 3: 0.67, 4: 1.0},
    "cesd_pos": {1: 1.0, 2: 0.67, 3: 0.33, 4: 0.0},
    "srh5": {1: 0.0, 2: 0.25, 3: 0.5, 4: 0.75, 5: 1.0},
    "ls5": {1: 0.0, 2: 0.25, 3: 0.5, 4: 0.75, 5: 1.0},
}
ANSWER_ZH = {
    "adl4": "1 = 没有困难；2 = 有困难但仍能完成；3 = 有困难，需要帮助；4 = 无法完成",
    "yesno": "0 = 没有；1 = 医生诊断过",
    "cesd_neg": "过去一周：1 = 很少或没有（不到 1 天）；2 = 1–2 天；3 = 3–4 天；4 = 大多数时间（5–7 天）",
    "cesd_pos": "过去一周：1 = 很少或没有（不到 1 天）；2 = 1–2 天；3 = 3–4 天；4 = 大多数时间（5–7 天）",
    "srh5": "1 = 很好；2 = 好；3 = 一般；4 = 不好；5 = 很不好",
    "ls5": "1 = 非常满意；2 = 满意；3 = 一般；4 = 不满意；5 = 非常不满意",
}

# Table 2: (item number, input key, label_zh, paper label, CHARLS code or "", kind).
# Item 12 (BMI) and items 45-48 (laboratory) are handled separately below.
FI_QUESTION_ITEMS = (
    (1, "fi01_bathing", "洗澡有困难", "Bathing", "db011", "adl4"),
    (2, "fi02_dressing", "穿衣有困难", "Dressing", "db010", "adl4"),
    (3, "fi03_toileting", "上厕所有困难", "Use of toilet", "db014", "adl4"),
    (4, "fi04_transferring", "上下床有困难", "Transferring", "db013", "adl4"),
    (5, "fi05_continence", "控制大小便有困难", "Continence", "db015", "adl4"),
    (6, "fi06_eating", "吃饭有困难", "Eating", "db012", "adl4"),
    (7, "fi07_cooking", "做饭有困难", "Cooking", "db017", "adl4"),
    (8, "fi08_shopping", "买东西有困难", "Shopping", "db018", "adl4"),
    (9, "fi09_housework", "做家务有困难", "Doing household", "db016", "adl4"),
    (10, "fi10_taking_medicine", "自己吃药有困难", "Taking medicine", "db020", "adl4"),
    (11, "fi11_managing_money", "管钱有困难", "Managing money", "db019", "adl4"),
    (13, "fi13_lift_5kg", "提起 5 公斤重物有困难", "Lift a weight of 5 kg", "db008", "adl4"),
    (14, "fi14_walk_1km", "走 1 公里有困难", "Walking 1 km", "db002", "adl4"),
    (15, "fi15_stoop_kneel_crouch", "弯腰、屈膝或下蹲有困难", "Stooping, kneeling, or crouching", "db006", "adl4"),
    (16, "fi16_stand_from_chair", "坐久后从椅子上站起来有困难", "Able to stand up from sitting", "db004", "adl4"),
    (17, "fi17_pick_up_coin", "从桌上拿起一枚硬币有困难", "Able to pick up a coin from a table", "db009", "adl4"),
    (18, "fi18_jog_1km", "跑或慢跑 1 公里有困难", "Running or jogging about 1 km", "db001", "adl4"),
    (19, "fi19_reach_arms", "手臂向上伸展有困难", "Reaching or extend arms", "db007", "adl4"),
    (20, "fi20_climb_stairs", "不休息连续爬几层楼有困难", "Climbing several flights of stairs without resting", "db005", "adl4"),
    (21, "fi21_chronic_lung_disease", "慢性肺病（慢性支气管炎、肺气肿）", "Chronic lung diseases", "da007_5", "yesno"),
    (22, "fi22_asthma", "哮喘", "Asthma", "da007_14", "yesno"),
    (23, "fi23_cancer", "癌症", "Cancer", "da007_4", "yesno"),
    (24, "fi24_arthritis", "关节炎或风湿病", "Arthritis or Rheumatism", "da007_13", "yesno"),
    (25, "fi25_peptic_ulcer", "胃或十二指肠溃疡", "Gastric or duodenal ulcer", "da007_10", "yesno"),
    (26, "fi26_kidney_disease", "肾脏疾病", "Kidney disease", "da007_9", "yesno"),
    (27, "fi27_hypertension", "高血压", "Hypertension", "da007_1", "yesno"),
    (28, "fi28_dyslipidemia", "血脂异常", "Dyslipidemia", "da007_2", "yesno"),
    (29, "fi29_diabetes", "糖尿病或血糖升高", "Diabetes", "da007_3", "yesno"),
    (30, "fi30_heart_disease", "心脏病", "Heart Disease", "da007_7", "yesno"),
    (31, "fi31_psychiatric_problem", "情感、神经或精神方面问题", "Emotional, nervous, or psychiatric problems", "da007_11", "yesno"),
    (32, "fi32_stroke", "中风", "Stroke", "da007_8", "yesno"),
    (33, "fi33_liver_disease", "肝脏疾病", "Liver disease", "da007_6", "yesno"),
    (34, "fi34_memory_disease", "记忆相关疾病", "Memory related disease", "da007_12", "yesno"),
    (35, "fi35_felt_depressed", "过去一周感到情绪低落", "Feeling depressed", "dc011", "cesd_neg"),
    (36, "fi36_felt_fearful", "过去一周感到害怕", "Feeling fearful", "dc014", "cesd_neg"),
    (37, "fi37_could_not_get_going", "过去一周觉得无法继续生活", "Feeling unable to continue living", "dc018", "cesd_neg"),
    (38, "fi38_felt_happy", "过去一周感到愉快", "Feeling happy", "dc016", "cesd_pos"),
    (39, "fi39_felt_hopeful", "过去一周对未来充满希望", "Feeling hopeful about the future", "", "cesd_pos"),
    (40, "fi40_poor_sleep", "过去一周睡不好", "Poor sleep quality", "dc015", "cesd_neg"),
    (41, "fi41_felt_lonely", "过去一周感到孤独", "Feeling lonely", "", "cesd_neg"),
    (42, "fi42_everything_effort", "过去一周觉得做什么都很费劲", "Feeling that doing things is very effortful", "dc012", "cesd_neg"),
    (43, "fi43_self_rated_health", "自评健康", "Self-rated health", "da002", "srh5"),
    (44, "fi44_life_satisfaction", "生活满意度", "Life satisfaction", "dc028", "ls5"),
)
FI_BMI_ITEM = 12
# Table 2, items 45-48 ("Experimental data"), cut-offs as printed.
HBA1C_CUT_PCT = 5.7            # 0%-5.7% = 0, > 5.7% = 1
HB_NORMAL_G_DL = {"male": (13.5, 18.0), "female": (12.0, 16.0)}   # M: 13.5-18 = 0, F: 12-16 = 0, other = 1
CRP_CUT_MG_L = 3.0             # > 3.0 mg/L = 1
CREATININE_CUT_MG_DL = 1.0     # > 1.0 mg/dL = 1 (row label "Creatinine", variable code "cystatinc")

# Table 4 (FP score) and Table 5 (FI score), Model 3, meeting >= 150 min/week vs not: (beta, low, high).
TABLE4_FP_GUIDELINE = {
    "total": (-1.169, -1.252, -1.086), "hpa": (-0.400, -0.489, -0.310),
    "mpa": (-0.474, -0.550, -0.398), "lpa": (-0.659, -0.747, -0.571),
}
TABLE5_FI_GUIDELINE = {
    "total": (-0.030, -0.039, -0.021), "hpa": (-0.016, -0.024, -0.007),
    "mpa": (-0.015, -0.023, -0.008), "lpa": (-0.024, -0.033, -0.016),
}

# Figure 6 (FP score) and Figure 7 (FI score): beta (95% CI) and p by category, reference 0 min/week.
# Index 0 (0 min/week) is the reference and is None.
FIG6_FP_BETA = {
    "total": (None, (-0.11, -0.31, 0.09, "0.265"), (-0.27, -0.4, -0.14, "<0.001"), (-0.77, -0.86, -0.67, "<0.001")),
    "hpa": (None, (-0.41, -0.62, -0.2, "<0.001"), (-0.57, -0.73, -0.41, "<0.001"), (-0.49, -0.57, -0.41, "<0.001")),
    "mpa": (None, (-0.35, -0.61, -0.09, "0.009"), (-0.46, -0.71, -0.21, "<0.001"), (-0.41, -0.5, -0.31, "<0.001")),
    "lpa": (None, (-0.08, -0.23, 0.06, "0.255"), (-1.17, -1.3, -1.04, "<0.001"), (-1.21, -1.32, -1.11, "<0.001")),
}
FIG7_FI_BETA = {
    "total": (None, (0.0, -0.02, 0.02, "0.721"), (-0.02, -0.03, -0.01, "0.002"), (-0.03, -0.04, -0.02, "<0.001")),
    "hpa": (None, (-0.01, -0.03, 0.01, "0.204"), (-0.01, -0.03, 0.0, "0.067"), (-0.02, -0.02, -0.01, "<0.001")),
    "mpa": (None, (-0.02, -0.04, 0.01, "0.198"), (-0.04, -0.07, -0.02, "<0.001"), (-0.01, -0.02, 0.0, "0.006")),
    "lpa": (None, (-0.01, -0.03, 0.0, "0.133"), (-0.03, -0.04, -0.01, "<0.001"), (-0.04, -0.05, -0.03, "<0.001")),
}

# Supplementary Table 1 (FP analyses, Figure 8) and Supplementary Table 2 (FI analyses, Figure 9):
# adjusted Cox HR (low, high, p) for 10-year all-cause mortality by PA category vs 0 min/week.
# Panels B-E: all participants; panels F-I: frail participants (figure captions: "FP score > 1").
SUPP1_FP_HR_ALL = {
    "total": (None, (0.958, 0.730, 1.257, "0.759"), (0.875, 0.636, 1.202, "0.410"), (0.732, 0.568, 0.944, "0.016")),
    "hpa": (None, (0.988, 0.626, 1.561, "0.962"), (1.081, 0.698, 1.674, "0.725"), (0.771, 0.643, 0.923, "0.005")),
    "mpa": (None, (1.029, 0.714, 1.481, "0.877"), (1.004, 0.761, 1.324, "0.975"), (0.734, 0.629, 0.857, "<0.001")),
    "lpa": (None, (0.956, 0.677, 1.34, "0.800"), (0.967, 0.772, 1.212, "0.776"), (0.879, 0.735, 1.053, "0.164")),
}
SUPP1_FP_HR_FRAIL = {
    "total": (None, (0.958, 0.730, 1.257, "0.759"), (0.875, 0.636, 1.202, "0.410"), (0.732, 0.568, 0.944, "0.016")),
    "hpa": (None, (0.980, 0.505, 1.902, "0.954"), (1.382, 0.682, 2.797, "0.368"), (0.592, 0.425, 0.826, "0.002")),
    "mpa": (None, (0.755, 0.402, 1.419, "0.384"), (0.837, 0.519, 1.349, "0.466"), (0.715, 0.565, 0.905, "0.005")),
    "lpa": (None, (1.041, 0.706, 1.531, "0.836"), (1.000, 0.761, 1.312, "0.996"), (0.857, 0.679, 1.082, "0.196")),
}
SUPP2_FI_HR_ALL = {
    "total": (None, (1.135, 0.836, 1.542, "0.415"), (0.875, 0.651, 1.176, "0.378"), (0.758, 0.589, 0.975, "0.031")),
    "hpa": (None, (0.887, 0.440, 1.788, "0.739"), (0.721, 0.384, 1.353, "0.310"), (0.597, 0.448, 0.797, "<0.001")),
    "mpa": (None, (1.131, 0.709, 1.803, "0.605"), (0.691, 0.469, 1.019, "0.515"), (0.693, 0.568, 0.845, "<0.001")),
    "lpa": (None, (1.068, 0.706, 1.615, "0.754"), (0.984, 0.736, 1.314, "0.913"), (0.967, 0.774, 1.210, "0.775")),
}
SUPP2_FI_HR_FRAIL = {
    "total": (None, (1.128, 0.816, 1.559, "0.465"), (0.918, 0.673, 1.252, "0.590"), (0.779, 0.597, 1.016, "0.066")),
    "hpa": (None, (0.887, 0.440, 1.788, "0.739"), (0.721, 0.384, 1.353, "0.310"), (0.597, 0.448, 0.797, "<0.001")),
    "mpa": (None, (0.969, 0.564, 1.664, "0.910"), (0.689, 0.456, 1.039, "0.076"), (0.705, 0.570, 0.871, "0.001")),
    "lpa": (None, (1.028, 0.654, 1.616, "0.902"), (0.982, 0.724, 1.333, "0.912"), (0.993, 0.785, 1.256, "0.956")),
}

COHORT = {
    "min_age": 60, "n_fp": 2231, "n_fi": 2330, "fp_deaths": 859, "fi_deaths": 903,
    "baseline_year": 2011, "last_wave": 2020,
}

BOUNDARY = ("这些数是中国 60 岁及以上老人（CHARLS 2011 基线）里的人群关联，大多来自横断面比较，论文明确说不能证明因果，"
            "也不是你个人的衰弱诊断或死亡概率；衰弱表型只算得出两项，其余三项需要论文没印出的队列切点。"
            "报告不建议开始或停止任何药物，运动安排请结合自身情况和医生意见。")
