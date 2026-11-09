"""Constants for the Philadelphia expanded ACE count, Temple et al., JAMA Netw Open 2026;9(9):e2635834.

Every number here is printed in the paper or its Supplement 1:
- items, answer options and the 'Item Threshold for Adversity': eTable 1 (Supplement 1)
- ACE categories 0, 1 to 3, 4 to 5, 6 or more: Methods, Exposure Measure / Statistical Methods
- cohort prevalence per category: Table 2
- adjusted odds ratios versus 0 ACEs: Table 3
The report quotes them as the cohort's numbers, never as this person's risk.
"""

TITLE = "童年逆境计数（费城扩展 ACE）"
BOUNDARY = (
    "这是按论文方法数出的童年逆境条数和该分档在研究队列里的比例，不是诊断，也不是你自己的发生概率。"
    "论文是观察性关联，不能说明因果。报告不给任何用药或剂量，不能据此开始或停止任何药物。"
    "如果你现在有伤害自己的想法，请立即拨打 120 或当地心理危机干预热线。"
)
COHORT_N = 1850

# Answer scales. Each code is the position on the printed answer list, counted from the end
# that names no adversity for negatively worded items (eTable 1 lists the options in order).
SCALES = {
    "freq3": {  # more than once, once, never
        "codes": {0: "从来没有", 1: "一次", 2: "不止一次"},
        "text": {"never": 0, "从来没有": 0, "从没有": 0, "没有": 0, "从不": 0,
                 "once": 1, "一次": 1, "more than once": 2, "不止一次": 2, "多次": 2},
    },
    "yesno": {
        "codes": {0: "否", 1: "是"},
        "text": {"no": 0, "n": 0, "否": 0, "无": 0, "没有": 0, "yes": 1, "y": 1, "是": 1, "有": 1},
    },
    "true5": {  # very often true, often true, sometimes true, rarely true, never true
        "codes": {0: "从不符合", 1: "很少符合", 2: "有时符合", 3: "经常符合", 4: "非常经常符合"},
        "text": {"never true": 0, "从不符合": 0, "从不": 0, "rarely true": 1, "很少符合": 1, "很少": 1,
                 "sometimes true": 2, "有时符合": 2, "有时": 2, "often true": 3, "经常符合": 3, "经常": 3,
                 "very often true": 4, "非常经常符合": 4, "总是": 4},
    },
    "freq4": {  # many times, a few times, once, never
        "codes": {0: "从来没有", 1: "一次", 2: "几次", 3: "很多次"},
        "text": {"never": 0, "从来没有": 0, "从没有": 0, "没有": 0, "从不": 0, "once": 1, "一次": 1,
                 "a few times": 2, "几次": 2, "many times": 3, "很多次": 3},
    },
    "time4": {  # all of the time, most of the time, some of the time, none of the time
        "codes": {0: "从来没有", 1: "有时", 2: "大部分时间", 3: "一直"},
        "text": {"none of the time": 0, "从来没有": 0, "从不": 0, "some of the time": 1, "有时": 1,
                 "most of the time": 2, "大部分时间": 2, "all of the time": 3, "一直": 3, "总是": 3},
    },
}

