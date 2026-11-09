"""Cut points and adjusted hazard ratios printed in the Taiwan senior fitness cohort.

[P] Wu M-C, Hsu C-T, Hsu H-T, et al. Physical Fitness and All-Cause Mortality in
    Older Adults. JAMA Netw Open. 2026;9(8):e2628227.
    doi:10.1001/jamanetworkopen.2026.28227 (CC BY-NC-ND 4.0; only the cut points and
    hazard ratios needed to reproduce the published grouping are extracted).
[S1] Supplement 1 of [P] (jamanetwopen-e2628227-s001.pdf, PMC13458872):
    eMethods 4 (protocols), eTable 3 (sex-specific quintile ranges),
    eFigure 4 (AHRs, 3 supplementary tests), eFigure 5 (men), eFigure 6 (women).

Quintiles are sex specific; Q1 is the poorest performance and the reference group,
Q5 the best. For the 8-foot up-and-go test quintiles are reverse-ranked (shorter
time = higher quintile). Every hazard ratio is from a separate multivariable Cox model
with the test entered alone, so hazard ratios of different tests must not be
multiplied or combined.
"""

from __future__ import annotations

# Test order, keys, Chinese labels and direction ("higher" = more is better).
TESTS = (
    ("step_2min", "step_2min_count", "2 分钟原地抬膝踏步", "次", "higher"),
    ("arm_curl", "arm_curl_30s_count", "30 秒手臂弯举", "次", "higher"),
    ("chair_stand", "chair_stand_30s_count", "30 秒椅子坐立", "次", "higher"),
    ("back_scratch", "back_scratch_cm", "抓背", "cm", "higher"),
    ("sit_reach", "chair_sit_reach_cm", "椅子坐姿体前弯", "cm", "higher"),
    ("one_leg", "one_leg_stance_s", "睁眼单脚站立", "秒", "higher"),
    ("up_and_go", "up_and_go_8ft_s", "8 英尺起身绕行", "秒", "lower"),
)
DOMAIN_ZH = {
    "step_2min": "心肺耐力", "arm_curl": "上肢肌力", "chair_stand": "下肢肌力",
    "back_scratch": "上肢柔韧", "sit_reach": "下肢柔韧", "one_leg": "平衡", "up_and_go": "敏捷与动态平衡",
}

# [S1] eTable 3, "Range" columns, Q1..Q5, as printed (raw test values).
# Each entry is (low, high) of the values observed in that quintile.
QUINTILE_RANGES = {
    "male": {
        "step_2min": ((0, 69), (70, 86), (87, 97), (98, 108), (109, 190)),
        "arm_curl": ((0, 13), (14, 16), (17, 19), (20, 22), (23, 36)),
        "chair_stand": ((0, 11), (12, 13), (14, 16), (17, 19), (20, 33)),
        "back_scratch": ((-50.0, -25.0), (-24.5, -15.1), (-15.0, -7.1), (-7.0, 2.0), (2.2, 30.0)),
        "sit_reach": ((-30.0, -7.0), (-6.9, 0.0), (0.1, 3.9), (4.0, 10.6), (10.7, 32.3)),
        "one_leg": ((0.00, 4.10), (4.12, 9.50), (9.56, 20.90), (21.00, 29.82), (30.00, 30.00)),
        "up_and_go": ((8.81, 22.00), (7.20, 8.80), (6.20, 7.19), (5.30, 6.19), (3.70, 5.29)),
    },
    "female": {
        "step_2min": ((0, 65), (66, 83), (84, 95), (96, 106), (107, 190)),
        "arm_curl": ((0, 13), (14, 16), (17, 18), (19, 22), (23, 36)),
        "chair_stand": ((0, 10), (11, 13), (14, 15), (16, 18), (19, 33)),
        "back_scratch": ((-50.0, -14.1), (-14.0, -5.1), (-5.0, 1.0), (1.1, 4.1), (4.2, 30.0)),
        "sit_reach": ((-30.0, -0.1), (0.0, 2.9), (3.0, 8.0), (8.1, 15.0), (15.1, 32.3)),
        "one_leg": ((0.00, 3.60), (3.61, 7.51), (7.58, 15.10), (15.12, 29.98), (30.00, 30.00)),
        "up_and_go": ((9.01, 22.00), (7.51, 9.00), (6.51, 7.50), (5.71, 6.50), (3.70, 5.70)),
    },
}

