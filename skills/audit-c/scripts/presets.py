"""Bush 1998: Methods / Measures; Results and final Comment paragraph.

Response codes are local zero-based option indices. Points are printed values.
No grams-per-drink conversion was specified by this paper.
"""
POINTS = {"q1": (0, 1, 2, 3, 4, 4), "q2": (0, 0, 1, 2, 3, 4),
          "q3": (0, 1, 2, 3, 4)}
OPTIONS_ZH = {
    "q1": ("从不", "每月或更少", "每月2–4次", "每周2–3次", "每周4–5次", "每周至少6次"),
    "q2": ("0杯", "1–2杯", "3–4杯", "5–6杯", "7–9杯", "至少10杯"),
    "q3": ("从不", "不到每月一次", "每月", "每周", "每天或几乎每天"),
}
LABELS = {"q1": "过去一年饮酒频率", "q2": "过去一年饮酒日的典型杯数",
          "q3": "过去一年单次至少 6 杯的频率"}
MEASUREMENTS = {f"{q}_response_code": ("1", (0, len(options) - 1))
                for q, options in OPTIONS_ZH.items()}
CUTOFFS = (3, 4)
MAX_SCORE = 12
BOUNDARY = ("这是饮酒问题筛查，不是酒精使用障碍诊断，也不预测寿命或长期风险；"
            "原研究验证样本为男性退伍军人，不能把其筛查性能直接推广到女性或其他人群。"
            "不能据此开始、停止或调整药物。")
DRINK_NOTE = ("本文的“杯”沿用原问卷的饮品份数：一罐或一瓶啤酒、一杯葡萄酒、"
              "一份 wine cooler、一份鸡尾酒或一小杯烈酒。原文未规定统一乙醇克数，"
              "不能将任意大小的容器直接当作一杯，也不能凭空换算成克。")