# eTable 1 'Item Threshold for Adversity'. ">=" counts that answer and answers further toward
# adversity; "<=" is for the three positively worded items (someone made you feel important,
# felt safe, neighbors looked out for each other), where adversity is the answer printed and
# the answers below it. The direction is the reading of eTable 1 written in references/contract.md.
# (key, domain, label_zh, scale, op, threshold code, printed threshold)
ITEMS = (
    ("ea_insult", "emotional_abuse", "大人辱骂、贬低你", "freq3", ">=", 2, "more than once"),
    ("ea_afraid", "emotional_abuse", "大人让你害怕会挨打", "freq3", ">=", 2, "more than once"),
    ("pa_push", "physical_abuse", "大人推、抓、搡或打耳光", "freq3", ">=", 2, "more than once"),
    ("pa_marks", "physical_abuse", "大人打得留下伤痕或受伤", "freq3", ">=", 1, "once"),
    ("sa_touch", "sexual_abuse", "年长者以性的方式触摸你", "yesno", ">=", 1, "yes"),
    ("sa_intercourse", "sexual_abuse", "年长者企图或实施性交", "yesno", ">=", 1, "yes"),
    ("en_important", "emotional_neglect", "有人让你觉得自己重要", "true5", "<=", 1, "rarely true"),
    ("pn_meals", "physical_neglect", "家里因为没钱减餐或不吃饭", "true5", ">=", 3, "often true"),
    ("dv_beaten", "domestic_violence", "看到或听到家里大人被打", "freq4", ">=", 2, "a few times"),
    ("dv_weapon", "domestic_violence", "看到或听到家里大人被器物击打或刺伤", "freq4", ">=", 1, "once"),
    ("hh_alcohol", "household_substance", "同住的人酗酒", "yesno", ">=", 1, "yes"),
    ("hh_drugs", "household_substance", "同住的人吸毒或滥用处方药", "yesno", ">=", 1, "yes"),
    ("hh_depressed", "household_mental_illness", "同住的大人抑郁或有精神疾病", "yesno", ">=", 1, "yes"),
    ("hh_suicidal", "household_mental_illness", "同住的大人有自杀倾向", "yesno", ">=", 1, "yes"),
    ("hh_incarcerated", "incarcerated_member", "同住的人坐过牢或被判刑", "yesno", ">=", 1, "yes"),
    ("wv_seen", "witnessed_violence", "亲眼看到或听到有人被殴打、刺伤或枪击", "freq4", ">=", 2, "a few times"),
    ("disc_race", "discrimination", "因种族或民族受到不公对待", "true5", ">=", 2, "sometimes true"),
    ("nb_safe", "neighborhood", "在社区里觉得安全", "time4", "<=", 1, "some of the time"),
    ("nb_trust", "neighborhood", "社区里的人互相照应、值得信任", "time4", "<=", 1, "some of the time"),
    ("bullied", "bullied", "被同伴或同学欺负", "time4", ">=", 2, "most of the time"),
    ("foster_care", "foster_care", "进过寄养家庭", "yesno", ">=", 1, "yes"),
)

# The 14 domains in eTable 1 order, with the 18-year incidence it prints (No. (%), n = 1850).
# The paper does not print which domains it counts as conventional and which as community-level,
# so the report does not split the count.
DOMAINS = (
    ("emotional_abuse", "情感虐待", (532, 29.4)),
    ("physical_abuse", "身体虐待", (483, 26.7)),
    ("sexual_abuse", "性虐待", (192, 10.5)),
    ("emotional_neglect", "情感忽视", (174, 9.5)),
    ("physical_neglect", "身体忽视", (190, 10.4)),
    ("domestic_violence", "目睹家庭暴力", (298, 16.4)),
    ("household_substance", "家人物质滥用", (429, 23.6)),
    ("household_mental_illness", "家人精神疾病", (489, 26.8)),
    ("incarcerated_member", "家人入狱", (260, 14.3)),
    ("witnessed_violence", "目睹社区暴力", (310, 17.0)),
    ("discrimination", "感到被歧视", (690, 37.8)),
    ("neighborhood", "不安全或缺乏互信的社区", (815, 44.7)),
    ("bullied", "被欺负", (267, 14.6)),
    ("foster_care", "寄养", (68, 3.7)),
)

# Methods: "categorized exposure as 0, 1 to 3, 4 to 5, or at least 6 or more ACEs".
CATEGORIES = (("0", 0, 0), ("1-3", 1, 3), ("4-5", 4, 5), ("6+", 6, 14))
CATEGORY_ZH = {"0": "0 条", "1-3": "1 到 3 条", "4-5": "4 到 5 条", "6+": "6 条及以上"}
# Table 2 column sizes.
CATEGORY_N = {"0": 337, "1-3": 878, "4-5": 355, "6+": 253}
MISSING_ACE = 27  # Table 2 footnote b: "Twenty seven (1.5%) participants were missing data for the ACEs measure."

