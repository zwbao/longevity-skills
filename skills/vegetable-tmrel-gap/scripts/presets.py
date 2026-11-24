"""Published endpoints; this module does not implement the MR-BRT risk curves."""
INTAKE_KEY = "vegetables_g_d"
UNIT = "g/d"
# Results: Minimum risk level of vegetable intake; also Table 1.
TMREL_LOWER_G_D = 306.0
TMREL_UPPER_G_D = 372.0
# Results Overview, largest observed exposure. Descriptive, not a safety limit.
OBSERVED_MAX_G_D = 1177.0
# Engineering input guard only, not a published clinical threshold.
INPUT_RANGE = (0, 3000)
BOUNDARY = "这里只比较饮食记录与论文的人群参考范围，不预测个人疾病风险，不证明改变摄入会带来相应获益，也不能据此开始或停止药物。"
FOOD_DEFINITION = "计入新鲜、冷冻、烹调、罐装或干制蔬菜；排除豆类、盐渍或腌制蔬菜、蔬菜汁、坚果种子，以及土豆、玉米等淀粉类蔬菜。"

