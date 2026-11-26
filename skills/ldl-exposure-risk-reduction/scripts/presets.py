"""Ference et al., European Heart Journal 2017, Table 2 footnote.

All model constants below are printed; none are fitted to the table cells.
Input bounds are conservative implementation limits, not clinical cutoffs.
"""

LOG_RR_AT_FIVE_YEARS = -0.249
LOG_RR_PER_ADDITIONAL_YEAR = -0.0152
REFERENCE_YEARS = 5
INPUT_UNITS = {"ldl_reduction_mmol_l": "mmol/L", "duration_years": "a"}
INPUT_RANGES = {"ldl_reduction_mmol_l": (0, 3.5), "duration_years": (5, 40)}

BOUNDARY = (
    "这是基于人群证据的相对风险情景估计，不是个人发病概率、寿命预测或治疗建议；"
    "长期外推不等于同等年限的随机试验证明。只有LDL-C下降与LDL颗粒数下降一致、"
    "且没有抵消获益的有害脱靶作用时，论文的推断才适用；不能据此开始、停用或调整药物。"
)