# Outcome labels, in Table 2 and Table 3 row order.
OUTCOMES = (
    ("depression", "抑郁（CES-D-10 ≥10）", "心理健康"),
    ("ptsd", "创伤后应激障碍（PC-PTSD-5 ≥3，只筛查报告过创伤事件的人）", "心理健康"),
    ("suicide_ideation", "过去一年有自杀念头", "心理健康"),
    ("suicide_attempt", "自杀尝试（终生）", "心理健康"),
    ("dv_exp_physical", "遭受恋爱关系中的身体暴力", "遭受约会暴力"),
    ("dv_exp_sexual", "遭受恋爱关系中的性暴力", "遭受约会暴力"),
    ("dv_exp_threatening", "遭受恋爱关系中的威胁", "遭受约会暴力"),
    ("dv_exp_psychological", "遭受恋爱关系中的心理暴力", "遭受约会暴力"),
    ("dv_perp_physical", "对伴侣施加身体暴力", "实施约会暴力"),
    ("dv_perp_sexual", "对伴侣施加性暴力", "实施约会暴力"),
    ("dv_perp_threatening", "对伴侣施加威胁", "实施约会暴力"),
    ("dv_perp_psychological", "对伴侣施加心理暴力", "实施约会暴力"),
    ("sexual_assault", "遭受性侵（终生）", "其他暴力"),
    ("physical_fight", "过去一年打过架", "其他暴力"),
    ("binge_drinking", "过去一月狂饮", "物质使用"),
    ("marijuana", "过去一年用过大麻", "物质使用"),
    ("illicit_substance", "过去一年用过兴奋剂、致幻剂、海洛因或摇头丸", "物质使用"),
    ("hs_a_b_average", "高中成绩平均 A 或 B", "学业"),
    ("graduated_hs", "高中毕业", "学业"),
    ("enrolled_college", "就读四年制大学", "学业"),
)

