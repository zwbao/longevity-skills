"""Guralnik et al., 1994, DOI 10.1093/geronj/49.2.m85.

Table A1/A2 footnotes (M94): inclusive bounds on recorded tenths of a second.
Table 1 (M87): inclusive integer-second standing-balance categories.
Input plausibility ranges in the manifest are engineering guards, not cutoffs.
"""
WALK_BANDS = ((0, 3.1, 4), (3.2, 4.0, 3), (4.1, 5.6, 2), (5.7, float('inf'), 1))
CHAIR_BANDS = ((0, 11.1, 4), (11.2, 13.6, 3), (13.7, 16.6, 2), (16.7, float('inf'), 1))
BALANCE_HOLD_S = 10
TANDEM_BANDS = ((0, 2, 2), (3, 9, 3), (10, 10, 4))
UNABLE_SCORE = 0
STUDY_MIN_AGE = 71
INPUT_UNITS = {
    'semi_tandem_s': 's', 'side_by_side_s': 's', 'full_tandem_s': 's',
    'walk_completed': '1', 'walk_8ft_trial1_s': 's', 'walk_8ft_trial2_s': 's',
    'chair_completed': '1', 'five_chair_stands_s': 's',
}
BALANCE_KEYS = ('semi_tandem_s', 'side_by_side_s', 'full_tandem_s')
STATUS_KEYS = ('walk_completed', 'chair_completed')
TIMED_TASKS = {
    'walk_completed': ('walk_8ft_trial1_s', 'walk_8ft_trial2_s'),
    'chair_completed': ('five_chair_stands_s',),
}
BOUNDARY = '本报告仅按 1994 年原版 8 英尺方案描述下肢体能，不诊断失能或衰弱，不预测你的死亡、入住养老机构或跌倒概率，不据此决定照护安置，也不能据此开始或停用药物。'
SCENARIO_NOTE = '目标情景只表示同一计分规则下的分数变化，不预测训练效果或风险下降。敏感度为记录精度的一步变化，不是连续导数；分数不变不等于功能没有变化。'
