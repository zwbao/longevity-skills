"""Scoring: Heatherton et al. 1991, Table 3, p. 1125. No fitted constants."""

ITEM_KEYS = (
    'time_to_first_cigarette_min', 'difficulty_refraining',
    'morning_cigarette_hardest', 'cigarettes_per_day_count',
    'smoke_more_after_waking', 'smoke_when_ill_in_bed',
)
BINARY_KEYS = (
    'current_cigarette_smoker', 'difficulty_refraining',
    'morning_cigarette_hardest', 'smoke_more_after_waking', 'smoke_when_ill_in_bed',
)
INPUT_UNITS = {key: 'min' if key == ITEM_KEYS[0] else '1'
               for key in ('current_cigarette_smoker', *ITEM_KEYS)}
OUTPUT_KEYS = {key: f'q{i}_points' for i, key in enumerate(ITEM_KEYS, 1)}
# Inclusive upper bounds; None is the open final category. Table 3 is
# authoritative where introductory prose uses a loose '<5' notation.
TTF_POINTS = ((5, 3), (30, 2), (60, 1), (None, 0))
CPD_POINTS = ((10, 0), (20, 1), (30, 2), (None, 3))
BINARY_POINTS = {0: 0, 1: 1}
STUDY_AGE_RANGE = (17, 77)  # Methods, p. 1121; descriptive, not a fitted cutoff.
BOUNDARY = ('本结果仅按1991年FTND六题规则描述当前卷烟吸烟者的自报依赖表现；'
            '不能诊断疾病、推算个人戒烟成功率或寿命，也不能据此开始、停止或调整药物。')
SCENARIO_NOTE = ('回答变化只改变量表分数，不是治疗效果，也不是吸烟量或吸烟时间建议；'
                 '不得把不再吸烟者的答案全部置零来推算戒烟收益。')
