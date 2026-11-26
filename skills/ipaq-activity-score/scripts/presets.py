"""Craig et al. 2003, Table 1 p.1382 and Appendix B pp.1391–1395.

Only the short-form pace-specific branch is implemented. No constants from
later IPAQ scoring protocols are imported.
"""
TITLE = "IPAQ 短表活动量：按步行速度计分"
BOUNDARY = "这是自报活动量的加权汇总，不是实际热量消耗、健康达标判断、疾病风险或寿命预测；目标情景只是算术比较，不能据此开始或停止用药。"
ACTIVITIES = ("walking", "moderate", "vigorous")
LABELS = {"walking": "步行", "moderate": "中等强度活动（不含步行）", "vigorous": "高强度活动"}
METS = {"vigorous": 8, "moderate": 4}
WALKING_METS = {"vigorous": 5, "moderate": 3.3, "slow": 2.5}
PACE_LABELS = {"vigorous": "快／高强度", "moderate": "中等", "slow": "慢"}
MIN_BOUT_MIN = 10
MAX_DAILY_MIN = 960
MAX_DAYS = 7
AGE_RANGE = (18, 65)  # Main Methods and Conclusions, not Appendix B's 15–69 label.
INPUT_RULES = {
    **{f"{a}_days": ("d", (0, MAX_DAYS)) for a in ACTIVITIES},
    **{f"{a}_min": ("min", (0, MAX_DAILY_MIN)) for a in ACTIVITIES},
    "sitting_weekday_min": ("min", (0, MAX_DAILY_MIN)),
    "age": ("a", AGE_RANGE),
}
