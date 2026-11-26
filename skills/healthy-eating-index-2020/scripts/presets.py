"""Shams-White et al. 2023, Figure 3 and footnotes; no fitted constants.

Density inputs are dimensionless ratios to 1 cup equivalent / 1000 kcal,
1 ounce equivalent / 1000 kcal, or 1 gram sodium / 1000 kcal as specified.
Their numeric values equal the densities printed in Figure 3.
"""

TITLE = "HEI-2020 饮食质量评分"
BOUNDARY = "本评分只描述所提供饮食记录与《美国居民膳食指南2020—2025》的符合程度，不代表营养是否充足、疾病风险或寿命；单次记录不能代表长期习惯，不适用于2岁以下儿童，也不能据此开始或停止用药。"

# key, output prefix, Chinese label, original component name, zero, full, points,
# reference quantity (None for fatty acid ratio and energy percentages).
ROWS = (
    ("total_fruits_density_ratio", "total_fruits", "总水果", "Total Fruits", 0, 0.8, 5, "1 cup equiv. per 1,000 kcal"),
    ("whole_fruits_density_ratio", "whole_fruits", "完整水果", "Whole Fruits", 0, 0.4, 5, "1 cup equiv. per 1,000 kcal"),
    ("total_vegetables_density_ratio", "total_vegetables", "总蔬菜", "Total Vegetables", 0, 1.1, 5, "1 cup equiv. per 1,000 kcal"),
    ("greens_beans_density_ratio", "greens_beans", "深绿色蔬菜和豆类", "Greens and Beans", 0, 0.2, 5, "1 cup equiv. per 1,000 kcal"),
    ("whole_grains_density_ratio", "whole_grains", "全谷物", "Whole Grains", 0, 1.5, 10, "1 oz equiv. per 1,000 kcal"),
    ("dairy_density_ratio", "dairy", "乳制品", "Dairy", 0, 1.3, 10, "1 cup equiv. per 1,000 kcal"),
    ("total_protein_density_ratio", "total_protein", "总蛋白质食物", "Total Protein Foods", 0, 2.5, 5, "1 oz equiv. per 1,000 kcal"),
    ("seafood_plant_density_ratio", "seafood_plant", "海鲜和植物蛋白质食物", "Seafood and Plant Proteins", 0, 0.8, 5, "1 oz equiv. per 1,000 kcal"),
    ("fatty_acids_ratio", "fatty_acids", "不饱和与饱和脂肪酸比", "Fatty Acids", 1.2, 2.5, 10, None),
    ("refined_grains_density_ratio", "refined_grains", "精制谷物", "Refined Grains", 4.3, 1.8, 10, "1 oz equiv. per 1,000 kcal"),
    ("sodium_density_ratio", "sodium", "钠", "Sodium", 2.0, 1.1, 10, "1 gram per 1,000 kcal"),
    ("added_sugars_energy_pct", "added_sugars", "添加糖供能比例", "Added Sugars", 26, 6.5, 10, None),
    ("saturated_fats_energy_pct", "saturated_fats", "饱和脂肪供能比例", "Saturated Fats", 16, 8, 10, None),
)
COMPONENTS = {
    key: {"output": out, "label_zh": label, "name": name, "zero": zero,
          "full": full, "points": points, "reference": reference,
          "unit": "%" if key.endswith("_pct") else "1"}
    for key, out, label, name, zero, full, points, reference in ROWS
}

# Software plausibility bounds, NOT clinical cutoffs or estimates from the paper.
INPUT_RANGES = {k: [0, 100] if k.endswith("_pct") else [0, 50] for k in COMPONENTS}
AGE_RANGE = [2, 120]
