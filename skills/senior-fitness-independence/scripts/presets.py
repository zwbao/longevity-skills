"""Rikli & Jones (2013), Table 4, p. 262: all 70 printed cut points.

Walking standards stay in the paper's yards here; SI conversion is exact,
not a refit or an interpolation of the published standards.
"""
YARD_TO_M = 0.9144
AGE_BANDS = ((60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89), (90, 94))
METRICS = (
    {'key': 'chair_stand_count', 'output': 'chair_stand', 'label': '30 秒椅子起立', 'unit': '1', 'direction': 1},
    {'key': 'arm_curl_count', 'output': 'arm_curl', 'label': '30 秒手臂弯举', 'unit': '1', 'direction': 1},
    {'key': 'walk_6min_m', 'output': 'walk_6min', 'label': '6 分钟步行', 'unit': 'm', 'direction': 1},
    {'key': 'step_2min_count', 'output': 'step_2min', 'label': '2 分钟原地踏步（右膝达标次数）', 'unit': '1', 'direction': 1},
    {'key': 'up_go_s', 'output': 'up_go', 'label': '8 英尺起立行走', 'unit': 's', 'direction': -1},
)
TABLE4 = {
    'female': {
        'chair_stand_count': (15, 15, 14, 13, 12, 11, 9),
        'arm_curl_count': (17, 17, 16, 15, 14, 13, 11),
        'walk_6min_m': (625, 605, 580, 550, 510, 460, 400),
        'step_2min_count': (97, 93, 89, 84, 78, 70, 60),
        'up_go_s': (5.0, 5.3, 5.6, 6.0, 6.5, 7.1, 8.0),
    },
    'male': {
        'chair_stand_count': (17, 16, 15, 14, 13, 11, 9),
        'arm_curl_count': (19, 18, 17, 16, 15, 13, 11),
        'walk_6min_m': (680, 650, 620, 580, 530, 470, 400),
        'step_2min_count': (106, 101, 95, 88, 80, 71, 60),
        'up_go_s': (4.8, 5.1, 5.5, 5.9, 6.4, 7.1, 8.0),
    },
}
TITLE = '老年体能与独立生活参考标准'
BOUNDARY = '本报告只比较标准化 SFT 测量与论文参考切点，不诊断失能，不预测你能否独立生活到 90 岁，也不估计寿命或给出运动、用药处方。'
