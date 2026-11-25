"""Buysse 2014, Figure S1, p. 17B. Original five-item SATED only."""
ITEMS = (
    ("satisfaction_score", "睡眠满意度", "score"),
    ("alertness_score", "白天清醒度", "score"),
    ("timing_score", "睡眠时间安排", "score"),
    ("efficiency_score", "睡眠效率", "score"),
    ("duration_score", "睡眠时长", "score"),
)
RESPONSE_SCORES = {"Rarely/Never": 0, "Sometimes": 1, "Usually/Always": 2}
RESPONSE_ZH = {0: "很少／从不", 1: "有时", 2: "通常／总是"}
QUESTIONS_ZH = (
    "你对自己的睡眠感到满意吗？",
    "你能整天保持清醒而不打瞌睡吗？",
    "凌晨 2:00 至 4:00 之间，你在睡觉或尝试入睡吗？",
    "你夜间清醒的总时间少于 30 分钟吗（包括入睡所需时间和睡后醒来的时间）？",
    "你每天睡眠在 6 至 8 小时之间吗？",
)
BOUNDARY = "这是 Buysse 2014 提出的原始五项 SATED 自评计分，原论文中尚未经过心理测量学验证；分值不是睡眠障碍诊断、疾病概率或寿命预测，不能据此开始或停止药物。原题面针对成人典型夜间单段睡眠，不直接推广至儿童、轮班或其他睡眠文化。"


def response_score(response):
    return RESPONSE_SCORES[response]


def score_answers(values):
    scores = {}
    labels = {value: label for label, value in RESPONSE_SCORES.items()}
    for key, _, _ in ITEMS:
        value = values[key]
        if value not in labels:
            raise ValueError("回答只能是 0、1 或 2。")
        scores[key] = response_score(labels[value])
    scores["sated_total_score"] = sum(scores.values())
    return scores
