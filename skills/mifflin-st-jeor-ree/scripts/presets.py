"""Mifflin et al., AJCN 1990;51:241–247, Eqs 3, 7, 8 and Table 1."""
TITLE = 'Mifflin–St Jeor 静息能量消耗'
INPUT_UNITS = {'weight_kg': 'kg', 'height_cm': 'cm', 'age': 'a', 'sex': ''}
# Eq 3, p. 244; Eqs 7 and 8, p. 246. Sex: male=1, female=0.
COEFFICIENTS = {
    'ree_original_kcal_d': {'weight_kg': 9.99, 'height_cm': 6.25, 'age': -4.92, 'sex': 166, 'intercept': -161},
    'ree_simplified_kcal_d': {'weight_kg': 10, 'height_cm': 6.25, 'age': -5, 'sex': 166, 'intercept': -161},
}
# Table 1 ranges; male age upper bound follows Subjects text p. 242 (78),
# not Table 1's inconsistent male row (76). Overall Table 1 also says 78.
STUDY_RANGES = {
    'male': {'weight_kg': (58, 143), 'height_cm': (160, 201), 'age': (19, 78)},
    'female': {'weight_kg': (46, 120), 'height_cm': (146, 186), 'age': (20, 76)},
}
BOUNDARY = ('本结果是健康成人静息能量消耗的统计估计，不是实测值、每日总能量消耗或饮食热量处方；'
            '不能用于判断代谢疾病、减重效果或寿命，也不能据此开始或停止药物。')
TARGET_NOTE = ('体重情景只表示在身高、年龄和性别不变时重新代入方程的结果，'
               '不是减重建议，也不预测减重后的代谢适应；数值更低不等于更健康。')
