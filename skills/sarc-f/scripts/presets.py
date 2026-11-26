"""Malmstrom et al. 2016, Methods: SARC-F questionnaire (0–10 points).

AAH/BLSA version only. All scoring constants are printed in that section.
Input upper bounds for count/age are software guards, not paper cutoffs.
"""

NO_POINTS = 0
SOME_POINTS = 1
SEVERE_POINTS = 2
FALLS_HIGH_THRESHOLD = 4
POSITIVE_THRESHOLD = 4
MAX_SCORE = 10
MEASUREMENTS = {
    "strength_response_score": ("score", (0, 2)),
    "walking_response_score": ("score", (0, 2)),
    "chair_response_score": ("score", (0, 2)),
    "stairs_response_score": ("score", (0, 2)),
    "falls_past_year_count": ("1", (0, 1000)),
}
COMPONENTS = {
    "strength": "提举或搬运10磅物品的困难",
    "walking": "走过一个房间的困难或辅助需求",
    "chair": "从椅子或床起身转移的困难或辅助需求",
    "stairs": "登上10级台阶的困难",
    "falls": "过去一年跌倒",
}
CATEGORY_ZH = {"screen_positive": "筛查阳性（达到症状风险切点）",
               "screen_negative": "筛查阴性（未达到症状风险切点）"}
BOUNDARY = (
    "SARC-F 是肌少症相关功能风险筛查问卷，不能单独确诊或排除肌少症，"
    "不能预测个人死亡概率、寿命或干预收益；本研究基于美国社区人群，其他人群的适用性需另行评估；"
    "不能据此开始、停止或调整药物。"
)
