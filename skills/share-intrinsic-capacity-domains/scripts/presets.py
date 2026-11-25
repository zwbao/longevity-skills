"""Frozen Table 1 scoring, Tzemah-Shahar et al., GeroScience (2026).

Source: https://link.springer.com/article/10.1007/s11357-026-02456-9/tables/1
All scoring constants are printed. The fluency input ceiling of 200 is solely
an input-error guard, not a published upper score limit or clinical threshold.
"""
RAW_MAX = {'cognition': 18, 'locomotion': 10, 'sensory': 10}
STANDARD_MAX = 10
DOMAIN_ZH = {'cognition': '认知', 'locomotion': '行动', 'sensory': '感官'}
FLUENCY_BINS = ((5, 0), (9, 1), (13, 2), (17, 3))
FLUENCY_TOP_SCORE = 4
RECALL_BINS = ((1, 0), (3, 1), (4, 2), (6, 3), (8, 4), (10, 5))
RATING_SCORES = {1: 2, 2: 2, 3: 1, 4: 1, 5: 0}
BINARY_SCORES = {0: 2, 1: 0}
INPUTS = {
    'orientation_correct_count': dict(group='cognition', label='时间定向正确数', unit='1', range=(0, 4), aliases=['orient_i', 'date orientation', '时间定向'], note='星期、日、月、年四题的正确数；不是年龄或日期数字。'),
    'animal_fluency_count': dict(group='cognition', label='动物命名正确词数', unit='1', range=(0, 200), aliases=['cf010_', 'semantic verbal fluency', '动物词语流畅性'], note='SHARE 语义流畅性测试的有效动物名称个数，不是已换算的分数；200 仅为录入防错上限。'),
    'serial_sevens_correct_count': dict(group='cognition', label='连续减七正确数', unit='1', range=(0, 5), aliases=['numeracy2', 'subtract 7', '连续减7'], note='SHARE 连续减七五次作答的正确数，不是最后算出的数。'),
    'delayed_recall_count': dict(group='cognition', label='延迟词表回忆正确词数', unit='1', range=(0, 10), aliases=['cf113tot', 'cf116tot', 'delayed word list recall', '延迟回忆'], note='SHARE 十词词表的延迟回忆正确数；cf113tot、cf116tot 是表 1 所列相应变量名，不相加，不用即时回忆替代。'),
    'stoop_difficulty_binary': dict(group='locomotion', label='弯腰跪蹲困难', unit='1', range=(0, 1), aliases=['ph048d6', 'difficulty stooping kneeling crouching'], note='有困难填 1，无困难填 0。'),
    'room_walk_difficulty_binary': dict(group='locomotion', label='穿过房间行走困难', unit='1', range=(0, 1), aliases=['ph049d2', 'difficulty walking across the room'], note='有困难填 1，无困难填 0。'),
    'walk_100m_difficulty_binary': dict(group='locomotion', label='步行一百米困难', unit='1', range=(0, 1), aliases=['ph048d1', 'difficulty walking 100 m'], note='有困难填 1，无困难填 0。'),
    'one_flight_difficulty_binary': dict(group='locomotion', label='爬一层楼梯困难', unit='1', range=(0, 1), aliases=['ph048d5', 'difficulty climbing one flight of stairs'], note='有困难填 1，无困难填 0。'),
    'several_flights_difficulty_binary': dict(group='locomotion', label='爬数层楼梯困难', unit='1', range=(0, 1), aliases=['ph048d4', 'difficulty climbing several flights of stairs'], note='有困难填 1，无困难填 0。'),
    'distance_vision_rating': dict(group='sensory', label='远距离视力自评分档', unit='1', range=(1, 5), aliases=['PH043_EyeSightDist', 'distance vision rating', '远视力自评'], note='SHARE 原有五级自评编码，1 为 excellent，5 为 poor；不是小数视力或眼科视力表数值。'),
    'reading_vision_rating': dict(group='sensory', label='阅读视力自评分档', unit='1', range=(1, 5), aliases=['PH044_EyeSightPap', 'reading vision rating', '阅读视力自评'], note='SHARE 原有五级自评编码，1 为 excellent，5 为 poor；不是小数视力。'),
    'hearing_rating': dict(group='sensory', label='听力自评分档', unit='1', range=(1, 5), aliases=['PH046_Hearing', 'hearing ability rating', '听力自评'], note='SHARE 原有五级自评编码，1 为 excellent，5 为 poor；不是听阈分贝。'),
    'glasses_use_binary': dict(group='sensory', label='是否使用眼镜', unit='1', range=(0, 1), aliases=['ph041', 'using glasses', '戴眼镜'], note='使用填 1，不使用填 0；计分不是停用眼镜的理由。'),
    'hearing_aid_use_binary': dict(group='sensory', label='是否使用助听器', unit='1', range=(0, 1), aliases=['ph045_', 'PH745_HaveHearingAid', 'using a hearing aid', '使用助听器'], note='使用填 1，不使用填 0；计分不是停用助听器的理由。'),
}
GROUP_KEYS = {group: tuple(k for k, spec in INPUTS.items() if spec['group'] == group) for group in RAW_MAX}
BINARY_KEYS = tuple(k for k in INPUTS if k.endswith('_binary'))
RATING_KEYS = tuple(k for k in INPUTS if k.endswith('_rating'))
BOUNDARY = ('这是 SHARE 人群研究中的探索性分域计分，不是 WHO 统一临床量表；不能据此诊断认知障碍、估计寿命或预测个人未来下降，也不能据此开始或停用药物、眼镜或助听器。未计算心理、活力分域和完整 IC 总分。')
