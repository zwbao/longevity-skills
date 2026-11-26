"""Frozen constants from Kivipelto et al., Lancet Neurology 2006, pp. 736–738."""
TITLE = "CAIDE中年痴呆风险评分"
BOUNDARY = ("这是芬兰中年人队列的风险模型，适用背景是存活到约20年后复查的人群；"
            "不用于诊断痴呆，也不能保证个人未来是否患病。目标情景只是模型重算，"
            "不代表改变指标就能获得相同风险降幅；不能据此开始、停止或调整药物。")
TARGET_NOTE = "只代入你提供的目标，不推荐目标值；年龄、性别、既往教育和APOE不是本报告的可改变目标。"
INPUT_UNITS = {"education_years": "a", "sbp_mmhg": "mmHg", "bmi_kg_m2": "kg/m^2",
               "total_cholesterol_mmol_l": "mmol/L", "active": "1", "apoe_e4": "1",
               "age": "a", "sex": ""}
MODIFIABLE = {"sbp_mmhg", "bmi_kg_m2", "total_cholesterol_mmol_l", "active"}
# Table 2: explicit Score columns, not re-rounded beta coefficients.
CUTS = {"age": (47, 53), "education_years": (6, 9), "sbp_mmhg": 140,
        "bmi_kg_m2": 30, "total_cholesterol_mmol_l": 6.5}
POINTS = {
    1: {"age": (0, 3, 4), "education_years": (3, 2, 0), "sex": (0, 1),
        "sbp_mmhg": (0, 2), "bmi_kg_m2": (0, 2), "total_cholesterol_mmol_l": (0, 2),
        "active": (1, 0)},
    2: {"age": (0, 3, 5), "education_years": (4, 3, 0), "sex": (0, 1),
        "sbp_mmhg": (0, 2), "bmi_kg_m2": (0, 2), "total_cholesterol_mmol_l": (0, 1),
        "active": (1, 0), "apoe_e4": (0, 2)},
}
OUTPUT_KEYS = {"age": "age_score", "education_years": "education_score", "sex": "sex_score",
               "sbp_mmhg": "sbp_score", "bmi_kg_m2": "bmi_score",
               "total_cholesterol_mmol_l": "cholesterol_score", "active": "activity_score",
               "apoe_e4": "apoe_score"}
CATEGORY_LABELS = {"age": ("<47岁", "47–53岁", ">53岁"),
                   "education_years": ("0–6年", "7–9年", "≥10年"), "sex": ("女性", "男性"),
                   "sbp_mmhg": ("≤140 mmHg", ">140 mmHg"), "bmi_kg_m2": ("≤30 kg/m²", ">30 kg/m²"),
                   "total_cholesterol_mmol_l": ("≤6.5 mmol/L", ">6.5 mmol/L"),
                   "active": ("未达到原文活动定义", "达到原文活动定义"),
                   "apoe_e4": ("非ε4携带者", "ε4携带者")}
# Table 3: lower score, upper score, observed risk (%), lower/upper 95% CI (%).
# Preserve the printed negative CI lower bound in Model 2; it is not a probability.
RISK_TABLE = {
    1: [(0, 5, 1.0, 0.0, 2.0), (6, 7, 1.9, 0.2, 3.5), (8, 9, 4.2, 1.9, 6.4),
        (10, 11, 7.4, 4.1, 10.6), (12, 15, 16.4, 9.7, 23.1)],
    2: [(0, 5, 0.3, -0.3, 1.0), (6, 8, 1.7, 0.3, 3.0), (9, 10, 4.6, 2.0, 7.1),
        (11, 12, 4.4, 1.7, 7.1), (13, 18, 16.3, 10.7, 21.9)],
}
# Methods p. 736: score-based logistic model. beta1 already represents 20 years.
LOGISTIC = {1: (-7.406, 0.796, 0.401), 2: (-8.083, 1.020, 0.390)}
CUTOFF = {1: 9, 2: 10}  # Results p. 738, primary cutoffs.
