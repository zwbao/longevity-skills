"""Cut-offs and hazard ratios printed in the MHAS handgrip strength and mortality study.

[P] Pérez-Sousa MÁ, Borda MG, Ramírez-Vélez R, Fernández-Aparicio Á, González-Jiménez E.
    Sex-specific associations between handgrip strength and all-cause mortality in
    older Mexican adults. GeroScience 2026. doi:10.1007/s11357-026-02639-4
[S3] Supplementary Material 2 (11357_2026_2639_MOESM2_ESM.pdf), Supplementary Table S3
    "Associations between consensus cut offs for low absolute handgrip strength and
    all cause mortality".

Methods "Assessment of muscle strength": digital handheld dynamometer, two trials for
each hand, the maximum value from the dominant hand (kg) is the predictor; allometric
HGS = HGS / height^2 (kg/m^2).
Methods "Statistical analysis": low absolute HGS defined by EWGSOP2 (< 27 kg in men and
< 16 kg in women) and FNIH (< 26 kg in men and < 16 kg in women), participants at or
above each cut-off as the reference group.
"""

from __future__ import annotations

# Methods "Statistical analysis" and [S3] row labels: low absolute HGS is strictly below the cut-off (kg).
CUTOFFS_KG = {
    "ewgsop2": {"male": 27.0, "female": 16.0},
    "fnih": {"male": 26.0, "female": 16.0},
}
CRITERION_ZH = {"ewgsop2": "EWGSOP2（欧洲肌少症工作组 2019）", "fnih": "FNIH（美国国立卫生研究院基金会肌少症项目 2014）"}

# [S3]: (n with low HGS, deaths among them, Model 1 HR, low, high, p, Model 2 HR, low, high, p).
# Model 1: adjusted for age. Model 2: additionally multimorbidity, smoking, alcohol, vigorous physical
# activity, living arrangement, rural residence and education. Unweighted, sex-stratified, complete-case.
# Women: "Both criteria used the same <16 kg cut-off in women and therefore yielded identical estimates."
S3 = {
    ("ewgsop2", "male"): {"n_low": 190, "deaths_low": 84, "model1": (2.112, 1.537, 2.901), "p1": "<0.001",
                          "model2": (2.302, 1.653, 3.206), "p2": "<0.001"},
    ("fnih", "male"): {"n_low": 155, "deaths_low": 72, "model1": (2.002, 1.449, 2.766), "p1": "<0.001",
                       "model2": (2.237, 1.596, 3.136), "p2": "<0.001"},
    ("ewgsop2", "female"): {"n_low": 157, "deaths_low": 49, "model1": (1.531, 1.093, 2.144), "p1": "0.013",
                            "model2": (1.268, 0.893, 1.799), "p2": "0.185"},
    ("fnih", "female"): {"n_low": 157, "deaths_low": 49, "model1": (1.531, 1.093, 2.144), "p1": "0.013",
                         "model2": (1.268, 0.893, 1.799), "p2": "0.185"},
}
# [S3] footnote: "The complete-case sample included 726 men (173 deaths) and 1,039 women (179 deaths)."
S3_SAMPLE = {"male": (726, 173), "female": (1039, 179)}

# Results "Mortality rates and distribution" and abstract.
COHORT = {
    "n": 1917,
    "men_pct": 41.7,
    "deaths": 371,
    "deaths_men": 184,
    "deaths_women": 187,
    "followup_median_months": 109,
    "min_age": 50,
    "baseline_year": 2012,
    "end_year": 2021,
}

# Results "Sex interaction" (Table 4) and abstract: per 1-SD (sex-specific z-score) hazard ratios.
# Shown as population context only; the SDs (Table 1) could not be opened, so no personal z-score is computed.
PER_SD = {
    ("absolute", "male"): (0.53, 0.44, 0.65),
    ("allometric", "male"): (0.60, 0.48, 0.75),
    ("allometric", "female"): (0.80, 0.68, 0.94),
}

LABELS = ("低于切点（握力偏低）", "达到或高于切点")

BOUNDARY = (
    "这些风险比来自墨西哥 50 岁及以上人群的观察研究，是握力低于切点的人和达到切点的人相比的死亡风险关联，"
    "不是你个人的死亡概率或预期寿命，也不能说明握力低导致死亡；不是肌少症诊断。"
    "握力明显偏低或近期下降，请找医生评估。"
)
