"""Goff et al., JACC 2014, Table A (Appendix 4); Full Work Group Table 4.

All model constants are the printed constants, without fitting or derivation.
N/A terms are absent, not estimated. Natural logarithms, lipids mg/dL, BP mmHg.
"""
COEFFICIENTS = {
    ('female', 'white'): dict(ln_age=-29.799, ln_age_squared=4.884,
        ln_tc=13.540, ln_age_tc=-3.114, ln_hdl=-13.578, ln_age_hdl=3.149,
        ln_sbp_treated=2.019, ln_sbp_untreated=1.957, smoker=7.574,
        ln_age_smoker=-1.665, diabetes=0.661),
    ('female', 'african_american'): dict(ln_age=17.114, ln_tc=0.940,
        ln_hdl=-18.920, ln_age_hdl=4.475, ln_sbp_treated=29.291,
        ln_age_sbp_treated=-6.432, ln_sbp_untreated=27.820,
        ln_age_sbp_untreated=-6.087, smoker=0.691, diabetes=0.874),
    ('male', 'white'): dict(ln_age=12.344, ln_tc=11.853, ln_age_tc=-2.664,
        ln_hdl=-7.990, ln_age_hdl=1.769, ln_sbp_treated=1.797,
        ln_sbp_untreated=1.764, smoker=7.837, ln_age_smoker=-1.795, diabetes=0.658),
    ('male', 'african_american'): dict(ln_age=2.469, ln_tc=0.302,
        ln_hdl=-0.307, ln_sbp_treated=1.916, ln_sbp_untreated=1.809,
        smoker=0.549, diabetes=0.645),
}
# Table A: Mean (Coefficient x Value), Baseline Survival.
BASELINES = {
    ('female', 'white'): (-29.18, 0.9665),
    ('female', 'african_american'): (86.61, 0.9533),
    ('male', 'white'): (61.18, 0.9144),
    ('male', 'african_american'): (19.54, 0.8954),
}
# Companion Omnibus_Risk_Estimator.xls, Omnibus D6:D8 (operational acceptance).
MEASUREMENTS = {'tc_mg_dl': ('mg/dL', (130, 320)),
                'hdl_mg_dl': ('mg/dL', (20, 100)),
                'sbp_mmhg': ('mmHg', (90, 200))}
FLAGS = ('treated', 'smoker', 'diabetes')
AGES = (40, 79)  # Article Appendix 4; workbook 10-Year ASCVD sheet.
DISPLAY_LIMITS = (1, 30)  # Article section 5; supplement Tables 8–11.
# Unit convention, not a fitted model parameter: repository cholesterol molar mass
# (skills/china-par-ascvd-risk/skill.json) 386.65 g/mol / 10 = mg/dL per mmol/L.
MMOL_TO_MG_DL = 386.65 / 10
TARGET_KEYS = frozenset((*MEASUREMENTS, 'smoker'))
BOUNDARY = ('PCE 是原始美国队列的十年首次动脉粥样硬化性心血管病风险模型估计，不是诊断，'
            '不代表中国人群已校准的风险；目标值情景不是治疗效果预测，不能据此开始、停止或调整药物。')
SCENARIO_NOTE = ('只替换输入并重算同一方程，变化单位为百分点。血压治疗和糖尿病状态保持不变；'
                 '不把系数方向当作干预建议，不预测戒烟后的时间进程或治疗获益。')
