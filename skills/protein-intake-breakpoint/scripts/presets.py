"""Morton et al., BJSM 2018: Figure 5 and Break point analysis; no fitted constants."""
BREAKPOINT = 1.62
BREAKPOINT_CI = (1.03, 2.20)
MODEL_P = 0.079
# Discussion, Muscle mass: intake range of the 42 arms in the breakpoint analysis.
OBSERVED_INTAKE = (0.9, 2.4)
MEASUREMENTS = (
    ('protein_g_day', '每日总蛋白质', 'g/d'),
    ('weight_kg', '体重', 'kg'),
)
BOUNDARY = '仅将记录的总蛋白摄入与健康、非能量限制且持续抗阻训练成人研究中的组水平拐点比较；不是个人蛋白需要量、安全上限、增肌预测或补剂剂量建议，不能据此开始或停止药物。'
SCENARIO_NOTE = '情景值由用户提供，只改变摄入量除以体重的算术结果；不代表改变体重或摄入量的建议，也不预测肌肉、力量或寿命变化。'
