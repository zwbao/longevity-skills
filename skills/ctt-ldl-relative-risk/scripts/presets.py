"""CTT Collaboration 2010: printed constants and explicit product scope."""
# Main text, Summary Findings / Figure 1 overall, and Discussion.
RR_PER_MMOL = 0.78
RR_CI95 = (0.76, 0.80)
# Webtable 1 footnote (PDF page 3): reverse of mmol/L / 0.02586.
MG_DL_TO_MMOL_L = 0.02586
INPUT_KEY = 'ldl_reduction_mmol_l'
INPUT_UNIT = 'mmol/L'
# Product scope: no inverse extrapolation; ceiling is the largest Discussion example.
# These are not clinical thresholds or a claim that all changes <=3 were trial arms.
REDUCTION_RANGE = (0.0, 3.0)
TITLE = 'LDL-C 降幅与主要血管事件相对发生率'
BOUNDARY = ('这是他汀随机试验人群平均效应的数学换算，不是个人绝对风险、寿命或净获益预测；'
            '不能据此开始或停止用药，也不能据此调整剂量。')
