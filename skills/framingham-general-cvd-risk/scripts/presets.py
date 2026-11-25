"""Published constants, no fitted or reconstructed coefficients.

Lipid model: Table 2 + Appendix, Circulation 2008;117:743–753.
BMI model: FHS official Cardiovascular Disease (10-year risk) webpage,
Simple Office-based non-laboratory Predictors table and its footnote.
Normal reference: paper p.751; official workbook Sheet3 (BMI 22.5).
"""
MEASUREMENT_UNITS = {'sbp_mmhg': 'mmHg', 'tc_mg_dl': 'mg/dL',
                     'hdl_mg_dl': 'mg/dL', 'bmi_kg_m2': 'kg/m^2'}
MODEL_KEYS = {'lipids': ('sbp_mmhg', 'tc_mg_dl', 'hdl_mg_dl'),
              'bmi': ('sbp_mmhg', 'bmi_kg_m2')}
COEFFICIENTS = {
    'lipids': {
        'male': {'age': 3.06117, 'tc_mg_dl': 1.12370, 'hdl_mg_dl': -0.93263,
                 'sbp_untreated': 1.93303, 'sbp_treated': 1.99881,
                 'smoker': 0.65451, 'diabetes': 0.57367, 'mean': 23.9802, 's10': 0.88936},
        'female': {'age': 2.32888, 'tc_mg_dl': 1.20904, 'hdl_mg_dl': -0.70833,
                   'sbp_untreated': 2.76157, 'sbp_treated': 2.82263,
                   'smoker': 0.52873, 'diabetes': 0.69154, 'mean': 26.1931, 's10': 0.95012},
    },
    'bmi': {
        'male': {'age': 3.11296, 'bmi_kg_m2': 0.79277,
                 'sbp_untreated': 1.85508, 'sbp_treated': 1.92672,
                 'smoker': 0.70953, 'diabetes': 0.53160, 'mean': 23.9388, 's10': 0.88431},
        'female': {'age': 2.72107, 'bmi_kg_m2': 0.51125,
                   'sbp_untreated': 2.81291, 'sbp_treated': 2.88267,
                   'smoker': 0.61868, 'diabetes': 0.77763, 'mean': 26.0145, 's10': 0.94833},
    },
}
NORMAL = {'sbp_mmhg': 125, 'tc_mg_dl': 180, 'hdl_mg_dl': 45, 'bmi_kg_m2': 22.5}
DERIVATION_AGES = (30, 74)
BOUNDARY = ('这是历史美国队列的首次总体心血管事件风险估计，不是诊断、个人命运或干预效果预测；'
            '心脏年龄只是风险的等价表达，不是实测器官年龄。不能据此开始、停止或调整药物。')
