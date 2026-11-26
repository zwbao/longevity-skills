"""Yuan et al. 2017 Table 3 and §3.1.3; no fitted or inferred constants."""
TITLE = '中国健康膳食指数 CHEI（2017）'
BOUNDARY = ('本报告只计算与《中国居民膳食指南（2016）》相符程度，不预测疾病、寿命或干预效果；'
            '短期饮食记录不能代表长期饮食。酒精得分不代表安全饮酒量，不据此开始或增加饮酒；'
            '不提供药物剂量，也不能据此开始或停止用药。')
AGE_RANGE = [2, 120]  # Software guard, not the observed cohort's upper age.
ENERGY_SCALE = 1000  # §3.1.3 amounts per 1000 kcal
GRAM_TO_MG = 1000    # Exact SI scaling, not a fitted parameter.
ADULT_AGE = 18
ALCOHOL = {'male': (25, 60), 'female': (15, 40)}  # prose, not reversed Table 3 row

# name, Chinese label, full-score density, maximum points (Table 3)
_ADEQUACY = [
    ('total_grains', '总谷物', 2.5, 5),
    ('whole_grains_mixed_beans', '全谷物和杂豆', 0.6, 5),
    ('tubers', '薯类', 0.3, 5),
    ('total_vegetables', '总蔬菜', 1.9, 5),
    ('dark_vegetables', '深色蔬菜', 0.9, 5),
    ('fruits', '水果', 1.1, 10),
    ('dairy', '奶类', 0.5, 5),
    ('soybeans', '大豆及制品', 0.4, 5),
    ('fish_seafood', '鱼和水产品', 0.6, 5),
    ('poultry', '禽肉', 0.3, 5),
    ('eggs', '蛋类', 0.5, 5),
    ('seeds_nuts', '种子和坚果', 0.4, 5),
]
COMPONENTS = {
    k: {'label_zh': label, 'input': k + '_sp_d', 'full': full, 'zero': 0,
        'max': maximum, 'direction': 'adequacy', 'density_unit': 'SP/1000 kcal'}
    for k, label, full, maximum in _ADEQUACY
}
for k, label, key, full, zero, maximum, unit in [
    ('red_meat', '红肉', 'red_meat_sp_d', 0.4, 3.5, 5, 'SP/1000 kcal'),
    ('cooking_oils', '烹调油', 'cooking_oils_g_d', 15.6, 32.6, 10, 'g/1000 kcal'),
    ('sodium', '钠', 'sodium_g_d', 1000, 3608, 10, 'mg/1000 kcal'),
    ('added_sugars', '添加糖', 'added_sugars_energy_pct', 10, 20, 5, '% 能量'),
    ('alcohol', '酒精', 'alcohol_g_d', None, None, 5, 'g/d'),
]:
    COMPONENTS[k] = {'label_zh': label, 'input': key, 'full': full, 'zero': zero,
                     'max': maximum, 'direction': 'limitation', 'density_unit': unit}

INPUTS = {}
for name, c in COMPONENTS.items():
    key = c['input']
    is_sp = key.endswith('_sp_d')
    unit = '1' if is_sp else ('%' if name == 'added_sugars' else 'g/d')
    upper = 60 if is_sp else {'cooking_oils': 300, 'sodium': 30, 'added_sugars': 100, 'alcohol': 300}[name]
    INPUTS[key] = {'label_zh': c['label_zh'] + ('每日标准份数' if is_sp else {'cooking_oils': '每日克数', 'sodium': '每日克数', 'added_sugars': '供能百分比', 'alcohol': '每日克数'}[name]),
                   'unit': unit, 'range': [0, upper],
                   'display_unit': 'SP/d' if is_sp else unit}
INPUTS['energy_kcal_d'] = {'label_zh': '每日总能量千卡数', 'unit': '1', 'range': [100, 10000], 'display_unit': 'kcal/d'}
INPUTS['pregnant_lactating_yes'] = {'label_zh': '孕期或哺乳期', 'unit': '1', 'range': [0, 1], 'display_unit': '是=1，否或不适用=0'}
DIET_KEYS = tuple(k for k in INPUTS if k != 'pregnant_lactating_yes')
