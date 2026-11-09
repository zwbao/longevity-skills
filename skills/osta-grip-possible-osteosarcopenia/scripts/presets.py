"""Formula, cut points and cohort numbers printed in the TARGET possible-osteosarcopenia study.

[P] Koh et al. Possible osteosarcopenia is associated with loss in intrinsic
    capacity and early cognitive deficits: a longitudinal study of older adults
    in Singapore. J Gerontol A Biol Sci Med Sci. 2026;81(11):glag211.
    doi:10.1093/gerona/glag211

Methods, "Possible osteoporosis": OSTA index = 0.2 x [body weight (kg) - age (years)];
high risk OSTA < -4, moderate -4 to -1, low > -1; moderate and high are possible
osteoporosis (threshold <= -1). The paper does not truncate or round the index.

Methods, "Possible sarcopenia" (AWGS 2019): handgrip strength < 18 kg (women),
< 28 kg (men); mean of two trials of the dominant hand, Smedley dynamometer,
nearest 0.5 kg. The 5-time chair stand was not administered.

Methods, "Possible osteosarcopenia": both possible osteoporosis and possible
sarcopenia.
"""

from __future__ import annotations

DOI = "10.1093/gerona/glag211"

# Methods, OSTA formula.
OSTA_FACTOR = 0.2
# Methods, OSTA risk groups: high < -4; moderate -4 to -1; low > -1.
OSTA_HIGH_BELOW = -4.0
OSTA_POSSIBLE_OSTEOPOROSIS_MAX = -1.0  # OSTA <= -1 -> possible osteoporosis
OSTA_LABELS = {"high": "高风险（OSTA < −4）", "moderate": "中风险（OSTA −4 到 −1）", "low": "低风险（OSTA > −1）"}

# Methods, AWGS 2019 low handgrip strength (kg): strictly below the cut point.
GRIP_CUT_KG = {"female": 18.0, "male": 28.0}

# Cohort facts (Methods, Results, Table 2, Table 3, Supplementary Tables 3 and 12).
# Not applied to one person.
COHORT = {
    "n": 2291,
    "min_age": 60,
    "mean_age": 74.6,
    "prevalence_pct": 50.3,
    "n_possible": 1153,
    "n_no": 1127,
    "n_dxa": 895,
}
# Table 3: possible osteosarcopenia vs none, IC score (0-5), adjusted.
IC_BETA = (-0.21, -0.29, -0.14)
# Supplementary Table 11 / Results: odds of intact cognitive capacity at baseline.
COGNITION_OR = (0.45, 0.34, 0.60)
# Table 2 / Results: loss in cognitive capacity at baseline.
COGNITIVE_LOSS_PCT = {"possible": 75.8, "no": 42.8}
# Results / Table 4: mini-MoCA (0-15) at 6 months.
MINIMOCA_INTERACTION = (-0.59, -1.16, -0.03)
MINIMOCA_JOINT = -1.74
# Supplementary Table 12: predicted mean mini-MoCA (95% CI) by baseline cognition and status.
TABLE_S12 = {
    ("loss", "no"): (11.64, 11.34, 11.94),
    ("loss", "possible"): (11.08, 10.79, 11.36),
    ("intact", "no"): (12.84, 12.65, 13.03),
    ("intact", "possible"): (12.82, 12.53, 13.10),
}
# Supplementary Table 3: possible osteosarcopenia vs DXA-based osteosarcopenia (515 participants).
SCREENING = {"sensitivity": 92.3, "specificity": 71.4, "ppv": 48.6, "npv": 96.9, "roc": 0.82, "n": 515}

BOUNDARY = (
    "这是筛查分类，不是诊断：OSTA 只用体重和年龄估计骨密度偏低的可能，握力只看肌肉力量，"
    "“可能骨肌减少症”在论文里约一半是 DXA 确认的骨肌减少症。论文里的认知关联是新加坡老人人群的平均差异，"
    "不是你的个人预测。不能据此开始或停止任何药物；要确认请找医生做骨密度（DXA）和肌少症评估。"
)
