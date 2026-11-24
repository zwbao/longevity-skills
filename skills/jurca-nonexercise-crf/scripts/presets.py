"""Jurca et al., AJPM 2005, Table 5 NASA column and Figure 1 (pp.189–190)."""
INPUT_UNITS = {'age': 'a', 'sex': '1', 'bmi_kg_m2': 'kg/m^2',
               'resting_hr_bpm': '/min', 'activity_level': 'score'}
INTERCEPT = 18.07
COEFFICIENTS = {'sex': 2.77, 'age': -0.10, 'bmi_kg_m2': -0.17, 'resting_hr_bpm': -0.03}
ACTIVITY_SCORES = {1: 0.00, 2: 0.32, 3: 1.06, 4: 1.76, 5: 3.03}
# Figure 1, Step 1: use this worksheet wording, not the original 0–7 NASA scale.
ACTIVITY_LABELS = {
    1: '除日常生活活动外，很少活动或不活动。',
    2: '每周至少5天做低强度活动，每次至少10分钟，呼吸和心率略增。',
    3: '快走、慢跑、骑车、游泳或相近强度有氧活动，每周20–60分钟。',
    4: '快走、慢跑或相近强度有氧活动，每周1–3小时。',
    5: '快走、慢跑或相近强度有氧活动，每周超过3小时。',
}
MODIFIABLE = ('bmi_kg_m2', 'resting_hr_bpm', 'activity_level')
BOUNDARY = '这是非运动测试回归模型的心肺适能估计，不等于实测心肺适能，不用于诊断、寿命或死亡风险预测；目标情景只是公式变化，不能证明个人干预效果，也不能据此开始或停止药物。'
VALIDATION_NOTE = '本实现暂定：论文正文示例印为9.02 MET，但表5和图1的公开系数不能复现该值；保留公开系数，未拟合或修正常数。'
SCENARIO_NOTE = '目标由用户提供，不推荐目标值。横断面模型没有验证个体变化；降低心率或BMI在公式中的变化不等于改善健康，活动等级也不是等距分数。'
