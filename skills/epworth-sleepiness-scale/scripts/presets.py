"""Johns 1991: Table 1 and Development of the ESS, p. 541.

No later ESS interpretation bands or regression predictions are used.
Chinese/English item labels are data-field identifiers, not a validated
translation or a replacement questionnaire.
"""

ITEM_UNIT = "score"
ITEM_RANGE = (0, 3)
MAX_TOTAL = 24
ITEM_KEYS = tuple(f"ess_item_{i}_score" for i in range(1, 9))
ITEM_LABELS = (
    "第1项：坐着阅读", "第2项：看电视", "第3项：公共场所静坐",
    "第4项：连续乘车一小时", "第5项：下午躺下休息", "第6项：坐着交谈",
    "第7项：无酒午餐后静坐", "第8项：车在路上短暂停驶",
)
RESPONSE_LABELS = {0: "不会打瞌睡", 1: "打瞌睡可能性小", 2: "打瞌睡可能性中等", 3: "打瞌睡可能性大"}
PATIENT_AGE_RANGE = (18, 78)
BOUNDARY = "ESS 衡量近期通常生活中的自报日间入睡倾向，不是诊断；不能据此判断特定睡眠疾病、驾驶安全、衰老速度或个人寿命，也不据此开始、停用或调整药物。"
