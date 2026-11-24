"""Wang et al., npj Aging 12:163 (2026), Methods IBI; Figures S3D/S4.

Use the printed raw CRP mg/L convention. No z-score, log transform or fitted
constants. See contract.md for the unresolved provenance of the threshold.
"""
IBI_THRESHOLD = 1.496
STUDY_MIN_AGE = 50
INPUT_UNITS = {
    'crp_mg_l': 'mg/L',
    'neutrophils_10e9_l': '10^9/L',
    'lymphocytes_10e9_l': '10^9/L',
}
STRATA_ZH = {'low': '低于论文探索切点', 'high': '达到或高于论文探索切点'}
TITLE = '炎症负荷指数（IBI）'
BOUNDARY = ('这是探索性炎症指标及论文切点的算术对照，不是衰弱诊断、衰老速度、'
            '个人患病概率或治疗目标；不能据此开始或停止药物，也不提供剂量。')
SCALE_NOTE = ('按论文明确写出的 CRP mg/L 原始公式与切点对照；论文回归分析另述标准化，'
              '缺少可核对的个体输入输出和公开分析源码，尚未独立核实切点推导尺度。'
              '分组仍在验证，不能作为正常值或干预目标。')
