"""EMFRA Reduced Model C; medRxiv 2026, DOI 10.64898/2026.11.11.26367642.

Signed weights transcribed from Supplementary R Quarto Script, section 5.3,
Table 64. Section 6 uses abs(weight) and factor-specific 2-X reversal, with
no centering, standardization or fitted intercept. Keep all nine cross-loadings.
"""

ITEM_UNIT = "score"
ITEM_RANGE = (0, 2)
MIN_AGE = 65  # Main text 2.1 eligibility.
MAX_INPUT_AGE = 120  # Input sanity check, not a paper-derived threshold.
OBSERVED_AGES = (65, 99)  # Main text 3.1; supplementary Table 1.

WEIGHTS = {
    "emfra_item1_score": (0.233, -0.011),
    "emfra_item2_score": (0.405, 0.034),
    "emfra_item5_score": (-0.054, 0.157),
    "emfra_item6_score": (0.172, -0.009),
    "emfra_item7_score": (0.179, 0.032),
    "emfra_item11_score": (0.024, 0.388),
    "emfra_item12_score": (0.009, 0.510),
    "emfra_item15_score": (0.038, -0.157),
    "emfra_item19_score": (0.234, -0.068),
}
ITEM_KEYS = tuple(WEIGHTS)
OUTPUT_KEYS = ("autonomy_score", "psychological_distress_score")
THEORETICAL_MAXIMA = (2.696, 2.732)  # Supplementary Table 65, not cutoffs.

TITLE = "EMFRA 自主性与心理困扰分数"
BOUNDARY = (
    "预印本，未经同行评审；仅按 EMFRA 九项原始条目分数计算两个独立因子，"
    "不计算总分，不作诊断、临床分档、个人变化判定或治疗建议，不据此开始或停止药物。"
)
