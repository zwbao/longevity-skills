"""Frozen points: Schonberg et al., J Gen Intern Med 2009, Table 2 / Appendix.
Risk lookup: Table 3, Validation, Point score (not annual person-year rate).
No coefficients were inferred, refit, or taken from a later index version.
"""
AGE_POINTS = ((65, 0), (70, 1), (75, 3), (80, 5), (85, 7))
BMI_CUTOFF = 25
BMI_LOW_POINTS = 2
CATEGORY_POINTS = {
    'male': (0, 3),
    'health_code': (0, 1, 2),
    'copd_history': (0, 2),
    'cancer_history': (0, 2),
    'diabetes_history': (0, 2),
    'iadl_help': (0, 2),
    'walking_difficulty': (0, 3),
    'smoking_code': (0, 1, 3),
}
HOSPITAL_POINTS = (0, 1, 3)  # 0, 1, >=2 overnight admissions in 12 months
# Inclusive lower score, printed label, validation mortality %, CI low, CI high.
RISK_ROWS = (
    (0, '0-1', 3, 1, 6), (2, '2-3', 5, 3, 8),
    (4, '4-5', 8, 6, 10), (6, '6-7', 12, 10, 15),
    (8, '8-9', 19, 16, 23), (10, '10-11', 29, 25, 33),
    (12, '12-13', 37, 32, 42), (14, '14-15', 49, 43, 55),
    (16, '16-17', 55, 48, 62), (18, '18+', 62, 54, 70),
)
INPUT_UNITS = {'age_years': 'a', 'bmi_kg_m2': 'kg/m^2',
               **{key: '1' for key in CATEGORY_POINTS if key != 'male'},
               'hospitalizations_count': '1'}
TARGET_KEYS = {'bmi_kg_m2', 'health_code', 'iadl_help', 'walking_difficulty',
               'smoking_code', 'hospitalizations_count'}
LABELS = {'age_years': '年龄', 'male': '性别', 'bmi_kg_m2': '体质指数',
          'health_code': '自评健康', 'copd_history': '肺气肿或慢性支气管炎史',
          'cancer_history': '癌症史', 'diabetes_history': '糖尿病史',
          'iadl_help': '日常事务需他人帮助', 'walking_difficulty': '步行四分之一英里困难',
          'smoking_code': '吸烟状态', 'hospitalizations_count': '过去一年过夜住院次数'}
CATEGORY_LABELS = {
    'health_code': ('极好或很好', '好', '一般或差'),
    'smoking_code': ('从未吸烟（终生少于100支）', '既往吸烟', '目前吸烟'),
    'male': ('女性', '男性'),
}
