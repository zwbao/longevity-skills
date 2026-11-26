"""Frozen original seven-item Diabetes Risk Score, Table 1 and Results p. 727.

No later FINDRISC family-history extension or age >=65 category is included.
"""
TITLE = "芬兰糖尿病风险评分（原版七项）"
BOUNDARY = (
    "这是芬兰人群研究中的筛查评分，适用范围为35–64岁、评估时未接受降糖药治疗者；"
    "结局是随访期间开始药物治疗的糖尿病，不是全部新发糖尿病。"
    "分数不是个人患病概率，也不能诊断或排除糖尿病；在中国人群中的准确性未由本论文验证。"
    "目标情景只表示评分规则下的变化，不代表干预效果，不能据此开始或停止任何药物。"
)
TARGET_NOTE = "只比较你提供的BMI、腰围、活动和饮食目标；不自动推荐目标，不把分数变化解释为风险降低。"
AGE_RANGE = (35, 64)
CUTOFF = 9
SCORE_RANGE = (0, 20)
AGE_CUTS = (45, 55)
BMI_CUTS = (25, 30)
WAIST_CUTS = {"male": (94, 102), "female": (80, 88)}
INPUT_UNITS = {
    "bmi_kg_m2": "kg/m^2", "waist_cm": "cm", "bp_medication_ever": "1",
    "high_glucose_history": "1", "low_activity": "1", "daily_produce": "1",
    "antidiabetic_treatment": "1", "age": "a", "sex": "",
}
BINARY_KEYS = ("bp_medication_ever", "high_glucose_history", "low_activity",
               "daily_produce", "antidiabetic_treatment")
MODIFIABLE = ("bmi_kg_m2", "waist_cm", "low_activity", "daily_produce")
POINTS = {
    "age": (0, 2, 3), "bmi_kg_m2": (0, 1, 3), "waist_cm": (0, 3, 4),
    "bp_medication_ever": (0, 2), "high_glucose_history": (0, 5),
    "low_activity": (0, 2), "daily_produce": (1, 0),
}
OUTPUT_KEYS = {
    "age": "age_score", "bmi_kg_m2": "bmi_score", "waist_cm": "waist_score",
    "bp_medication_ever": "bp_medication_score", "high_glucose_history": "high_glucose_score",
    "low_activity": "activity_score", "daily_produce": "produce_score",
}
CATEGORY_LABELS = {
    "age": ("35–44岁", "45–54岁", "55–64岁"),
    "bmi_kg_m2": ("≤25 kg/m²", ">25至≤30 kg/m²", ">30 kg/m²"),
    "bp_medication_ever": ("从未使用降压药", "曾经使用降压药"),
    "high_glucose_history": ("无医务人员告知的血糖升高史", "有医务人员告知的血糖升高史"),
    "low_activity": ("不属于原文低活动类别", "属于原文低活动类别"),
    "daily_produce": ("并非每天吃蔬菜、水果或浆果", "每天吃蔬菜、水果或浆果"),
}
# Descriptive cohort figures only, never converted into a personal probability.
COHORTS = {
    "1987": {"eligible": 4746, "events": 196, "concise_n": 4595, "concise_events": 194,
             "full_n": 4435, "full_events": 182, "followup_years": 10,
             "ogtt_n": 2525, "ogtt_diabetes": 87},
    "1992": {"eligible": 4615, "events": 67, "full_n": 4586,
             "followup_years": 5, "ogtt_n": 1976, "ogtt_diabetes": 112},
}
