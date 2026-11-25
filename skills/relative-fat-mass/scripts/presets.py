"""Final published RFM, Woolcott & Bergman, Scientific Reports 2018.

Sources: main-text Eqs. (1–3), Supplementary Table 5 footnote, p.30.
The raw regressions in Supplementary Table 7 are NOT the final RFM.
"""
INTERCEPT = 64
RATIO_COEFFICIENT = -20
SEX_COEFFICIENT = 12
SEX_CODES = {'male': 0, 'm': 0, '男': 0, '0': 0,
             'female': 1, 'f': 1, '女': 1, '1': 1}
INPUT_UNITS = {'height_cm': 'cm', 'waist_cm': 'cm', 'age': 'a', 'sex': '1'}
DEVELOPMENT_AGE = (20, 85)
VALIDATION_AGE = (20, 69)
# Supplementary Methods excludes height >6 feet 5 inches for DXA eligibility.
DXA_HEIGHT_LIMIT_CM = (6 * 12 + 5) * 2.54
TITLE = 'RFM 全身体脂率估计'
BOUNDARY = ('RFM 是横断面人群公式的体脂率估计，不是 DXA 实测或肥胖诊断；'
            '不能据此推断个人寿命、减脂效果或决定开始、停止药物。')
TARGET_NOTE = ('目标情景只把你给出的腰围代入同一公式，保持身高、年龄及性别不变；'
               '变化以百分点表示，不代表实际体脂会同幅改变，也不是推荐目标。')
