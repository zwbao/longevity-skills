"""Cut points and printed cohort numbers of the RLAS cumulative-obesity study.

[P] Yu J, Zhang L, Yang Z, et al. The impact of cumulative obesity and genetic
    susceptibility on biological aging in Chinese older adults. GeroScience (2026).
    doi:10.1007/s11357-026-02437-y. Only the cut points, the formula and the
    printed cohort numbers needed for the readout are extracted.

Methods, "Measurement of obesity indicators": cBMI and cWC across the 2014, 2017
and 2019 waves are "the excessive exposure of BMI and WC relative to their
reference values, multiplied by their durations (in years)"; references BMI 24
kg/m2 (Working Group on Obesity in China), WC 90 cm for males and 80 cm for
females (IDF, Asian populations); "if BMI and WC were lower than their specific
references, the excessive exposures were set to zero". Baseline (2019 wave) BMI
groups: <18.5, 18.5 to <24, 24 to <28, >=28 kg/m2. Supplementary Table 12 repeats
the analysis with a WC cut point of 85 cm for females (Chinese criteria).

How the per-wave excess is combined with the durations is not printed; this skill
uses the area under the excess curve between consecutive waves (trapezoid), see
references/contract.md.
"""

from __future__ import annotations

# Methods: reference values.
BMI_REF = 24.0                      # kg/m2
WC_REF_CM = {"male": 90.0, "female": 80.0}
WC_REF_FEMALE_CHINESE_CM = 85.0     # Supplementary Table 12 sensitivity analysis

# Methods: baseline BMI groups (kg/m2).
BMI_UNDERWEIGHT_BELOW = 18.5
BMI_OBESITY_FROM = 28.0
BMI_LABELS = ("偏瘦（<18.5）", "正常（18.5 到 <24）", "超重（24 到 <28）", "肥胖（≥28）")

# Methods: wave years and the durations between them in the paper's design.
PAPER_WAVES = (2014, 2017, 2019)

# Results "Baseline characteristics": median (IQR) of the cumulative exposures.
COHORT = {
    "n": 687,
    "mean_age": 79.6,
    "sd_age": 3.5,
    "female_n": 370,
    "female_pct": 53.9,
    "cbmi_median": 1.3,
    "cbmi_iqr": (0.0, 11.0),
    "cwc_median": 20.5,
    "cwc_iqr": (0.5, 50.5),
}

# Supplementary Table 2 (Model 1, n = 687): beta (95% CI) versus the zero group, in
# KDM-BA years and PD units. Per-unit rows are per 1 kg/m2 x year and 1 cm x year.
TABLE_S2 = {
    "cbmi": {
        "kdm_ba": {"T1": (0.52, 0.11, 0.93), "T2": (0.90, 0.48, 1.31), "T3": (1.22, 0.80, 1.63),
                   "per_unit": (0.034, 0.021, 0.048)},
        "pd": {"T1": (-0.03, -0.16, 0.11), "T2": (0.05, -0.08, 0.19), "T3": (0.18, 0.05, 0.31),
               "per_unit": (0.007, 0.002, 0.011)},
    },
    "cwc": {
        "kdm_ba": {"T1": (0.65, 0.23, 1.08), "T2": (0.81, 0.37, 1.24), "T3": (1.65, 1.19, 2.12),
                   "per_unit": (0.015, 0.01, 0.02)},
        "pd": {"T1": (-0.05, -0.19, 0.09), "T2": (-0.06, -0.20, 0.08), "T3": (0.17, 0.02, 0.32),
               "per_unit": (0.002, 0.001, 0.004)},
    },
}

# Supplementary Table 4 (Model 1): KDM-BA beta (95% CI) for baseline BMI groups vs normal weight.
TABLE_S4_BMI_KDM = {0: (-0.51, -1.25, 0.22), 1: None, 2: (0.78, 0.45, 1.11), 3: (1.02, 0.52, 1.53)}

BOUNDARY = (
    "累积肥胖暴露是按论文公式算的过去几年 BMI、腰围超出切点的“量×年”，不是生物年龄，也不是诊断；"
    "论文里它与两种血液指标生物年龄（KDM-BA、PD）的关联来自 687 名如皋 70 岁以上老人的观察研究，"
    "不能说明因果，也不能换算成你个人老了几岁。体重和腰围管理请和医生一起定。"
)
