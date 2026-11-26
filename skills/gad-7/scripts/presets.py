"""Spitzer et al. 2006: Figure 1, Table 3 and Comment; no fitted constants."""

ITEMS = {
    "gad7_item_1_score": "感到紧张、焦虑或坐立不安",
    "gad7_item_2_score": "无法停止或控制担忧",
    "gad7_item_3_score": "对各种事情担忧过多",
    "gad7_item_4_score": "难以放松",
    "gad7_item_5_score": "烦躁不安，难以静坐",
    "gad7_item_6_score": "容易烦恼或易怒",
    "gad7_item_7_score": "感到害怕，仿佛会有可怕的事情发生",
}
# Figure 1 p1094. Numeric answers are already the printed item scores.
RESPONSE_ZH = {0: "完全没有", 1: "有几天", 2: "超过一半的天数", 3: "几乎每天"}
MEASUREMENTS = {key: ("score", (0, 3)) for key in ITEMS}
TOTAL_RANGE = (0, 21)  # Item selection, p1093.
# Table 3 p1096 and Comment p1095. Table 2's '5-21' severe row is inconsistent.
SEVERITY_BANDS = ((0, 4, "minimal"), (5, 9, "mild"),
                  (10, 14, "moderate"), (15, 21, "severe"))
SEVERITY_ZH = {"minimal": "极轻微", "mild": "轻度", "moderate": "中度", "severe": "重度"}
SCREENING_CUTOFF = 10  # Table 1 footnote: greater than or equal to the score.
STUDY_AGE_RANGE = (18, 95)  # Description of patients, p1093.
BOUNDARY = (
    "GAD-7 只用于焦虑症状筛查和程度分档，不能单独确诊或排除广泛性焦虑障碍，"
    "也不估计个人患病概率、生物年龄或寿命；本研究验证对象为美国基层医疗成年患者，"
    "中文题干为解释性翻译，其他语言和人群的适用性需另行核对；不能据此开始、停止或调整药物。"
)
