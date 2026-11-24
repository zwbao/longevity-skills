"""Published Supplementary material_20210604_v2.docx, Methods Tables 1–3.

Four-decimal coefficients, S10 and mean LP are printed in Methods Table 3;
regional scales are from Methods Table 1. No fitted or inferred constants.
SBP coefficients here are PER mmHg, unlike main-text Table 2 (per 10 mmHg).
"""
TITLE = 'SCORE2-OP 十年心血管事件风险（仍在验证）'
BOUNDARY = ('这是已发表风险方程的暂定复算，尚未复现地区校准后的论文算例；'
            '不是诊断、个人寿命预测或治疗建议，不能据此开始或停止任何药物。'
            '目标值差异只表示模型估计变化，不等于干预能够带来的风险下降。')
GAP = ('补充 Methods Table 1 与 Table 3 的低风险地区校准参数不同，'
       '按参数表计算不能复现算例的女性 14% 和男性 19.3%；因此结果仍在验证。')
CENTERS = {'age': 73, 'sbp_mmhg': 150, 'tc_mmol_l': 6, 'hdl_mmol_l': 1.4}
# Order: age, diabetes, smoker, SBP, TC, HDL, age*diabetes, age*smoker,
# age*SBP, age*TC, age*HDL. Source: Supplementary Methods Table 3.
COEFFICIENTS = {
    'male': (0.0634, 0.4245, 0.3524, 0.0094, 0.0850, -0.3564,
             -0.0174, -0.0247, -0.0005, 0.0073, 0.0091),
    'female': (0.0789, 0.6010, 0.4921, 0.0102, 0.0605, -0.3040,
               -0.0107, -0.0255, -0.0004, -0.0009, 0.0154),
}
BASE_SURVIVAL_10Y = {'male': 0.7576, 'female': 0.8082}
MEAN_LP = {'male': 0.0929, 'female': 0.229}
SCALES = {
    'low': {'male': (-0.34, 1.19), 'female': (-0.52, 1.01)},
    'moderate': {'male': (0.01, 1.25), 'female': (-0.1, 1.1)},
    'high': {'male': (0.08, 1.15), 'female': (0.38, 1.09)},
    'very_high': {'male': (0.05, 0.7), 'female': (0.38, 0.69)},
}
REGION_LABELS = {'low': '低风险地区', 'moderate': '中等风险地区',
                 'high': '高风险地区', 'very_high': '很高风险地区'}
# Supplementary Table 2: country allocation frozen to 2021, not ethnicity.
COUNTRIES = {
    'low': ('France', 'Israel', 'Spain', 'Netherlands', 'Switzerland', 'Denmark',
            'Norway', 'Luxembourg', 'Belgium', 'United Kingdom'),
    'moderate': ('Iceland', 'Portugal', 'Sweden', 'Italy', 'San Marino', 'Ireland',
                 'Cyprus', 'Finland', 'Austria', 'Malta', 'USA', 'Greece', 'Germany', 'Slovenia'),
    'high': ('Albania', 'Czech Republic', 'Turkey', 'Kazakhstan', 'Croatia', 'Poland',
             'Estonia', 'Slovakia', 'Hungary', 'Bosnia and Herzegovina'),
    'very_high': ('Armenia', 'Lithuania', 'Georgia', 'Latvia', 'Serbia', 'Romania',
                  'Montenegro', 'Russian Federation', 'TFYR Macedonia', 'Belarus',
                  'Azerbaijan', 'Bulgaria', 'Republic of Moldova', 'Ukraine', 'Kyrgyzstan',
                  'Uzbekistan', 'Egypt', 'Morocco', 'Syria', 'Tunisia', 'Lebanon', 'Algeria', 'Libya'),
}
COUNTRY_ALIASES = {'英国': 'United Kingdom', 'uk': 'United Kingdom', '美国': 'USA',
                   'united states': 'USA', '法国': 'France', '德国': 'Germany',
                   '挪威': 'Norway', '荷兰': 'Netherlands'}
MEASUREMENT_UNITS = {'sbp_mmhg': 'mmHg', 'tc_mmol_l': 'mmol/L',
                     'hdl_mmol_l': 'mmol/L', 'smoker': '1', 'diabetes': '1'}
# Implementation input guards, NOT clinical cutoffs or derivation-age limits.
INPUT_RANGES = {'age': (70, 89), 'sbp_mmhg': (70, 250), 'tc_mmol_l': (1, 15),
                'hdl_mmol_l': (0.2, 5), 'smoker': (0, 1), 'diabetes': (0, 1)}
MODIFIABLE = ('sbp_mmhg', 'tc_mmol_l', 'hdl_mmol_l', 'smoker')
