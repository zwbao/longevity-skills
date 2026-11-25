"""Frozen printed constants: Tapias et al., medRxiv v1 (2026), S4 p.32.

No refitting, reverse engineering, or extra precision. Transformation from
Methods 2.1 p.5. Operational input ranges live in skill.json.
"""
INTERCEPT = -4.053
# key: (mean, SD, coefficient on standardized predictor)
MODEL = {
    "hba1c_ifcc": (38.74, 3.47, 1.469),
    "age": (67.71, 7.30, -0.147),
    "female": (0.57, 0.50, -0.067),
    "log_years_next": (1.56, 0.26, 0.507),
}
DCCT_OFFSET = 2.15
DCCT_FACTOR = 10.929
IFCC_MINIMUM = 15
IFCC_DIABETES = 48
DCCT_DIABETES = 6.5
TYPICAL_INTERVALS = (4, 7)
INPUT_UNITS = {"hba1c_pct": "%", "age": "a", "sex": "1",
               "years_next": "a", "eligible_baseline": "1"}
TITLE = "ELSA HbA1c Model A 研究模型报告"
BOUNDARY = ("预印本，未经同行评审；这是 ELSA 队列研究模型在指定访视间隔下的估计，"
            "不是诊断、个人真实发病概率或干预效果；不据此开始、停用或调整药物。")
TARGET_NOTE = ("目标值仅为用户指定的数学情景，并非干预效果，也不代表应达到的治疗目标；"
               "年龄、性别和随访间隔保持不变。")
