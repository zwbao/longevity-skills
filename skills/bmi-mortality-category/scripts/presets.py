"""Global BMI Mortality Collaboration, Lancet 2016, Table 2 (nine categories).

Rows: lower inclusive BMI, upper exclusive BMI, pooled HR, floating CI low/high.
No fitting, interpolation, or reconstruction of participant data.
"""
INPUT_UNITS = {"height_cm": "cm", "weight_kg": "kg"}
BMI_ROWS = (
    (15.0, 18.5, 1.51, 1.43, 1.59),
    (18.5, 20.0, 1.13, 1.09, 1.17),
    (20.0, 22.5, 1.00, 0.98, 1.02),
    (22.5, 25.0, 1.00, 0.99, 1.01),
    (25.0, 27.5, 1.07, 1.07, 1.08),
    (27.5, 30.0, 1.20, 1.18, 1.22),
    (30.0, 35.0, 1.45, 1.41, 1.48),
    (35.0, 40.0, 1.94, 1.87, 2.01),
    (40.0, 60.0, 2.76, 2.60, 2.92),
)
AGE_MIN = 20
AGE_MAX_EXCLUSIVE = 90  # Conservative intersection of Methods and appendix p51.
REFERENCE = "22.5–<25.0 kg/m²"
TITLE = "BMI 分档与全因死亡关联"
BOUNDARY = "本报告只按 BMI 查询论文特定人群的死亡危险比（HR），不是个人死亡概率、预期寿命或体重改变的因果效果；不能据此开始、停用或调整药物。"
SCENARIO_NOTE = "目标体重只改变所查的 BMI 档位和人群 HR，不是个人减重获益预测，也不是建议体重。档内 HR 不变来自离散查表，不能解释为体重变化没有影响；切点处 HR 导数未定义。"
