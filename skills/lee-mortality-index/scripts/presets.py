"""Lee et al., JAMA 2006, Tables 3 and 4; corrected Box (Apr 26, 2006)."""

# Inclusive lower age cutoffs from Table 3; reference 50-59 from Methods.
AGE_POINTS = ((50, 0), (60, 1), (65, 2), (70, 3), (75, 4), (80, 5), (85, 7))
MALE_POINTS = 2
BMI_CUTOFF = 25
LOW_BMI_POINTS = 1
WEIGHTS = {
    'diabetes': 1,
    'cancer': 2,
    'lung_disease': 2,
    'heart_failure': 2,
    'current_smoker': 2,
    'bathing_difficulty': 2,
    'finances_difficulty': 2,
    'walking_difficulty': 2,
    'pushing_difficulty': 1,
}
# Table 4 validation cohort percentages, by point score 0..13 and >=14.
# Preserve rounding and the observed 45 -> 44 reversal; no smoothing.
VALIDATION_PERCENT = (1, 2, 2, 4, 6, 8, 9, 15, 20, 20, 28, 45, 44, 59, 64)
INPUT_UNITS = dict(age='a', sex='1', bmi_kg_m2='kg/m^2',
                   community_dwelling='1', **{key: '1' for key in WEIGHTS})
BINARY_KEYS = ('sex', 'community_dwelling', *WEIGHTS)
TARGET_KEYS = ('bmi_kg_m2', 'current_smoker', 'bathing_difficulty',
               'finances_difficulty', 'walking_difficulty', 'pushing_difficulty')
BOUNDARY = ('本结果是美国社区居住、50岁及以上人群的历史观察性风险分层，'
            '不是个人寿命预测，也未在当代中国人群或机构照护人群中验证；'
            '不能据此开始或停止药物、筛查或治疗。目标模拟只反映模型变化，'
            '不能解释为干预能减少的死亡风险，不能把BMI阈值当作增重目标。')
VALIDATION_NOTE = ('暂定验证：表3逐项计分和表4逐分风险已核对；正文78岁示例的'
                   '年龄得分与表3矛盾，完整示例尚未复现。')
