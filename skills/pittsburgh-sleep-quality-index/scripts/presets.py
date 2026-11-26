"""Buysse et al. 1989, Appendix pp. 211–213; Fig. 2 p. 202.

All clinical scoring constants are transcribed here. No endpoint repairs.
"""
BOUNDARY = '边界: 本结果只描述过去一个月的自评睡眠质量，不能诊断失眠或其他疾病，不能换算生物年龄、寿命或死亡风险；不能据此开始、调整或停止药物。'
# p.211 Q2 and pair-sum tables; p.212 disturbance-sum table.
LATENCY_BANDS = ((0, 15, 0), (16, 30, 1), (31, 60, 2), (61, None, 3))
PAIR_BANDS = ((0, 0, 0), (1, 2, 1), (3, 4, 2), (5, 6, 3))
DISTURBANCE_BANDS = ((0, 0, 0), (1, 9, 1), (10, 18, 2), (19, 27, 3))
# lo, hi, inclusive_lo, inclusive_hi, score; preserve overlapping rows.
DURATION_BANDS = ((7, None, False, False, 0), (6, 7, True, True, 1),
                  (5, 6, True, True, 2), (0, 5, True, False, 3))
EFFICIENCY_BANDS = ((85, 100, False, True, 0), (75, 84, True, True, 1),
                    (65, 74, True, True, 2), (0, 65, True, False, 3))
CUTOFF = 5
MAX_SCORE = 21
COMPONENT_LABELS = ('主观睡眠质量', '入睡潜伏期', '睡眠时长', '习惯性睡眠效率',
                    '睡眠障碍', '助眠药使用频度', '日间功能障碍')
CATEGORY_ZH = {'above_cutoff': '超过论文切点，提示自评睡眠质量较差',
               'not_above_cutoff': '未超过论文切点；不等于排除睡眠疾病'}
CODE_KEYS = tuple(f'q5{letter}_code' for letter in 'abcdefghij') + tuple(f'q{n}_code' for n in (6, 7, 8, 9))
DISTURBANCE_KEYS = tuple(f'q5{letter}_code' for letter in 'bcdefghij')
INTEGER_KEYS = CODE_KEYS + ('bedtime_min', 'rise_time_min', 'sleep_latency_min')
# Technical input guards, not paper-derived clinical reference intervals.
MEASUREMENTS = {'bedtime_min': ('min', (0, 1439)), 'rise_time_min': ('min', (0, 1439)),
                'sleep_latency_min': ('min', (0, 1440)), 'sleep_duration_h': ('h', (0, 24)),
                **{key: ('score', (0, 3)) for key in CODE_KEYS}}
MINUTES_PER_HOUR = 60
MINUTES_PER_DAY = 1440
PERCENT_FACTOR = 100
STUDY_AGE_RANGE = (19, 83)  # p.195, combined observed age ranges
