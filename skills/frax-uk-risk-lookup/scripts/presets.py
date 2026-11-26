"""Kanis et al. 2008, DOI 10.1007/s00198-007-0543-5, Table 2.

Numeric facts transcribed into code; each row contains major fracture at
50/60/70/80 years then hip fracture at 50/60/70/80 years (percent).
No FRAX coefficients are inferred from this table.
"""
TITLE = '英国 FRAX 骨折概率查表（2008 年表 2）'
BOUNDARY = '这是2008年英国模型表2在固定BMI和单一危险因素条件下的查表值，不是完整或现行FRAX，也未经中国人群校准；不能据此诊断、决定治疗、开始或停用药物。情景差异不是改变行为后的因果获益。'
AGES = (50, 60, 70, 80)
BMI = 25
FACTORS = {
    'parental_hip_fracture': '父母髋部骨折史',
    'current_smoking': '目前吸烟',
    'high_alcohol': '高酒精摄入分类',
    'rheumatoid_arthritis': '类风湿关节炎',
    'oral_glucocorticoids': '曾长期口服糖皮质激素',
    'previous_fragility_fracture': '既往脆性骨折',
}
TARGET_KEYS = ('current_smoking', 'high_alcohol')
INPUT_SPECS = {'bmi_kg_m2': ('kg/m^2', (10, 80)),
               **{key: ('1', (0, 1)) for key in FACTORS},
               'secondary_osteoporosis': ('1', (0, 1)), 'age': ('a', (50, 80))}
OUTPUTS = {'major_osteoporotic_10y_pct': '主要骨质疏松性骨折十年概率',
           'hip_fracture_10y_pct': '髋部骨折十年概率'}
TABLE_2 = {
    'male': {
        'none': (2.8, 3.9, 5.7, 7.2, 0.1, 0.4, 1.3, 3.4),
        'parental_hip_fracture': (5.5, 7.6, 9.1, 15, 0.2, 0.6, 2.8, 11),
        'current_smoking': (2.8, 4.1, 5.9, 7.5, 0.2, 0.7, 1.8, 4.2),
        'high_alcohol': (3.3, 4.7, 7.1, 9.5, 0.2, 0.7, 2.0, 5.1),
        'rheumatoid_arthritis': (3.7, 5.3, 8.0, 11, 0.2, 0.8, 2.3, 5.8),
        'oral_glucocorticoids': (4.4, 6.1, 8.5, 10, 0.3, 0.9, 2.4, 5.5),
        'previous_fragility_fracture': (5.8, 7.9, 11, 12, 0.5, 1.3, 2.7, 5.2),
    },
    'female': {
        'none': (3.5, 6.0, 11, 17, 0.2, 0.7, 2.3, 7.0),
        'parental_hip_fracture': (6.9, 12, 17, 31, 0.3, 0.9, 5.0, 22),
        'current_smoking': (3.6, 6.5, 12, 19, 0.3, 1.1, 3.4, 9.5),
        'high_alcohol': (4.1, 7.3, 14, 22, 0.3, 1.1, 3.6, 10),
        'rheumatoid_arthritis': (4.7, 8.2, 15, 25, 0.4, 1.3, 4.1, 12),
        'oral_glucocorticoids': (5.6, 9.8, 18, 26, 0.5, 1.5, 4.8, 13),
        'previous_fragility_fracture': (7.4, 12, 20, 28, 0.8, 2.1, 4.9, 11),
    },
}
