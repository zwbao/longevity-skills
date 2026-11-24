"""GBD 2021, Lancet 2024, appendix 1 Table S9 p 513; SBP methods pp 278–279."""
TMREL_MMHG = (105, 115)
SBP_KEY = "sbp_mmhg"
SBP_UNIT = "mmHg"
# Engineering input guard, not a clinical cutoff or a paper inclusion criterion.
SBP_RANGE = (40, 300)
BOUNDARY = ("这是个人收缩压与 GBD 2021 群体研究参照区间的算术比较，"
            "不是高血压诊断、个人患病概率或寿命预测；TMREL 不是降压治疗目标，"
            "低于区间不代表更健康，区间内也不代表没有风险，不能据此开始、停止或调整药物。")
