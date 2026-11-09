"""EDISEA constants. Lai et al., Nature Communications 17:11146 (2026).

Every number here is printed in the paper or its Source Data workbook:

- WEIGHTS: Source Data (41467_2026_77790_MOESM13_ESM.xlsx), sheet "Figure 2",
  block "Figure 2b", columns "Food groups" / "Weight". The authors' code
  (github.com/WilliamLai3/Diet_EpigeneticAging, construct/hrs-ediea.R, lines
  1200-1247) writes this column as Estimate = -beta_z / sd_fg, i.e. the weight
  per serving per 2000 kcal/day, and applies it as
  ediea_servday = as.matrix(foods[, sel_fg]) %*% beta_sel_servday (line 1259).
  The main text (Results, "Derivation of EDISEA") prints the same weights to
  three decimals, and Supplementary Data 2 column "Primary model" too.
- Q1_Q5_MEDIANS: Results, same paragraph: "comparing Q5 versus Q1 of EDISEA,
  median intake was higher for tea (0.87 vs 0.12 servings/day) ...".
- ENERGY_PLAUSIBLE_KCAL: Methods, Dietary assessment (HRS): "<500 or >3500
  kcal/day for women and <800 or >4200 kcal/day for men".
"""

from __future__ import annotations

DOI = "10.1038/s41467-026-77790-9"
FULL_TEXT_READ = True
REFERENCE_KCAL = 2000.0  # Results: "servings per 2000 kcal/day"

TITLE = "表观衰老饮食指数 EDISEA"

BOUNDARY = (
    "这是按论文公布的权重算出的饮食模式分数，不是生物年龄、不是死亡风险，也不是治疗或饮食处方。"
    "论文是观察性研究，分数高低与表观衰老、死亡的关联来自人群比较，不能当成这个人的预测。"
    "不能据此开始或停止任何药物；饮酒、饮食有疾病相关限制的，以医生意见为准。"
)

# (key, label_zh, paper food group, Source Data Fig. 2b weight per serving per 2000 kcal/day)
FOODS = (
    ("tea_serv_d", "茶", "Tea", 0.0031500237501964),
    ("whole_grains_serv_d", "全谷物", "Whole grains", 0.00247676500330298),
    ("fruits_serv_d", "水果（不含果汁）", "Fruits", 0.00222189151065779),
    ("fries_serv_d", "炸薯条和炸土豆", "Fries", -0.0212815714052865),
    ("liquor_serv_d", "烈酒", "Liquor", -0.0131522549478942),
    ("beer_serv_d", "啤酒", "Beer", -0.0112024072531731),
    ("processed_meat_serv_d", "加工肉", "Processed meat", -0.00844182535322732),
    ("ssb_serv_d", "含糖饮料", "Sugar-sweetened beverages", -0.00249335427347874),
    ("asb_serv_d", "人工甜味剂饮料", "Artificial sweetened beverages", -0.00215929126148077),
    ("margarine_serv_d", "人造黄油", "Margarine", -0.00205263713264228),
)

WEIGHTS = {key: weight for key, _label, _name, weight in FOODS}
LABELS = {key: label for key, label, _name, _weight in FOODS}

# Weights as printed in the main text (three decimals), same order as FOODS.
PRINTED_WEIGHTS_3DP = {
    "tea_serv_d": 0.003,
    "whole_grains_serv_d": 0.002,
    "fruits_serv_d": 0.002,
    "fries_serv_d": -0.021,
    "liquor_serv_d": -0.013,
    "beer_serv_d": -0.011,
    "processed_meat_serv_d": -0.008,
    "ssb_serv_d": -0.002,
    "asb_serv_d": -0.002,
    "margarine_serv_d": -0.002,
}

# Results: median intake in the derivation sample (HRS), EDISEA Q1 vs Q5, servings/day as printed.
Q1_Q5_MEDIANS = {
    "tea_serv_d": (0.12, 0.87),
    "whole_grains_serv_d": (0.84, 1.96),
    "fruits_serv_d": (0.90, 2.38),
    "fries_serv_d": (0.10, 0.03),
    "liquor_serv_d": (0.04, 0.00),
    "beer_serv_d": (0.24, 0.01),
    "processed_meat_serv_d": (0.50, 0.16),
    "ssb_serv_d": (0.36, 0.10),
    "asb_serv_d": (0.12, 0.03),
    "margarine_serv_d": (0.13, 0.05),
}

# Methods (HRS): energy intakes treated as implausible and excluded.
ENERGY_PLAUSIBLE_KCAL = {"female": (500.0, 3500.0), "male": (800.0, 4200.0)}
