"""Constants of the HANDLS Life's Simple 7 (LS7) score.

Source [P]: Georgescu MF, Beydoun MA, et al. Life's Simple 7, depressive
symptoms, cognitive performance, and their associations with all-cause
mortality among middle-aged urban adults. GeroScience 2026,
doi:10.1007/s11357-026-02549-5. Online Supplementary Materials ESM 1
(Supplementary Methods 2 sections 1.1, 1.3, 1.4, 1.5 and Table S1A).

Every cutoff below is copied from [P]; nothing is taken from another source.
Where Table S1A and the Supplementary Methods 2 text disagree, the choice and
the reason are written next to the constant and in references/contract.md.
"""

from __future__ import annotations

# Points per level (Supplementary Methods 2, 1.5; Table S1A header):
# "2 points for excellent, 1 point for intermediate, and 0 points for poor".
POINTS = {"ideal": 2, "intermediate": 1, "poor": 0}
LEVEL_ZH = {"ideal": "理想", "intermediate": "中等", "poor": "差"}

# Body mass index, kg/m^2 (Table S1A; Methods 1.1): ideal <25, intermediate
# 25-29.9 (">= 25 and < 30"), poor >= 30.
BMI_IDEAL_BELOW = 25.0
BMI_POOR_AT = 30.0

# Blood pressure, mmHg (Table S1A; Methods 1.5): ideal <120/<80 untreated;
# intermediate SBP 120-139 or DBP 80-89 or treated to ideal; poor SBP >= 140
# or DBP >= 90. Methods 1.1 writes "and"/"with" instead of "or"; Table S1A
# and section 1.5 write "or", which is what is implemented.
SBP_IDEAL_BELOW = 120.0
DBP_IDEAL_BELOW = 80.0
SBP_POOR_AT = 140.0
DBP_POOR_AT = 90.0

# Total cholesterol, mg/dL (Table S1A; Methods 1.1): ideal <200 untreated;
# intermediate 200-239 or treated to ideal; poor >= 240 mg/dL.
TC_IDEAL_BELOW = 200.0
TC_POOR_AT = 240.0

# Fasting glucose, mg/dL (Table S1A; Methods 1.1): ideal <100 untreated;
# intermediate 100-125 or treated to ideal; poor >= 126 mg/dL.
GLUCOSE_IDEAL_BELOW = 100.0
GLUCOSE_POOR_AT = 126.0

# Smoking (Table S1A): ideal "Never or former = >1 year"; intermediate
# "Former = <=1 year"; poor "Current". Methods 1.1 instead calls every former
# user intermediate; Table S1A is the table the main text cites for the
# component definitions, so it is implemented and the report names the other
# reading when the person quit more than a year ago.
SMOKING_LEVEL = {
    "never": "ideal",
    "quit_over_1y": "ideal",
    "quit_within_1y": "intermediate",
    "current": "poor",
}
SMOKING_ZH = {
    "never": "从不吸烟",
    "quit_over_1y": "已戒烟超过 1 年",
    "quit_within_1y": "戒烟不满 1 年",
    "current": "现在吸烟",
}

# Healthy diet score (Methods 1.3; Table S1A): one point per goal met, scaled
# to 2,000 kcal; ideal 4-5 points, intermediate 2-3, poor 0-1.
DIET_GOALS_ZH = [
    "蔬菜水果每天至少 4.5 杯",
    "鱼每周至少两份（每份 3.5 盎司）",
    "高纤维全谷物每天至少 3 盎司当量（或每 10 克碳水化合物至少 1.1 克纤维）",
    "钠每天少于 1500 毫克",
    "含糖饮料每周不超过 450 千卡",
]
DIET_IDEAL_AT = 4
DIET_INTERMEDIATE_AT = 2

# Physical activity, minutes per week (Methods 1.4; Table S1A): ideal ">150
# minutes per week at a moderate intensity, >75 minutes per week at vigorous
# intensity, or a combination" (Table S1A prints ">=150" and ">=75"; the
# table's ">=" is implemented); "no active scored 0, and any activity
# generated a score of 1". The paper does not print how a combination of
# moderate and vigorous minutes is weighed, so a mix in which neither part
# reaches its own threshold is scored 1 and flagged in the report.
PA_MODERATE_IDEAL_AT = 150.0
PA_VIGOROUS_IDEAL_AT = 75.0

# Total score bands (Methods 1.5): "Other studies have classified scores as
# either optimal (10-14), moderate (5-9), or poor (0-4)".
TOTAL_MAX = 14
TOTAL_BANDS = [(10, "较好（10–14 分）"), (5, "中等（5–9 分）"), (0, "较差（0–4 分）")]

COMPONENTS = ["smoking", "diet", "physical_activity", "bmi", "blood_pressure", "cholesterol", "glucose"]
COMPONENT_ZH = {
    "smoking": "吸烟",
    "diet": "健康饮食",
    "physical_activity": "身体活动",
    "bmi": "体重指数",
    "blood_pressure": "血压",
    "cholesterol": "总胆固醇",
    "glucose": "空腹血糖",
}

# Printed per-component mean scores (Table S4, "LS7 SUBSCORES", Mean ± SE) and
# the printed mean totals they add up to (Results, "Descriptives of analytic
# sample": "lower LS7 total score (7.38 vs. 7.78, P < 0.001)").
TABLE_S4_SUBSCORES = {
    "women": {"bmi": 0.62, "blood_pressure": 1.43, "cholesterol": 1.43, "smoking": 0.93, "diet": 0.42,
              "physical_activity": 1.00, "glucose": 1.55},
    "men": {"bmi": 0.90, "blood_pressure": 1.50, "cholesterol": 1.64, "smoking": 0.81, "diet": 0.38,
            "physical_activity": 1.08, "glucose": 1.47},
}
PRINTED_MEAN_TOTAL = {"women": 7.38, "men": 7.78}

BOUNDARY = ("LS7 总分是心血管健康的七项打分，研究里它和死亡风险相关，不能算出你个人的死亡概率；"
            "它不是诊断，也不决定开始、停用或调整任何药物。")
