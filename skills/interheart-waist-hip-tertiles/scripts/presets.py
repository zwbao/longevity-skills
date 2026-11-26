"""Yusuf et al., Lancet 2004: Methods p 939 and Table 3 p 941."""
from decimal import Decimal

TITLE = "INTERHEART 腰臀比分组"
INPUT_UNITS = {"waist_cm": "cm", "hip_cm": "cm"}
CUTPOINTS = {
    "male": (Decimal("0.90"), Decimal("0.95")),
    "female": (Decimal("0.83"), Decimal("0.90")),
}
# Table 3, Adjusted for all: OR and 99% CI relative to tertile 1.
ASSOCIATIONS = {2: (1.12, 1.01, 1.25), 3: (1.62, 1.45, 1.80)}
BOUNDARY = "本报告只计算腰臀比、研究分组及对应的人群关联，不是肥胖诊断或个人心梗概率，也不能预测改变腰臀围后的获益；不能据此开始、停用或调整药物。"
SCENARIO_NOTE = "目标由你提供，只展示算术情景和分组变化，不是推荐目标，也不是干预效果或因果获益预测；臀围变化不等同于脂肪变化。"
BOUNDARY_NOTE = "原文只列切点，未说明等于切点时的归属；边界处保留腰臀比，不指定三分位组或比值比。"
