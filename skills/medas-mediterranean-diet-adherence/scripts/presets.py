"""Schröder et al., J Nutr 2011;141:1140–1145, Table 2 and Dietary assessment.

All scoring constants below are printed there. Ranges are engineering input
guards, not paper-derived normal ranges or dietary recommendations.
Unit '1' denotes a questionnaire count over the period encoded in the key,
or a yes/no code. No mass, volume or different-period conversion is implicit.
"""

TITLE = "MEDAS 地中海饮食依从性"
BOUNDARY = "本报告只按该论文的问卷规则计算饮食依从性，不诊断疾病、不预测个人冠心病风险或寿命，不据此开始或停止药物。酒类得分仅用于忠实记录原量表，不建议为了得分开始或增加饮酒。"
AGE_RANGE = (55, 80)
TOTAL_RANGE = (0, 14)

# Table 2 footnotes and item definitions; descriptive conversions only.
OLIVE_OIL_GRAMS_PER_TABLESPOON = 13.5
CUP_ML = 100
VEGETABLE_SERVING_G = 200
VEGETABLE_SIDE_SERVING = 0.5
RED_MEAT_SERVING_G = (100, 150)
BUTTER_SERVING_G = 12
PULSES_SERVING_G = 150
FISH_SERVING_G = (100, 150)
SEAFOOD_SERVING_G = 200
SEAFOOD_PIECES = (4, 5)
NUTS_SERVING_G = 30


def item(label, aliases, op, cutoff, upper, display_unit, note):
    return {"label_zh": label, "aliases": aliases, "op": op, "cutoff": cutoff,
            "range": [0, upper], "unit": "1", "display_unit": display_unit,
            "note_zh": note}


ITEMS = {
    "olive_oil_main_yes": item("橄榄油是否为主要烹调用油", ["olive oil principal cooking fat", "MEDAS Q1"], "eq", 1, 1, "是=1，否=0", "只能填 0 或 1；询问主要烹调用油，不是是否偶尔使用。"),
    "olive_oil_tbsp_day": item("每日橄榄油汤匙数", ["olive oil tablespoons per day", "MEDAS Q2"], "ge", 4, 30, "汤匙/日", "含煎炸、沙拉、外食等全部橄榄油；论文 1 汤匙=13.5 g，不用家用勺容量推算。"),
    "vegetables_servings_day": item("每日蔬菜份数", ["vegetable servings per day", "MEDAS Q3"], "ge", 2, 30, "份/日", "1 完整份=200 g；配菜或装饰菜按半份计入摄入量，最终该题仍只得 0 或 1 分。"),
    "fruit_pieces_day": item("每日水果个数", ["fruit pieces per day", "MEDAS Q4"], "ge", 3, 30, "个/日", "原问题包含鲜榨果汁；论文未规定果汁每份毫升数，不能自动把毫升换算成果实个数。"),
    "red_meat_servings_day": item("每日红肉汉堡香肠份数", ["red meat hamburger sausage servings per day", "MEDAS Q5"], "lt", 1, 20, "份/日", "包括红肉、汉堡、香肠；完整份为 100–150 g，须按问卷报告份数，不能取区间中点转换。"),
    "butter_margarine_cream_servings_day": item("每日黄油人造黄油奶油份数", ["butter margarine cream servings per day", "MEDAS Q6"], "lt", 1, 40, "份/日", "三者合计；每份 12 g。按 Table 2 明确列举的食品计，不泛化成所有动物脂肪。"),
    "sweet_carbonated_drinks_cups_day": item("每日碳酸或含糖饮料杯数", ["carbonated sugar sweetened beverages per day", "MEDAS Q7"], "lt", 1, 100, "杯/日", "按 Table 2 的碳酸和/或含糖饮料问题记录；正文规定 1 杯=100 mL，不按常见大杯计。"),
    "wine_cups_week": item("每周葡萄酒杯数", ["wine cups per week", "MEDAS Q8"], "ge", 7, 140, "杯/周", "Table 2 写 wine；正文写 red wine。采用 Table 2 原题，1 杯=100 mL；不把啤酒或白酒折算成葡萄酒，不作为饮酒建议。"),
    "pulses_servings_week": item("每周豆类份数", ["pulses servings per week", "legumes servings per week", "MEDAS Q9"], "ge", 3, 50, "份/周", "每份 150 g；不自行将豆浆或其他豆制品折算成该问卷的豆类份数。"),
    "fish_seafood_servings_week": item("每周鱼或海鲜份数", ["fish seafood servings per week", "MEDAS Q10"], "ge", 3, 50, "份/周", "每份鱼 100–150 g；海鲜为 4–5 个或 200 g。混合记录先按原问卷确认份数，不猜统一克重。"),
    "commercial_pastry_times_week": item("每周商业糕点次数", ["commercial pastry times per week", "MEDAS Q11"], "lt", 2, 100, "次/周", "仅商业制作（非自制）的饼干、蛋糕等；本论文是每周少于 2 次，不套用其他版本阈值。"),
    "nuts_servings_week": item("每周坚果份数", ["nuts servings per week", "MEDAS Q12"], "ge", 3, 100, "份/周", "每份 30 g；本论文阈值为每周至少 3 份。"),
    "white_meat_preferred_yes": item("是否更偏好鸡火鸡兔肉", ["prefer chicken turkey rabbit", "MEDAS Q13"], "eq", 1, 1, "是=1，否=0", "相对于牛肉、猪肉、汉堡或香肠，是否更偏好鸡、火鸡或兔肉；只能填 0 或 1。"),
    "sofrito_times_week": item("每周橄榄油番茄蒜洋葱酱菜肴次数", ["sofrito times per week", "MEDAS Q14"], "ge", 2, 100, "次/周", "指配有以橄榄油炒制番茄、蒜、洋葱或韭葱酱汁的蔬菜、意面、米饭等；不是任意含番茄的菜肴。"),
}