# Table 2: (n, %) per ACE category; Table 3: OR text (95% CI) and P per category vs 0 ACEs.
# Generated from the PMC full text by pattern match, then read against the page.
TABLE2 = {
    'depression': {'overall': (695, 37.9), '0': (70, 21.0), '1-3': (313, 36.0), '4-5': (165, 46.5), '6+': (141, 56.9)},  # Depression
    'ptsd': {'overall': (210, 11.4), '0': (7, 2.1), '1-3': (69, 7.5), '4-5': (54, 15.2), '6+': (77, 30.9)},  # PTSD
    'suicide_ideation': {'overall': (390, 21.3), '0': (20, 6.0), '1-3': (166, 19.1), '4-5': (98, 27.8), '6+': (103, 41.4)},  # Suicide ideation
    'suicide_attempt': {'overall': (278, 15.1), '0': (15, 4.5), '1-3': (95, 10.9), '4-5': (72, 20.4), '6+': (93, 37.2)},  # Suicide attempt
    'dv_exp_physical': {'overall': (109, 6.0), '0': (9, 2.7), '1-3': (32, 3.7), '4-5': (30, 8.5), '6+': (37, 14.9)},  # Physical
    'dv_exp_sexual': {'overall': (81, 4.4), '0': (4, 1.2), '1-3': (26, 3.0), '4-5': (21, 5.9), '6+': (29, 11.6)},  # Sexual
    'dv_exp_threatening': {'overall': (122, 6.7), '0': (8, 2.4), '1-3': (43, 4.9), '4-5': (32, 9.1), '6+': (39, 15.6)},  # Threatening
    'dv_exp_psychological': {'overall': (306, 16.6), '0': (24, 7.1), '1-3': (123, 14.0), '4-5': (87, 24.5), '6+': (71, 28.3)},  # Psychological
    'dv_perp_physical': {'overall': (96, 5.2), '0': (5, 1.5), '1-3': (31, 3.6), '4-5': (25, 7.1), '6+': (35, 14.1)},  # Physical
    'dv_perp_sexual': {'overall': (31, 1.7), '0': (0, 0.0), '1-3': (12, 1.4), '4-5': (6, 1.7), '6+': (13, 5.2)},  # Sexual
    'dv_perp_threatening': {'overall': (101, 5.5), '0': (5, 1.5), '1-3': (29, 3.3), '4-5': (25, 7.1), '6+': (40, 16.0)},  # Threatening
    'dv_perp_psychological': {'overall': (272, 14.7), '0': (18, 5.4), '1-3': (101, 11.5), '4-5': (74, 20.8), '6+': (76, 30.3)},  # Psychological
    'sexual_assault': {'overall': (182, 9.9), '0': (8, 2.4), '1-3': (58, 6.6), '4-5': (44, 12.5), '6+': (69, 27.6)},  # Sexual assault
    'physical_fight': {'overall': (140, 7.6), '0': (8, 2.4), '1-3': (40, 4.6), '4-5': (43, 12.1), '6+': (48, 19.2)},  # Physical fight
    'binge_drinking': {'overall': (194, 10.7), '0': (20, 6.0), '1-3': (78, 9.0), '4-5': (51, 14.5), '6+': (42, 17.1)},  # Binge drinking
    'marijuana': {'overall': (406, 22.1), '0': (37, 11.1), '1-3': (156, 17.8), '4-5': (107, 30.2), '6+': (98, 39.2)},  # Marijuana use
    'illicit_substance': {'overall': (79, 4.3), '0': (1, 0.3), '1-3': (27, 3.1), '4-5': (22, 6.3), '6+': (27, 10.8)},  # Illicit substance use
    'hs_a_b_average': {'overall': (1568, 85.0), '0': (314, 93.5), '1-3': (760, 86.7), '4-5': (290, 81.9), '6+': (182, 72.5)},  # Academic performance in HS
    'graduated_hs': {'overall': (1715, 92.9), '0': (318, 94.4), '1-3': (820, 93.5), '4-5': (335, 94.4), '6+': (219, 86.6)},  # Graduated HS
    'enrolled_college': {'overall': (849, 46.6), '0': (186, 55.2), '1-3': (424, 48.4), '4-5': (155, 43.7), '6+': (84, 33.2)},  # Enrolled in college
}
TABLE3 = {
    'depression': {'n': 1798, 'icc': '0.000', '1-3': ('2.13 (1.56-2.91)', '<.001'), '4-5': ('3.09 (2.16-4.41)', '<.001'), '6+': ('4.53 (3.06-6.70)', '<.001')},  # Depression
    'ptsd': {'n': 1802, 'icc': '0.009', '1-3': ('3.68 (1.66-8.17)', '.001'), '4-5': ('6.67 (2.94-15.13)', '<.001'), '6+': ('16.58 (7.31-37.61)', '<.001')},  # PTSD
    'suicide_ideation': {'n': 1797, 'icc': '0.020', '1-3': ('3.73 (2.25-6.20)', '<.001'), '4-5': ('5.36 (3.12-9.21)', '<.001'), '6+': ('9.71 (5.56-16.99)', '<.001')},  # Suicide ideation
    'suicide_attempt': {'n': 1800, 'icc': '0.000', '1-3': ('2.31 (1.30-4.08)', '.004'), '4-5': ('4.09 (2.25-7.43)', '<.001'), '6+': ('9.04 (4.95-16.51)', '<.001')},  # Suicide attempt
    'dv_exp_physical': {'n': 1795, 'icc': '0.006', '1-3': ('1.13 (0.53-2.43)', '.75'), '4-5': ('2.59 (1.19-5.63)', '.02'), '6+': ('4.45 (2.05-9.68)', '<.001')},  # Physical
    'dv_exp_sexual': {'n': 1805, 'icc': '0.000', '1-3': ('2.23 (0.77-6.51)', '.14'), '4-5': ('4.32 (1.44-12.94)', '.009'), '6+': ('8.53 (2.87-25.39)', '<.001')},  # Sexual
    'dv_exp_threatening': {'n': 1798, 'icc': '0.002', '1-3': ('1.90 (0.88-4.13)', '.10'), '4-5': ('3.52 (1.57-7.89)', '.002'), '6+': ('6.33 (2.83-14.17)', '<.001')},  # Threatening
    'dv_exp_psychological': {'n': 1810, 'icc': '0.000', '1-3': ('1.99 (1.26-3.16)', '.003'), '4-5': ('3.87 (2.72-7.63)', '<.001'), '6+': ('4.55 (2.72-7.63)', '<.001')},  # Psychological
    'dv_perp_physical': {'n': 1796, 'icc': '0.000', '1-3': ('2.19 (0.84-5.72)', '.11'), '4-5': ('3.93 (1.47-10.52)', '.007'), '6+': ('7.66 (2.88-20.34)', '<.001')},  # Physical
    'dv_perp_sexual': {'n': 1804, 'icc': '0.078', '1-3': ('NA', 'NA'), '4-5': ('1.56 (0.57-4.29)', '.38'), '6+': ('4.94 (2.12-11.52)', '<.001')},  # Sexual
    'dv_perp_threatening': {'n': 1796, 'icc': '0.000', '1-3': ('2.06 (0.78-5.39)', '.14'), '4-5': ('4.15 (1.55-11.10)', '.005'), '6+': ('9.80 (3.72-25.81)', '<.001')},  # Threatening
    'dv_perp_psychological': {'n': 1810, 'icc': '0.010', '1-3': ('2.28 (1.35-3.85)', '.002'), '4-5': ('4.58 (2.63-7.96)', '<.001'), '6+': ('7.50 (4.24-13.24)', '<.001')},  # Psychological
    'sexual_assault': {'n': 1800, 'icc': '0.009', '1-3': ('2.76 (1.28-5.92)', '.009'), '4-5': ('4.84 (2.19-10.69)', '<.001'), '6+': ('13.18 (5.98-29.02)', '<.001')},  # Sexual assault
    'physical_fight': {'n': 1798, 'icc': '0.000', '1-3': ('1.72 (0.79-3.74)', '.17'), '4-5': ('4.55 (2.08-9.96)', '<.001'), '6+': ('7.47 (3.39-16.47)', '<.001')},  # Physical fight
    'binge_drinking': {'n': 1786, 'icc': '0.008', '1-3': ('1.37 (0.82-2.30)', '.24'), '4-5': ('2.35 (1.34-4.10)', '.003'), '6+': ('2.79 (1.55-5.02)', '.001')},  # Binge drinking
    'marijuana': {'n': 1804, 'icc': '0.007', '1-3': ('1.58 (1.07-2.34)', '.02'), '4-5': ('2.88 (1.89-4.39)', '<.001'), '6+': ('4.00 (2.56-6.24)', '<.001')},  # Marijuana use
    'illicit_substance': {'n': 1802, 'icc': '0.028', '1-3': ('9.14 (1.23-67.84)', '.03'), '4-5': ('16.88 (2.24-127.14)', '.006'), '6+': ('27.83 (3.70-209.31)', '.001')},  # Illicit substance use
    'hs_a_b_average': {'n': 1809, 'icc': '0.035', '1-3': ('0.57 (0.35-0.92)', '.02'), '4-5': ('0.43 (0.25-0.73)', '.002'), '6+': ('0.29 (0.17-0.49)', '<.001')},  # Academic performance in HS
    'graduated_hs': {'n': 1813, 'icc': '0.045', '1-3': ('1.09 (0.63-1.89)', '.77'), '4-5': ('1.40 (0.71-2.73)', '.33'), '6+': ('0.59 (0.32-1.11)', '.10')},  # Graduated HS
    'enrolled_college': {'n': 1812, 'icc': '0.120', '1-3': ('0.99 (0.74-1.34)', '.96'), '4-5': ('0.88 (0.61-1.25)', '.47'), '6+': ('0.62 (0.42-0.93)', '.02')},  # Enrolled in college
}

# Table 3 footnote c: sexual DV perpetration uses 0 and 1 to 3 ACEs combined as the referent.
TABLE3_NOTES = {
    "dv_perp_sexual": "这一行的参照组是 0 条和 1 到 3 条合并（表 3 脚注 c，格子太小）。",
    "dv_exp_psychological": "表 3 这一行 4 到 5 条的置信区间印作 2.72-7.63，和 6 条及以上那一格相同，照原样抄录。",
}
