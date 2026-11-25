"""FRAIL, AAH operationalization: Morley et al., 2012, Methods and Appendix 1."""

FATIGUE_POSITIVE_CODES = (1, 2)
ILLNESS_THRESHOLD = 5
ILLNESS_MAX = 11
WEIGHT_LOSS_THRESHOLD_PCT = 5
PERCENT_FACTOR = 100
FRAIL_MIN_SCORE = 3
MAX_SCORE = 5
VALIDATION_AGE_YEARS = (49, 65)

# Questionnaire domains are printed; weight bounds are input-error guards,
# not clinical thresholds or eligibility criteria from the paper.
MEASUREMENTS = {
    "fatigue_response_code": ("score", (1, 5)),
    "resistance_difficulty_binary": ("1", (0, 1)),
    "ambulation_difficulty_binary": ("1", (0, 1)),
    "illnesses_count": ("1", (0, ILLNESS_MAX)),
    "weight_current_kg": ("kg", (15, 500)),
    "weight_year_ago_kg": ("kg", (15, 500)),
}
INTEGER_KEYS = tuple(key for key in MEASUREMENTS if not key.startswith("weight_"))
FATIGUE_LABELS = {1: "一直", 2: "大部分时间", 3: "有些时候", 4: "少部分时间", 5: "从不"}
ILLNESSES_ZH = (
    "高血压", "糖尿病", "癌症（不含轻微皮肤癌）", "慢性肺病", "心肌梗死",
    "充血性心力衰竭", "心绞痛", "哮喘", "关节炎", "卒中", "肾病",
)
CATEGORY_ZH = {"robust": "健壮", "prefrail": "衰弱前期", "frail": "衰弱"}
COMPONENT_LABELS = {
    "fatigue_score": "疲劳", "resistance_score": "上楼困难",
    "ambulation_score": "步行困难", "illnesses_score": "疾病种数",
    "weight_loss_score": "体重下降",
}
WEIGHT_RULE_NOTE = (
    "体重项按论文正文的“过去一年下降至少 5%”计分；附录写“大于 5%”，"
    "没有说明恰好 5% 时如何计分，本报告在该边界采用正文定义。"
)
BOUNDARY = (
    "FRAIL 是衰弱筛查问卷，不能单独确诊衰弱、预测个人死亡概率或预期寿命；"
    "本研究在美国社区中晚年非裔成年人中验证，其他人群的适用性需另行评估；"
    "不能据此开始、停止或调整药物。"
)
