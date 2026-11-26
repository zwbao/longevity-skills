"""Shah et al. 2009: Table 1 formula, Table 5 strict cutoffs.

Input ranges are implementation guards, not paper-derived reference ranges.
"""
import math

LOW_CUTOFF = 1.30
HIGH_CUTOFF = 2.67
INPUTS = {
    "age_years": ("a", (18, 120)),
    "ast_u_l": ("U/L", (1, 20000)),
    "alt_u_l": ("U/L", (1, 20000)),
    "platelets_10e9_l": ("10^9/L", (1, 2000)),
}
LABELS = {"low": "低值档", "indeterminate": "不确定档", "high": "高值档"}
BOUNDARY = "本结果仅为成人非酒精性脂肪肝研究中的 FIB-4 指数及分档，不是个人患病概率、纤维化分期或 NASH 诊断，不能替代医生评估或据此决定是否肝活检，不能据此开始或停止用药。"
SCENARIO_NOTE = "情景仅显示公式变化，不是治疗目标或疗效预测；尤其 ALT 在分母，升高 ALT 会使指数下降，这不代表健康改善。本研究未验证指数变化能够反映纤维化变化。"


def fib4(values):
    """Table 1: (age [years] × AST [U/L]) / (platelets [10^9/L] × √ALT [U/L])."""
    return values["age_years"] * values["ast_u_l"] / (values["platelets_10e9_l"] * math.sqrt(values["alt_u_l"]))


def classify(score):
    if score < LOW_CUTOFF:
        return "low"
    if score > HIGH_CUTOFF:
        return "high"
    return "indeterminate"
