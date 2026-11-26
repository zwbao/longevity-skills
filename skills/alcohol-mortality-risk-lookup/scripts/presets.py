"""Zhao et al., JAMA Network Open 2023: Tables 2/4, Fully adjusted.
Reference is lifetime nondrinker. Exact printed cells; no fitted coefficients.
"""
TITLE = '日均饮酒量与全因死亡关联查表'
INPUT_KEY = 'ethanol_g_day'
INPUT_UNIT = 'g/d'
PLAUSIBLE_RANGE = (0, 300)  # Input plausibility guard, not a published safety limit.
BOUNDARY = ('这是观察性队列荟萃分析的人群关联查表，不是个人死亡概率、寿命预测或改变饮酒后的因果效应；'
            '未显著不等于无风险，不能据此建议开始饮酒，也不提供药物剂量或启停药建议。')
CATEGORIES = ('occasional', 'low', 'medium', 'high', 'higher')
CUTPOINTS = (1.30, 25, 45, 65)
LABELS = {
    'lifetime_abstainer': '终身不饮酒（参照）', 'former': '既往饮酒、现已完全不饮酒',
    'occasional': '偶尔饮酒（>0 至 <1.30 g/d）', 'low': '低量（1.30 至 <25 g/d）',
    'medium': '中量（25 至 <45 g/d）', 'high': '高量（45 至 <65 g/d）',
    'higher': '更高量（≥65 g/d）',
}
STRATA = {'overall': '总体（表 2）', 'male': '男性（表 4）', 'female': '女性（表 4）'}
# Columns: RR, lower 95% CI, upper 95% CI.
TABLES = {
    'overall': {
        'lifetime_abstainer': (1.00, None, None), 'former': (1.26, 1.12, 1.42),
        'occasional': (.96, .86, 1.06), 'low': (.93, .85, 1.01),
        'medium': (1.05, .96, 1.14), 'high': (1.19, 1.07, 1.32), 'higher': (1.35, 1.23, 1.47),
    },
    'male': {
        'lifetime_abstainer': (1.00, None, None), 'former': (1.39, 1.21, 1.58),
        'occasional': (1.00, .91, 1.09), 'low': (.94, .88, 1.01),
        'medium': (1.01, .93, 1.10), 'high': (1.15, 1.03, 1.28), 'higher': (1.34, 1.23, 1.47),
    },
    'female': {
        'lifetime_abstainer': (1.00, None, None), 'former': (1.27, 1.13, 1.43),
        'occasional': (.99, .87, 1.11), 'low': (.99, .90, 1.10),
        'medium': (1.21, 1.08, 1.36), 'high': (1.34, 1.11, 1.63), 'higher': (1.61, 1.44, 1.80),
    },
}
