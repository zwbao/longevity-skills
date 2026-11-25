"""Zhou et al., Diabetes Care 36(12):3944–3952 (2013), Table 2.

Use the printed integer Score column, not re-rounded beta coefficients.
Intervals are lower-inclusive, upper-exclusive (Methods p. 3945).
"""
from math import inf

AGE_BINS = ((20, 0), (25, 4), (35, 8), (40, 11), (45, 12), (50, 13), (55, 15), (60, 16), (65, 18))
BMI_BINS = ((-inf, 0), (22, 1), (24, 3), (30, 5))
WAIST_BINS = {
    'male': ((-inf, 0), (75, 3), (80, 5), (85, 7), (90, 8), (95, 10)),
    'female': ((-inf, 0), (70, 3), (75, 5), (80, 7), (85, 8), (90, 10)),
}
SBP_BINS = ((-inf, 0), (110, 1), (120, 3), (130, 6), (140, 7), (150, 8), (160, 10))
BINARY_POINTS = {'sex': {0: 0, 1: 2}, 'family_history': {0: 0, 1: 6}}
CUTOFF = 25  # Results p. 3947; >=25, not >25.
SCORE_RANGE = (0, 51)
DERIVATION_AGES = (20, 74)
# Excluded extremes in Methods p. 3945; these are evidence limits, not input-error limits.
DERIVATION_RANGES = {'waist_cm': (56, 120), 'bmi_kg_m2': (15.23, 39.74), 'sbp_mmhg': (80, 205)}
# Engineering sanity limits, not clinical cutoffs or paper-derived coefficients.
INPUT_RANGES = {'age': (20, 74), 'sex': (0, 1), 'waist_cm': (40, 200),
                'bmi_kg_m2': (10, 70), 'sbp_mmhg': (60, 260),
                'family_history': (0, 1), 'known_diabetes': (0, 1)}
INPUT_UNITS = {'age': 'a', 'sex': '1', 'waist_cm': 'cm', 'bmi_kg_m2': 'kg/m^2',
               'sbp_mmhg': 'mmHg', 'family_history': '1', 'known_diabetes': '1'}
MODIFIABLE = ('waist_cm', 'bmi_kg_m2', 'sbp_mmhg')
BOUNDARY = ('本评分用于中国成人未诊断糖尿病的筛查分层，不是诊断，也不是个人三年发病概率；'
            '低于阈值不能排除糖尿病，目标情景的分数变化不代表干预效果，不能据此开始或停止药物。')
LEVER_NOTE = ('这是阶梯评分。敏感度是指定输入变化后的分差，不是连续导数；同一分档内变化可能为零。'
              '目标由使用者提供，不是健康目标建议；BMI、腰围与血压分别改变只是数学情景，不代表可独立干预。')
