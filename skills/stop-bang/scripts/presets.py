"""Chung et al., Anesthesiology 2008, p. 821, Appendices 1 and 2."""

STOP_KEYS = ("snoring_binary", "tiredness_binary", "observed_apnea_binary", "hypertension_binary")
HIGH_RISK_MIN = {"stop": 2, "stop_bang": 3}
MAX_SCORE = {"stop": 4, "stop_bang": 8}
BMI_THRESHOLD = 35
AGE_THRESHOLD = 50
NECK_THRESHOLD_CM = 40
# All three numeric comparisons are strictly greater than, not >=.
# The counts are the number of affirmative answers: no fitted weights.

# Technical input-error guards, not study sample extrema or clinical cutoffs.
MEASUREMENTS = {
    **{key: ("1", (0, 1)) for key in STOP_KEYS},
    "bmi_kg_m2": ("kg/m^2", (10, 100)),
    "neck_circumference_cm": ("cm", (15, 80)),
}
AGE_RANGE = (18, 120)  # lower bound is adult eligibility; upper is an input guard
SEX_CODES = {"male": 1, "男": 1, "female": 0, "女": 0}
CATEGORY_ZH = {"high": "高风险", "low": "低风险"}
COMPONENT_LABELS = {
    "snoring_score": "S：大声打鼾", "tiredness_score": "T：白天经常疲倦或困倦",
    "observed_apnea_score": "O：他人目击睡眠中停止呼吸",
    "hypertension_score": "P：有高血压或正在接受高血压治疗",
    "bmi_score": "B：BMI", "age_score": "A：年龄",
    "neck_score": "N：颈围", "male_score": "G：原问卷男性项",
}
BOUNDARY = (
    "STOP 与 STOP-Bang 是阻塞性睡眠呼吸暂停筛查工具，不能确诊或排除疾病，"
    "不能估计个人患病概率、严重程度或手术安全性；本研究验证对象是术前成人，"
    "其他人群的适用性需另行评估；不能据此开始、停止或调整药物。"
)
VALIDATION_NOTE = "仍在验证：已核对原文计分规则，但论文未印出可复算的个人输入与总分示例。"
