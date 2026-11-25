"""Constants for the modifiable risk factor score (Chen et al., J Gerontol A Biol Sci Med Sci 2026;81(10):glag196).

Every number here is printed in the paper or its supplementary appendix
(glag196_supplementary_data.docx). Locators are given next to each block.
"""

from __future__ import annotations

BOUNDARY = (
    "这是中国三个队列里人群层面的关联（风险比），是模型估计，不是诊断，也不是这个人一定会发生的事；"
    "它不决定是否用药，不能据此开始或停用任何药物。"
)

# --- Method S1 (harmonized binary definitions, last column "Category") -------------------------
# Education: 0 = completed middle / junior middle / old-style private school or more; 1 = less.
# Depression: CIDI-SF "yes" to any question, or GDS-15 score >= 6.
GDS15_DEPRESSION_MIN = 6
# Smoking: 0 = never smoker; 1 = occasional / ex regular / ex-occasional / ex-daily / current smoker.
# Alcohol: 0 = never drinker / never regular drinker; 1 = everything else.
# Physical activity: 1 = total PA score < 10 MET-h/week.
PA_MET_H_WEEK_MIN = 10.0
# Diet (CKB, CHCCS): 10-item healthy diet score; 1 = score <= 6.
DIET_SCORE_RISK_MAX = 6
DIET_ITEMS_ZH = (
    "米饭及米制品每周多于 3 份",
    "面食（中式小麦制品）每周多于 3 份",
    "红肉每周不超过 3 份",
    "禽肉及其制品每周不超过 6 份",
    "鱼和其他海产每周至少 1 份",
    "鸡蛋每周 3–6 份",
    "绿叶蔬菜每周至少 7 份",
    "豆类和豆制品每周多于 3 份",
    "新鲜水果每周至少 7 份",
    "奶和奶制品每周不超过 6 份",
)
# Sleep: 0 = 6 to 8 hours per day; 1 = < 6 or > 8 hours.
SLEEP_LOW_H = 6.0
SLEEP_HIGH_H = 8.0
# BMI: 0 = 18.5~28; 1 = BMI < 18.5 OR > 28 (Method S1 table and footnote).
# The harmonization paragraph instead writes healthy as 18.5 to <28 and obesity as >= 28;
# the script follows the table and flags a BMI of exactly 28 in the report.
BMI_LOW = 18.5
BMI_HIGH = 28.0
# Diabetes: diagnosis, or glucose-lowering medication, or fasting glucose >= 7 (CHCCS, GBCS)
# or random glucose >= 11.1 mmol/L (CKB).
FASTING_GLUCOSE_MMOL = 7.0
RANDOM_GLUCOSE_MMOL = 11.1
# Hypertension: diagnosis, or antihypertensive medication, or SBP >= 140 or DBP >= 90 mmHg.
SBP_MMHG = 140.0
DBP_MMHG = 90.0
# Dyslipidemia (CHCCS, GBCS): diagnosis, or lipid-lowering medication, or LDL-C >= 4.14,
# HDL-C < 1.04, TG >= 2.26, or TC >= 6.22 mmol/L.
LDL_MMOL = 4.14
HDL_MMOL = 1.04
TG_MMOL = 2.26
TC_MMOL = 6.22

# The 11 factors, in the paper's order, with their cluster (Methods, "Assessment of modifiable risk factors").
FACTORS = (
    ("low_education", "受教育程度低于初中", "sep"),
    ("depression", "抑郁", "sep"),
    ("smoking", "吸烟（含偶尔吸、已戒）", "behavior"),
    ("alcohol", "饮酒（含偶尔饮、已戒）", "behavior"),
    ("physical_inactivity", "体力活动不足（<10 MET-小时/周）", "behavior"),
    ("unhealthy_diet", "饮食不健康（健康饮食得分 ≤6）", "behavior"),
    ("abnormal_sleep", "睡眠时长不在 6–8 小时", "behavior"),
    ("abnormal_bmi", "体质指数 <18.5 或 >28", "metabolic"),
    ("diabetes", "糖尿病", "metabolic"),
    ("hypertension", "高血压", "metabolic"),
    ("dyslipidemia", "血脂异常", "metabolic"),
)
CLUSTERS_ZH = {"sep": "社会经济与心理", "behavior": "行为", "metabolic": "代谢"}

# --- Age groups (Methods, Statistical analysis) ---------------------------------------------------
# (lower bound inclusive, key, label). Middle age 30-49, presenium 50-59, younger old 60-79,
# oldest-old 80-99, centenarian >= 100.
AGE_MIN = 30
AGE_GROUPS = (
    (30, "middle_age", "中年（30–49 岁）"),
    (50, "presenium", "老年前期（50–59 岁）"),
    (60, "younger_old", "低龄老人（60–79 岁）"),
    (80, "oldest_old", "高龄老人（80–99 岁）"),
    (100, "centenarian", "百岁老人（≥100 岁）"),
)

# --- Supplementary Table S11 (appendix title; the table of contents calls it S12) ----------------
# "Hazard ratio (95% CI) of all-cause mortality associated with each one-point increase in
# composite risk scores by age group using pooled dataset". Adjusted for age, sex, cohort and all
# other composite risk scores. (hr, low, high) per one-point increase.
TABLE_S11 = {
    "overall": {
        "modifiable": (1.275, 1.186, 1.370), "sep": (1.661, 1.601, 1.723),
        "behavior": (1.139, 1.114, 1.164), "metabolic": (1.410, 1.377, 1.444),
    },
    "middle_age": {
        "modifiable": (1.231, 1.102, 1.374), "sep": (1.718, 1.289, 2.288),
        "behavior": (1.058, 0.913, 1.224), "metabolic": (1.430, 1.138, 1.797),
    },
    "presenium": {
        "modifiable": (1.235, 1.185, 1.288), "sep": (1.347, 1.226, 1.480),
        "behavior": (1.060, 0.997, 1.127), "metabolic": (1.388, 1.302, 1.479),
    },
    "younger_old": {
        "modifiable": (1.236, 1.214, 1.259), "sep": (1.309, 1.252, 1.369),
        "behavior": (1.168, 1.138, 1.199), "metabolic": (1.293, 1.256, 1.330),
    },
    "oldest_old": {
        "modifiable": (1.106, 1.010, 1.211), "sep": (1.292, 0.987, 1.693),
        "behavior": (1.040, 0.917, 1.180), "metabolic": (1.147, 0.984, 1.336),
    },
    "centenarian": {
        "modifiable": (1.118, 1.069, 1.170), "sep": (1.238, 1.087, 1.410),
        "behavior": (1.107, 1.034, 1.185), "metabolic": (1.073, 0.987, 1.168),
    },
}
P_INTERACTION = {"modifiable": 0.065, "sep": 0.007, "behavior": 0.007, "metabolic": 0.004}
