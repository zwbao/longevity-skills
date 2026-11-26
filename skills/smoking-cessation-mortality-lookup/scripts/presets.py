"""Doll et al. 2004, Table 5 and Figure 4 accompanying text. No fitted constants."""
TITLE = "吸烟史与死亡率：历史男性队列查表"
BOUNDARY = (
    "本结果仅为1900–1930年出生、1951–2001年随访的英国男性医生队列参考，"
    "不是你的死亡概率、剩余寿命或个人戒烟获益预测；不适用于女性或其他烟草使用模式，"
    "不能据此开始或停止任何药物。"
)
INPUT_SPECS = {
    "smoking_history_code": ("1", (0, 3)),
    "quit_age_years": ("a", (0, 120)),
    "age": ("a", (35, 85)),
}
HISTORY_LABELS = {0: "终生不吸烟", 1: "持续仅吸卷烟", 2: "曾持续仅吸卷烟，现已戒烟"}
AGE_STARTS = (35, 45, 55, 65, 75)
QUIT_STARTS = (25, 35, 45, 55)
# Table 5 column order: never, quit 35-44, quit 45-54, quit 55-64, continuing.
# Each populated cell is (annual deaths per 1000 men, observed deaths).
TABLE_5 = {
    35: ((1.6, 55), None, None, None, (2.7, 150)),
    45: ((3.8, 145), (5.4, 95), None, None, (8.5, 487)),
    55: ((8.4, 290), (9.0, 132), (16.4, 229), None, (21.4, 703)),
    65: ((18.6, 528), (22.7, 262), (31.7, 331), (36.4, 250), (50.7, 722)),
    75: ((51.7, 666), (53.1, 316), (69.1, 370), (78.9, 299), (112.2, 453)),
}
# Printed ratios must NOT be recalculated from the rounded rate cells.
PRINTED_RATIOS = {35: 1.6, 45: 2.3, 55: 2.5, 65: 2.7, 75: 2.2}
# Figure 4 caption defines cessation bands; accompanying text / Discussion
# gives approximate lifetime gains versus continued smoking (not remaining life).
FIGURE_4_GAINS = {25: 10, 35: 9, 45: 6, 55: 3}


def band_start(age, starts):
    return next((low for low in starts if low <= age < low + 10), None)


def band_label(low):
    return f"{low}-{low + 9}"