# [S1] eTable 3, "No. (%)" columns: participants per quintile, Q1..Q5.
QUINTILE_N = {
    "male": {
        "step_2min": (976, 1063, 1010, 980, 1000),
        "arm_curl": (918, 1001, 1055, 956, 1099),
        "chair_stand": (1046, 818, 1189, 873, 1103),
        "back_scratch": (1009, 952, 1011, 1120, 937),
        "sit_reach": (1024, 1282, 674, 1044, 1005),
        "one_leg": (1013, 999, 995, 399, 1623),
        "up_and_go": (1000, 1014, 1006, 1006, 1003),
    },
    "female": {
        "step_2min": (1701, 1709, 1667, 1580, 1737),
        "arm_curl": (1729, 1793, 1293, 2053, 1526),
        "chair_stand": (1477, 1970, 1441, 1745, 1761),
        "back_scratch": (1639, 1669, 1737, 1670, 1679),
        "sit_reach": (1297, 1912, 1900, 1636, 1649),
        "one_leg": (1683, 1673, 1684, 1303, 2051),
        "up_and_go": (1621, 1708, 1706, 1661, 1698),
    },
}

# [S1] eTable 3, IQR rows: median [25th, 75th percentile] by sex.
MEDIAN_IQR = {
    "male": {
        "step_2min": (92.0, 75.0, 105.0), "arm_curl": (18.0, 15.0, 22.0), "chair_stand": (15.0, 12.0, 19.0),
        "back_scratch": (-11.0, -22.0, 1.0), "sit_reach": (1.0, -4.0, 8.5), "one_leg": (14.0, 5.1, 30.0),
        "up_and_go": (6.7, 5.5, 8.2),
    },
    "female": {
        "step_2min": (90.0, 71.0, 104.0), "arm_curl": (18.0, 14.0, 21.0), "chair_stand": (15.0, 12.0, 18.0),
        "back_scratch": (0.0, -12.0, 3.3), "sit_reach": (5.0, 0.0, 13.1), "one_leg": (10.4, 4.4, 29.0),
        "up_and_go": (7.0, 6.0, 8.5),
    },
}

REF = (1.0, None, None)

# Both sexes, adjusted for sex and the other covariates. Q1..Q5: (AHR, low, high).
# step_2min, chair_stand, one_leg, up_and_go: [P] Figure 3; arm_curl, back_scratch,
# sit_reach: [S1] eFigure 4.
AHR_ALL = {
    "step_2min": (REF, (0.77, 0.67, 0.88), (0.61, 0.53, 0.71), (0.59, 0.50, 0.70), (0.58, 0.49, 0.68)),
    "arm_curl": (REF, (0.81, 0.71, 0.93), (0.75, 0.65, 0.87), (0.73, 0.63, 0.85), (0.63, 0.53, 0.75)),
    "chair_stand": (REF, (0.77, 0.67, 0.87), (0.63, 0.54, 0.73), (0.61, 0.52, 0.72), (0.55, 0.46, 0.65)),
    "back_scratch": (REF, (0.87, 0.76, 1.00), (0.75, 0.65, 0.86), (0.72, 0.61, 0.84), (0.65, 0.55, 0.76)),
    "sit_reach": (REF, (0.98, 0.85, 1.12), (0.81, 0.69, 0.95), (0.84, 0.72, 0.98), (0.79, 0.67, 0.93)),
    "one_leg": (REF, (0.75, 0.66, 0.85), (0.70, 0.61, 0.81), (0.53, 0.43, 0.66), (0.50, 0.42, 0.59)),
    "up_and_go": (REF, (0.73, 0.64, 0.83), (0.57, 0.49, 0.67), (0.46, 0.38, 0.55), (0.41, 0.33, 0.51)),
}

