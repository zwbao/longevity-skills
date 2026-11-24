"""Fang & Schwartz, medRxiv 2026 v2, Table 2 / appendix p9 Table S3.

Rows: conditional quantiles; columns: imputations I1..I5. Units: years per
log2 whole-blood lead (ug/dL). None is printed NE, never zero or imputed.
"""
MEASUREMENTS = {"blood_lead_ug_dl": "ug/dL", "reference_lead_ug_dl": "ug/dL"}
BETAS = {
    10: (-0.671, -0.685, -0.679, -0.706, -0.625),
    25: (-0.555, -0.607, -0.587, -0.650, -0.612),
    50: (None, -0.613, -0.626, None, -0.620),
}
TITLE = "血铅与条件生存时间差"
BOUNDARY = (
    "预印本，未经同行评审；本结果仅为观察性模型在其他协变量保持相同时的条件生存时间差，"
    "不是你的预期寿命、死亡时间或死亡概率，也不是降低血铅可获得的寿命；"
    "不能据此开始或停止药物、补剂或排铅治疗。"
)
CAUTION = (
    "主要模型没有调整尿镉；镉调整后，血铅与较短生存时间的关联不再成立。"
    "本模型不能分离铅的独立因果作用。"
)
SCENARIO_NOTE = "目标仅为用户指定的数学情景，不是安全阈值或治疗目标；数值变化不代表干预获益。"
