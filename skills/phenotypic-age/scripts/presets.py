"""Printed constants: Liu et al., 2019 correction, DOI 10.1371/journal.pmed.1002760.

Units: Levine et al., Aging 2018, Table 1 (reference 12 of Liu 2018).
Do not substitute the uncorrected 2018 equation or higher precision BioAge
package constants. All numerical model parameters live here.
"""
INTERCEPT = -19.907
COEFFICIENTS = {
    "albumin_g_l": -0.0336,
    "creatinine_umol_l": 0.0095,
    "glucose_mmol_l": 0.1953,
    "crp_mg_dl": 0.0954,
    "lymphocyte_pct": -0.0120,
    "mcv_fl": 0.0268,
    "rdw_pct": 0.3306,
    "alp_u_l": 0.00188,
    "wbc_10e9_l": 0.0554,
    "age": 0.0804,
}
UNITS = {
    "albumin_g_l": "g/L", "creatinine_umol_l": "umol/L",
    "glucose_mmol_l": "mmol/L", "crp_mg_dl": "mg/dL",
    "lymphocyte_pct": "%", "mcv_fl": "fL", "rdw_pct": "%",
    "alp_u_l": "U/L", "wbc_10e9_l": "10^9/L", "age": "a",
}
RISK_NUMERATOR = 1.51714
RISK_DENOMINATOR = 0.0076927
AGE_OFFSET = 141.50
AGE_LOG_FACTOR = 0.00553
AGE_SCALE = 0.09165

TITLE = "表型年龄报告"
BOUNDARY = "这是观察性人群模型的表型年龄估计，不能诊断疾病、预测个人寿命或证明干预能逆转衰老，不能据此开始或停止用药。"
TARGET_NOTE = "目标情景只改变指定输入并固定其余输入，是模型的数学变化，不是因果效应或治疗目标；不应为了降低年龄分数而追求化验极值。"
