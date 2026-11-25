"""Frozen from updated Supplementary Methods Tables 2–4, DOI ehab309."""
# Order: age, smoking, SBP, TC, HDL, age*smoking, age*SBP, age*TC, age*HDL.
COEFFICIENTS = {
    'male': (0.3742, 0.6012, 0.2777, 0.1458, -0.2698, -0.0755, -0.0255, -0.0281, 0.0426),
    'female': (0.4648, 0.7744, 0.3131, 0.1002, -0.2606, -0.1088, -0.0277, -0.0226, 0.0613),
}
BASE_SURVIVAL = {'male': 0.9605, 'female': 0.9776}
SCALES = {
    'low': {'male': (-0.5699, 0.7476), 'female': (-0.7380, 0.7019)},
    'moderate': {'male': (-0.1565, 0.8009), 'female': (-0.3143, 0.7701)},
    'high': {'male': (0.3207, 0.9360), 'female': (0.5710, 0.9369)},
    'very_high': {'male': (0.5836, 0.8294), 'female': (0.9412, 0.8329)},
}
# Table 2 centring and scaling, in age, SBP, TC, HDL order.
CENTRES = (60, 120, 6, 1.3)
DIVISORS = (5, 20, 1, 0.5)
AGE_RANGE = (40, 69)
INPUT_UNITS = {'sbp_mmhg': 'mmHg', 'tc_mmol_l': 'mmol/L', 'hdl_mmol_l': 'mmol/L', 'smoker': '1', 'age': 'a'}
# Engineering input bounds, NOT diagnostic cutoffs or the ranges of the printed chart.
RANGES = {'sbp_mmhg': (70, 250), 'tc_mmol_l': (1, 15), 'hdl_mmol_l': (0.2, 5), 'smoker': (0, 1), 'age': AGE_RANGE}
REGION_ZH = {'low': '低风险地区', 'moderate': '中等风险地区', 'high': '高风险地区', 'very_high': '极高风险地区'}
BOUNDARY = '边界：仅适用于欧洲风险地区、40–69 岁、无既往心血管病且无糖尿病的人；这是首次致死或非致死心血管事件的十年模型估计，不是诊断或个人寿命预测；目标情景不代表干预效果，不能据此开始或停止药物。'
