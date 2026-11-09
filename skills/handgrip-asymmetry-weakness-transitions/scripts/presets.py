"""Cut points and hazard ratios printed in the CHARLS two-wave handgrip study.

[P] Xu D, Lin B, Ran Z. Two-wave status patterns of handgrip strength asymmetry and
    low handgrip strength in relation to all-cause mortality in middle-aged and older
    Chinese adults. GeroScience (2026). doi:10.1007/s11357-026-02558-4
    Supplementary Material ESM1 (PDF, Supplementary Tables S1-S26):
    https://static-content.springer.com/esm/art%3A10.1007%2Fs11357-026-02558-4/MediaObjects/11357_2026_2558_MOESM1_ESM.pdf

Methods, "Assessment of muscle phenotypes and two-wave status patterns":
- HGS measured twice per hand (Yuejian WL-1000); the maximum of each hand is used.
- HGSA: ratio of non-dominant to dominant HGS < 0.90 or > 1.10.
- LHGS (AWGS 2025): < 34.0 kg men and < 20.0 kg women aged < 65 years;
  < 28.0 kg men and < 18.0 kg women aged >= 65 years; applied at each wave.
- Four two-wave patterns per phenotype; Wave 2 joint abnormality score = HGSA(W2) + LHGS(W2).
- AAI = |ratio - 1|; delta AAI = AAI(W2) - AAI(W1).
- RGS = maximum HGS / BMI; Loss RGS = RGS(W1) - RGS(W2).
"""

from __future__ import annotations

# Methods: HGSA ratio band (asymmetry when ratio < low or > high).
HGSA_RATIO_LOW = 0.90
HGSA_RATIO_HIGH = 1.10

# Methods: AWGS 2025 LHGS thresholds (kg): abnormal when max HGS < threshold.
LHGS_AGE_SPLIT = 65
LHGS_KG = {
    ("male", "under65"): 34.0,
    ("female", "under65"): 20.0,
    ("male", "65plus"): 28.0,
    ("female", "65plus"): 18.0,
}

# Pattern index: 0 normal at both waves, 1 newly abnormal at Wave 2,
# 2 normalized at Wave 2, 3 abnormal at both waves.
PATTERN_ZH = ("两次都正常", "第二次新出现异常", "第二次恢复正常", "两次都异常")

# Table 2 (text, Results) and Supplementary Table S14 "Unweighted HR (95% CI)":
# primary Cox models, adjusted for the primary covariate set; reference = normal at both waves.
HGSA_HR = (
    (1.0, None, None),
    (1.07, 0.86, 1.33),
    (0.97, 0.78, 1.22),
    (1.32, 1.07, 1.61),
)
LHGS_HR = (
    (1.0, None, None),
    (1.91, 1.54, 2.37),
    (1.54, 1.21, 1.97),
    (2.35, 1.88, 2.94),
)
# Wave 2 joint abnormality score: Score 0 reference, Score 1, Score 2.
JOINT_HR = (
    (1.0, None, None),
    (1.22, 1.02, 1.46),
    (2.30, 1.84, 2.87),
)

# Supplementary Table S12: same models fitted within mutually exclusive comorbidity-burden
# groups (0, 1, >= 2 of: cardiovascular disease, hypertension, dyslipidemia, diabetes,
# cancer, chronic lung disease).
COMORBID_ZH = {0: "0 种慢病", 1: "1 种慢病", 2: "2 种及以上慢病"}
S12_HGSA = {
    0: ((1.0, None, None), (0.83, 0.53, 1.30), (0.69, 0.41, 1.14), (0.88, 0.56, 1.39)),
    1: ((1.0, None, None), (1.16, 0.82, 1.64), (0.84, 0.58, 1.21), (1.17, 0.83, 1.65)),
    2: ((1.0, None, None), (1.15, 0.81, 1.63), (1.26, 0.90, 1.78), (1.62, 1.19, 2.23)),
}
S12_LHGS = {
    0: ((1.0, None, None), (2.01, 1.26, 3.23), (1.10, 0.62, 1.97), (1.80, 1.09, 2.99)),
    1: ((1.0, None, None), (1.88, 1.33, 2.67), (1.53, 1.02, 2.30), (2.76, 1.91, 3.98)),
    2: ((1.0, None, None), (1.71, 1.22, 2.39), (1.58, 1.11, 2.25), (2.00, 1.42, 2.80)),
}
S12_JOINT = {
    0: ((1.0, None, None), (0.90, 0.61, 1.33), (1.98, 1.21, 3.24)),
    1: ((1.0, None, None), (1.26, 0.94, 1.69), (2.52, 1.75, 3.62)),
    2: ((1.0, None, None), (1.26, 0.96, 1.66), (2.07, 1.47, 2.91)),
}

# Supplementary Table S11: continuous change metrics, linear HR per 1-unit increase,
# and the 10th / 50th / 90th percentile knot locations in the analytic sample.
DELTA_AAI_HR = (1.66, 1.14, 2.42)
DELTA_AAI_KNOTS = (-0.133949, 0.000734, 0.142560)
LOSS_RGS_HR = (2.39, 1.86, 3.08)
LOSS_RGS_KNOTS = (-0.398013, 0.049102, 0.476531)

# Supplementary Table S10: observed deaths by pattern (n deaths, N, %).
S10_HGSA = ((208, 3302, 6.3), (142, 1997, 7.1), (125, 1859, 6.7), (172, 1766, 9.7))
S10_LHGS = ((320, 6745, 4.7), (121, 866, 14.0), (86, 793, 10.8), (120, 520, 23.1))

# Abstract / Results.
COHORT = {
    "n": 8924,
    "deaths": 647,
    "followup_median_years": 5.38,
    "min_age": 45,
    "wave1": 2011,
    "wave2": 2013,
    "end": 2018,
}

BOUNDARY = (
    "这是中国 45 岁及以上人群（CHARLS 2011、2013 两次握力，随访到 2018 年）里握力状态与全因死亡的关联，"
    "风险比是和参照组相比的人群平均，不是你个人的死亡概率或预期寿命，也不能说明因果；不是肌少症诊断。"
    "握力明显下降或两手差别大，请找医生评估肌肉、神经和关节情况。"
)
