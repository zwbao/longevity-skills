"""Printed constants: Momma et al., BJSM 2022, Table 1 (PMC9209691 XML).

Only the linear dose-response column; no spline coefficients are reconstructed.
"""
INPUT_KEY = 'strength_minutes_per_week'
INPUT_UNIT = 'min'  # Total duration in a seven-day period, not minutes per session.
INPUT_RANGE = (0, 10080)  # Physical time budget: 7 * 24 * 60; NOT a validated model range.
INCREMENT_MIN = 10
OUTCOMES = {
    'all_cause_mortality': ('全因死亡', (0.99, 0.98, 1.00)),
    'cvd': ('心血管疾病（发病或死亡）', (0.996, 0.99, 1.003)),
    'total_cancer': ('总癌症（发病或死亡）', (0.99, 0.98, 1.004)),
    'diabetes': ('糖尿病发病', (0.98, 0.97, 0.99)),
}
BOUNDARY = '这是观察性队列荟萃分析的线性关联换算，不是个人患病或死亡概率、寿命预测或改变训练时长后的因果收益；不能据此开始或停止药物，也不提供用药剂量或训练处方。'
MODEL_NOTE = '全因死亡、心血管疾病和总癌症存在 J 形关联，糖尿病存在 L 形关联。这里的线性换算不刻画这些非线性变化，也不能确定最佳时长；尤其不能把更长时长下更低的线性 RR 理解为继续增加训练的获益。'
