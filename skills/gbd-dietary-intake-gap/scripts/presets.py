"""GBD 2017 Table, Lancet 2019;393:1960 (DOI 10.1016/S0140-6736(19)30041-8).

reference/reference_range are printed, not re-derived from mortality weights.
EPA+DHA: 250 (200–300) mg/day divided by exactly 1000 for g/day.
input_max is an engineering input guard, NOT a paper cutoff or health limit.
"""

_ROWS = [
    ("fruits_g_d", "fruits", "水果", "g/d", 250, (200, 300), "low", 5000,
     ["fruits", "fruit intake", "水果摄入量"],
     "鲜、冻、熟、罐装或干水果；排除果汁及盐渍、腌制水果。"),
    ("vegetables_g_d", "vegetables", "蔬菜", "g/d", 360, (290, 430), "low", 5000,
     ["vegetables", "vegetable intake", "蔬菜摄入量"],
     "排除豆类、盐渍或腌制蔬菜、蔬菜汁、坚果、种子及土豆、玉米等淀粉类蔬菜。"),
    ("legumes_g_d", "legumes", "豆类", "g/d", 60, (50, 70), "low", 3000,
     ["legumes", "legume intake", "豆类摄入量"],
     "鲜、冻、熟、罐装或干豆类；须记录采用的食物形态，不自动换算干重、熟重。"),
    ("whole_grains_g_d", "whole_grains", "全谷物", "g/d", 125, (100, 150), "low", 3000,
     ["whole grains", "whole grain intake", "全谷物摄入量"],
     "麸皮、胚芽和胚乳保持天然比例的全谷物部分；不能把混合食品总重全部计入。"),
    ("nuts_seeds_g_d", "nuts_seeds", "坚果和种子", "g/d", 21, (16, 25), "low", 1000,
     ["nuts and seeds", "坚果及种子", "坚果种子摄入量"], "坚果及种子类食物。"),
    ("milk_g_d", "milk", "牛奶", "g/d", 435, (350, 520), "low", 10000,
     ["milk", "牛奶摄入量", "奶类饮用量"],
     "包括脱脂、低脂和全脂奶；不包括豆奶和其他植物饮品，不以全部乳制品代替。"),
    ("red_meat_g_d", "red_meat", "红肉", "g/d", 23, (18, 27), "high", 3000,
     ["red meat", "红肉摄入量"], "牛、猪、绵羊、山羊肉；排除禽、鱼、蛋及所有加工肉。"),
    ("processed_meat_g_d", "processed_meat", "加工肉", "g/d", 2, (0, 4), "high", 2000,
     ["processed meat", "加工肉摄入量"], "经烟熏、腌制、盐渍或添加化学防腐剂保存的肉。"),
    ("sugar_sweetened_beverages_g_d", "sugar_sweetened_beverages", "含糖饮料", "g/d", 3, (0, 5), "high", 15000,
     ["sugar-sweetened beverages", "SSB", "含糖饮料摄入量"],
     "每226.8克一份含至少50千卡的饮料，包括汽水、能量饮料及果味饮料；排除纯果蔬汁。单位是饮料总质量，不是糖质量。"),
    ("fibre_g_d", "fibre", "膳食纤维", "g/d", 24, (19, 28), "low", 200,
     ["fibre", "fiber", "dietary fibre", "dietary fiber", "膳食纤维摄入量"], "所有来源的膳食纤维总摄入量。"),
    ("calcium_g_d", "calcium", "膳食钙", "g/d", 1.25, (1.00, 1.50), "low", 10,
     ["dietary calcium", "calcium intake", "钙摄入量"], "所有来源的钙摄入量；不是血钙。若原记录为mg/d，先按1000 mg = 1 g整理为g/d。"),
    ("seafood_omega3_g_d", "seafood_omega3", "海产品EPA和DHA", "g/d", 0.250, (0.200, 0.300), "low", 20,
     ["seafood omega-3 fatty acids", "EPA+DHA", "EPA和DHA摄入量"],
     "海产品来源EPA与DHA合计；不是鱼肉重量、鱼油总重或ALA。原表250 mg/d精确换算为0.250 g/d。"),
    ("omega6_energy_pct", "omega6", "Omega-6供能比", "%", 11, (9, 13), "low", 100,
     ["omega-6 energy percent", "omega6 energy percent", "ω-6供能比"],
     "Omega-6脂肪酸占每日总能量的百分比；不是全部脂肪供能比，也不是食物质量百分比。"),
    ("trans_fat_energy_pct", "trans_fat", "反式脂肪供能比", "%", 0.5, (0.0, 1.0), "high", 100,
     ["trans fat energy percent", "trans fatty acids energy percent", "反式脂肪酸供能比"],
     "所有来源反式脂肪酸占每日总能量的百分比。与Omega-6供能比之和不能超过100%。"),
    ("urinary_sodium_g_d", "urinary_sodium", "24小时尿钠", "g/d", 3, (1, 5), "high", 30,
     ["24 h urinary sodium", "24-hour urinary sodium", "24h尿钠", "24小时尿钠排泄量"],
     "完整24小时尿钠排泄质量；不是尿钠浓度、随机尿、膳食钠或食盐。论文的膳食钠转尿钠系数未印出，不做此转换。"),
]

FACTORS = {
    key: dict(output=output, label_zh=label, unit=unit, reference=ref,
              reference_range=list(bounds), risk_direction=direction,
              input_max=maximum, aliases=aliases, definition_zh=definition)
    for key, output, label, unit, ref, bounds, direction, maximum, aliases, definition in _ROWS
}

BOUNDARY = "本报告仅将个人记录与GBD 2017的人群研究参考值作算术对照；不足或超量只表示相对参考点的差值，不诊断营养缺乏，不预测个人患病、死亡风险或寿命，不提供饮食处方、补剂剂量或用药启停建议。参考范围表示模型参考值的不确定性，不是个人安全区间。"
