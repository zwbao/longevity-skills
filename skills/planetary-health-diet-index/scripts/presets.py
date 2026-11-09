"""Planetary Health Diet Index (PHDI) cutoffs and the Seniors-ENRICA frailty associations.

[P] Diez-Echave et al. Planetary health diet adherence and frailty in older adults:
    evidence from the Seniors-ENRICA cohorts. J Gerontol A Biol Sci Med Sci.
    2026;81(11):glag244. doi:10.1093/gerona/glag244

Scoring (Methods, "Planetary health diet index"): 15 food groups, each scored 0-10
(non-soy legumes and soy 0-5); "Cutoff points for minimum and maximum intake are
provided in Table S1. For intakes between these cutoffs, scores were calculated
proportionally. The total PHDI score ranged from 0 to 140."

Supplementary Table 1 ("Description of the Planetary Health Diet Index (PHDI)",
reproduced from Bui et al., Am J Clin Nutr 2024;120:80-91) prints, for every
component, the intake that scores 0 ("Min score (0)"), the intake that scores 10
("Max score (10)") and the "Weight in total score". Components 13-15 are printed
as percent of total energy intake (TEI), not grams.
"""

from __future__ import annotations

DOI = "10.1093/gerona/glag244"
BUI_DOI = "10.1016/j.ajcnut.2024.03.019"

BOUNDARY = (
    "这是按论文印出的切点算出的饮食评分，不是诊断，也不是对你个人衰弱风险的预测；"
    "比值比是西班牙社区老人队列里的人群关联，不能说明因果。"
    "不据此开始或停止任何药物、补充剂或治疗；有慢病或特殊饮食需要时，改饮食前请先问医生或营养师。"
)

POINTS_PER_COMPONENT = 10.0
PHDI_MAX = 140.0
PHDI_MIN = 0.0

# Supplementary Table 1, verbatim cutoffs. Each entry:
#   key: (No., label_zh, unit, intake scoring 0, intake scoring 10, weight)
# A row whose 0-point intake is larger than its 10-point intake scores higher for
# eating less. Whole grains' 10-point intake is sex-specific ("75 g/day for
# females / 90 g/day for males"); stored as None and resolved by WHOLE_GRAIN_MAX.
COMPONENTS = {
    "whole_grains_g_d": (1, "全谷物", "g/d", 0.0, None, 1.0),
    "tubers_g_d": (2, "薯类（土豆、木薯等）", "g/d", 200.0, 50.0, 1.0),
    "vegetables_g_d": (3, "蔬菜（不含土豆等淀粉类）", "g/d", 0.0, 300.0, 1.0),
    "fruit_g_d": (4, "完整水果", "g/d", 0.0, 200.0, 1.0),
    "dairy_g_d": (5, "奶类（奶、奶酪、酸奶）", "g/d", 1000.0, 250.0, 1.0),
    "red_meat_g_d": (6, "红肉和加工肉（牛、羊、猪）", "g/d", 100.0, 14.0, 1.0),
    "poultry_g_d": (7, "鸡肉和其他禽肉", "g/d", 100.0, 29.0, 1.0),
    "eggs_g_d": (8, "蛋", "g/d", 120.0, 13.0, 1.0),
    "fish_g_d": (9, "鱼和贝类", "g/d", 0.0, 28.0, 1.0),
    "nuts_g_d": (10, "坚果（花生、核桃、杏仁等）", "g/d", 0.0, 50.0, 1.0),
    "legumes_g_d": (11, "非大豆豆类（干豆、扁豆、豌豆）", "g/d", 0.0, 100.0, 0.5),
    "soy_g_d": (12, "大豆和豆制品", "g/d", 0.0, 50.0, 0.5),
    "unsat_oil_pct_energy": (13, "不饱和植物油（橄榄油、菜籽油等）", "%", 3.5, 21.0, 1.0),
    "sat_fat_pct_energy": (14, "饱和脂肪和反式脂肪（黄油、猪油、棕榈油、人造黄油等）", "%", 10.0, 0.0, 1.0),
    "added_sugar_pct_energy": (15, "添加糖和果汁里的糖", "%", 25.0, 5.0, 1.0),
}
WHOLE_GRAIN_MAX = {"female": 75.0, "male": 90.0}

# Table 1: PHDI (0-140 points), mean (SD) by tertile and overall. Tertile cut points
# are not printed anywhere in the paper or Supplementary Data.
COHORT_PHDI = {
    "Seniors-ENRICA-1": {"n": 2143, "tertile_means": (79.5, 90.8, 102.2), "tertile_sds": (5.7, 2.5, 6.0), "mean": 91.0, "sd": 10.4},
    "Seniors-ENRICA-2": {"n": 1602, "tertile_means": (83.5, 93.3, 103.5), "tertile_sds": (5.0, 2.3, 5.2), "mean": 93.7, "sd": 9.3},
}
POOLED_N = 3745

# Table 2, Model 3 (fully adjusted GEE): OR (95% CI) for frailty, tertile 3 and
# tertile 2 vs tertile 1, and per 20-point increase.
TABLE2_MODEL3 = {
    "Seniors-ENRICA-1": {"t2": (0.83, 0.59, 1.18), "t3": (0.62, 0.42, 0.92), "per20": (0.64, 0.47, 0.87)},
    "Seniors-ENRICA-2": {"t2": (0.74, 0.49, 1.14), "t3": (0.40, 0.24, 0.65), "per20": (0.56, 0.36, 0.85)},
    "pooled": {"t2": (0.79, 0.61, 1.03), "t3": (0.52, 0.38, 0.70), "per20": (0.62, 0.49, 0.79)},
}
# Results text (Figure 2): per 2-point increment in a component, pooled Model 3.
COMPONENT_PER2 = {"vegetables_g_d": (0.88, 0.81, 0.96), "fruit_g_d": (0.89, 0.81, 0.98)}
# Table 3, pooled Model 3: tertile 3 vs 1 for low physical activity.
LOW_ACTIVITY_T3 = (0.70, 0.56, 0.87)

# Study population (Methods): Seniors-ENRICA-1 aged 60+, Seniors-ENRICA-2 aged 65+.
MIN_COHORT_AGE = 60
