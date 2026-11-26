"""Kroenke et al. 2001: Methods p607, Table 2 p608, Appendix p613."""

ITEM_KEYS = tuple(f"phq9_q{i}_score" for i in range(1, 10))
ITEM_RANGE = (0, 3)
MAX_SCORE = 27
RESPONSE_ZH = ("完全没有", "有几天", "超过一半天数", "几乎每天")
ITEM_LABELS = (
    "做事缺乏兴趣或乐趣", "情绪低落、抑郁或绝望",
    "难以入睡、睡眠中断或睡得过多", "疲倦或缺乏精力",
    "食欲差或进食过量", "对自己失望、觉得失败或让自己或家人失望",
    "难以集中注意力", "别人可察觉的动作或说话迟缓，或比平常明显坐立不安",
    "觉得不如死去，或想到以某种方式伤害自己",
)
SEVERITY_BANDS = (
    (0, 4, "minimal", "极少"), (5, 9, "mild", "轻度"),
    (10, 14, "moderate", "中度"),
    (15, 19, "moderately_severe", "中重度"), (20, 27, "severe", "重度"),
)
CATEGORY_ZH = {category: label for _, _, category, label in SEVERITY_BANDS}
BOUNDARY = (
    "PHQ-9 反映过去两周的抑郁症状严重度，不能单独确诊或排除抑郁症，"
    "也不能判断自杀风险等级、推算个人寿命或衰老速度；"
    "本研究为成人门诊人群的横断面验证；不能据此开始、停止或调整药物。"
)
# Product safety response, not a risk prediction or treatment rule from the paper.
SUPPORT_LINES = [
    "## 先关注安全与支持", "",
    "第九题的回答提示过去两周出现过死亡或自伤相关想法。无论总分多少，"
    "请尽快联系心理或精神卫生专业人员，并让可信任的人知道你的处境。",
    "如果现在有伤害自己的打算、已采取行动，或无法保证自身安全，"
    "请立即联系当地急救服务或前往急诊，请可信任的人陪伴，避免独处。",
    "这一个回答不能判断是否存在即时危险，需要进一步直接了解你现在的安全状况。", "",
]
