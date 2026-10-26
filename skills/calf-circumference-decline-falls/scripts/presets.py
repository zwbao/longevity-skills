"""Cut points and odds ratios printed in the CLHLS calf-circumference change study.

[P] Zhang et al. Longitudinal Change in Calf Circumference and Incident Falls in
    Older Adults. JAMA Netw Open. 2026;9(10):e2640127.
    doi:10.1001/jamanetworkopen.2026.40127 (CC BY-NC-ND 4.0; only the cut points
    and odds ratios needed to reproduce the published grouping are extracted).

Methods, "CC Measurement": seated, feet flat, knees bent at about 90 degrees,
right leg, nearest 0.1 cm, measured in 2018 and 2021. Absolute change is
CC2021 - CC2018 (cm); relative change is (CC2021 - CC2018) / CC2018 x 100.
Categories: no decrease, decrease < 3 cm, 3 to < 5 cm, >= 5 cm; relative no
decrease, < 10 %, 10 % to < 20 %, >= 20 %. "No decrease" includes stable and
increased CC and is the reference group. Values outside 15-50 cm were treated as
outliers ("Participant Characteristics").
"""

from __future__ import annotations

# Methods "CC Measurement": absolute-decrease groups (cm) and relative-decrease groups (%).
ABS_CUTS_CM = (3.0, 5.0)
REL_CUTS_PCT = (10.0, 20.0)
# "Participant Characteristics": outlying CC defined as <15 cm or >50 cm.
CC_VALID_CM = (15.0, 50.0)

ABS_LABELS = ("没有减少", "减少不到 3 cm", "减少 3 cm 到不到 5 cm", "减少 5 cm 及以上")
REL_LABELS = ("没有减少", "减少不到 10%", "减少 10% 到不到 20%", "减少 20% 及以上")

# Table 2, model 4 (fully adjusted, inverse probability weighted): OR (95% CI) per absolute group.
# Index 0 is the reference group.
TABLE2_MODEL4 = (
    (1.0, None, None),
    (1.27, 1.04, 1.55),
    (1.32, 1.11, 1.58),
    (1.33, 1.10, 1.60),
)
# Table 3, model 4: OR (95% CI) per relative group.
TABLE3_MODEL4 = (
    (1.0, None, None),
    (1.10, 0.91, 1.32),
    (1.26, 1.05, 1.51),
    (1.48, 1.20, 1.84),
)
# Table 2 / Table 3, model 4, continuous: per 1-cm decrease and per 10% decrease.
PER_1CM = (1.03, 1.02, 1.05)
PER_10PCT = (1.10, 1.06, 1.15)

# Table 4 (fully adjusted, stratified): OR (95% CI) per group, keyed by stratum.
TABLE4_ABS = {
    "male": ((1.0, None, None), (1.08, 0.79, 1.49), (1.33, 1.01, 1.74), (1.31, 0.98, 1.76)),
    "female": ((1.0, None, None), (1.35, 1.07, 1.70), (1.35, 1.05, 1.74), (1.44, 1.11, 1.87)),
    "under80": ((1.0, None, None), (1.36, 1.04, 1.78), (1.33, 1.06, 1.66), (1.29, 1.00, 1.65)),
    "80plus": ((1.0, None, None), (1.25, 0.96, 1.65), (1.33, 1.04, 1.70), (1.35, 1.05, 1.75)),
}
TABLE4_REL = {
    "male": ((1.0, None, None), (1.02, 0.75, 1.38), (1.21, 0.93, 1.59), (1.36, 0.98, 1.91)),
    "female": ((1.0, None, None), (1.16, 0.91, 1.47), (1.30, 1.02, 1.67), (1.57, 1.18, 2.09)),
    "under80": ((1.0, None, None), (1.09, 0.86, 1.39), (1.17, 0.87, 1.57), (1.22, 0.95, 1.56)),
    "80plus": ((1.0, None, None), (1.08, 0.84, 1.39), (1.36, 1.06, 1.76), (1.64, 1.23, 2.18)),
}
STRATUM_ZH = {"male": "男性", "female": "女性", "under80": "不到 80 岁", "80plus": "80 岁及以上"}

# Results "Participant Characteristics" and abstract.
COHORT = {
    "n": 7068,
    "falls": 1671,
    "falls_pct": 23.64,
    "mean_age": 79.66,
    "followup_median_years": 3.07,
    "followup_iqr_years": (2.91, 3.17),
    "min_age": 60,
}

BOUNDARY = (
    "这是中国 60 岁及以上社区老人 3 年间小腿围变化与新发跌倒的人群关联，比值比是和小腿围没有减少的人相比，"
    "不是你个人的跌倒概率，也不能说明小腿围减少导致跌倒；不是诊断。"
    "小腿围明显变细或近期跌过倒，请找医生评估肌肉、平衡和用药。"
)