# Sex-stratified models: [S1] eFigure 5 (men) and eFigure 6 (women).
AHR_SEX = {
    "male": {
        "step_2min": (REF, (0.74, 0.62, 0.89), (0.65, 0.53, 0.79), (0.57, 0.45, 0.71), (0.54, 0.43, 0.68)),
        "arm_curl": (REF, (0.81, 0.67, 0.97), (0.71, 0.59, 0.87), (0.64, 0.51, 0.80), (0.62, 0.49, 0.78)),
        "chair_stand": (REF, (0.89, 0.74, 1.08), (0.65, 0.53, 0.78), (0.67, 0.53, 0.84), (0.59, 0.47, 0.75)),
        "back_scratch": (REF, (0.83, 0.69, 1.01), (0.70, 0.57, 0.86), (0.69, 0.56, 0.85), (0.60, 0.47, 0.75)),
        "sit_reach": (REF, (0.98, 0.82, 1.18), (0.88, 0.70, 1.11), (0.89, 0.73, 1.10), (0.79, 0.63, 0.99)),
        "one_leg": (REF, (0.77, 0.64, 0.92), (0.67, 0.55, 0.82), (0.57, 0.41, 0.78), (0.48, 0.38, 0.60)),
        "up_and_go": (REF, (0.75, 0.63, 0.90), (0.62, 0.51, 0.76), (0.48, 0.38, 0.61), (0.42, 0.31, 0.55)),
    },
    "female": {
        "step_2min": (REF, (0.80, 0.66, 0.96), (0.57, 0.46, 0.71), (0.62, 0.50, 0.78), (0.61, 0.49, 0.78)),
        "arm_curl": (REF, (0.81, 0.67, 0.99), (0.79, 0.63, 0.99), (0.82, 0.67, 0.99), (0.64, 0.50, 0.81)),
        "chair_stand": (REF, (0.66, 0.55, 0.80), (0.61, 0.49, 0.76), (0.56, 0.45, 0.70), (0.50, 0.39, 0.64)),
        "back_scratch": (REF, (0.92, 0.75, 1.12), (0.80, 0.65, 0.98), (0.74, 0.59, 0.93), (0.70, 0.55, 0.89)),
        "sit_reach": (REF, (0.97, 0.79, 1.18), (0.76, 0.61, 0.95), (0.78, 0.62, 0.99), (0.78, 0.61, 0.99)),
        "one_leg": (REF, (0.73, 0.60, 0.88), (0.73, 0.60, 0.90), (0.52, 0.40, 0.67), (0.52, 0.41, 0.67)),
        "up_and_go": (REF, (0.70, 0.58, 0.84), (0.53, 0.42, 0.65), (0.43, 0.33, 0.56), (0.41, 0.31, 0.54)),
    },
}

# [S1] eFigures 5 and 6: deaths per quintile, "No. of death (%)". Used only by the
# tests to check that eTable 3's columns are read with the right sex (deaths / n).
DEATHS_SEX = {
    "male": {
        "step_2min": ((299, 30.6), (195, 18.3), (144, 14.3), (106, 10.8), (104, 10.4)),
        "arm_curl": ((266, 29.0), (197, 19.7), (164, 15.6), (117, 12.2), (104, 9.5)),
        "chair_stand": ((302, 28.9), (173, 21.2), (164, 13.8), (102, 11.7), (107, 9.7)),
        "back_scratch": ((246, 24.4), (189, 19.9), (154, 15.2), (151, 13.5), (108, 11.5)),
        "sit_reach": ((217, 21.2), (245, 19.1), (109, 16.2), (158, 15.1), (119, 11.8)),
        "one_leg": ((321, 31.7), (205, 20.5), (155, 15.6), (45, 11.3), (122, 7.5)),
        "up_and_go": ((330, 33.0), (211, 20.8), (144, 14.3), (95, 9.4), (68, 6.8)),
    },
    "female": {
        "step_2min": ((280, 16.5), (182, 10.7), (113, 6.8), (107, 6.8), (101, 5.8)),
        "arm_curl": ((245, 14.2), (169, 9.4), (112, 8.7), (168, 8.2), (89, 5.8)),
        "chair_stand": ((273, 18.5), (189, 9.6), (114, 7.9), (114, 6.5), (93, 5.3)),
        "back_scratch": ((230, 14.0), (175, 10.5), (152, 8.8), (118, 7.1), (108, 6.4)),
        "sit_reach": ((163, 12.6), (222, 11.6), (156, 8.2), (128, 7.8), (114, 6.9)),
        "one_leg": ((305, 18.1), (171, 10.2), (147, 8.7), (70, 5.4), (90, 4.4)),
        "up_and_go": ((331, 20.4), (186, 10.9), (120, 7.0), (81, 4.9), (65, 3.8)),
    },
}

# [S1] eMethods 4.6: two trials, each stopped at 30 seconds; the longer is recorded.
ONE_LEG_CEILING_S = 30.0

# [P] Results and Table.
COHORT = {
    "n": 13423,
    "n_male": 5029,
    "n_female": 8394,
    "deaths": 1631,
    "deaths_pct": 12.2,
    "followup_median_years": 7.0,
    "mean_age": 72.9,
    "age_range": (65, 90),
}

BOUNDARY = (
    "这是台湾 65 到 90 岁社区老人一次体适能测试与约 7 年全因死亡的人群关联：风险比是该五分位组相对同性别最低五分位组的平均差别，"
    "每项测试单独建模，不能相乘或相加，不是你个人的死亡概率，也不能说明提高成绩就会降低死亡风险；不是诊断。"
    "成绩明显偏低、近期跌倒或有心肺疾病时，请先找医生评估再开始新的锻炼。"
)
