"""Sterling et al., Hepatology 2006, doi:10.1002/hep.21178.

Formula and worked examples: Results, Development of a Novel Model to Predict
Fibrosis. Cutoff equality follows Tables 5A and 5B, not abstract shorthand.
"""
from math import sqrt

INPUT_UNITS = {
    "age": "a", "ast_u_l": "U/L", "alt_u_l": "U/L",
    "platelets_10e9_l": "10^9/L",
}
ADVANCED_CUTS = (1.45, 3.25)  # Table 5A: <= lower; >= upper.
MODERATE_ADVANCED_CUTS = (0.6, 1.0)  # Table 5B: <= lower; >= upper.
MIN_AGE_EXCLUSIVE = 18  # Patients: age greater than 18 years.
ENTRY_PLATELET_MIN = 70  # Patients: excluded below 70,000/mm^3 = 70 x 10^9/L.
OBSERVED_INDEX_RANGE = (0.2, 10)  # Results; observed range, not clamping limits.

BOUNDARY = (
    "本报告只按 Sterling 等（2006）的 FIB-4 公式计算指数并对照原研究切点；"
    "原研究对象为 HIV/HCV 共感染、ALT 升高且肝病代偿的成人，不能直接外推到一般体检人群。"
    "结果不是纤维化确诊、个人患病概率、生物年龄或寿命预测，不能据此自行决定是否需要肝活检，"
    "也不能据此开始或停止药物。"
)


def fib4(age_years, ast_u_l, platelets_10e9_l, alt_u_l):
    """Printed formula: age * AST / (platelet count * sqrt(ALT))."""
    return age_years * ast_u_l / (platelets_10e9_l * sqrt(alt_u_l))


def band(index, cutoffs):
    if index <= cutoffs[0]:
        return "low"
    if index >= cutoffs[1]:
        return "high"
    return "indeterminate"
