"""Cole et al., NEJM 1999, pp. 1352–1353; no fitted risk equation."""

TITLE = "运动后1分钟心率恢复"
MEASUREMENT_KEYS = ("peak_hr_bpm", "recovery_hr_1min_bpm")
ABNORMAL_CUTOFF_BPM = 12  # Table 1 header, p. 1353; Results, p. 1352.
RECOVERY_MINUTES = 1
COOLDOWN_MINUTES = 2  # Minimum duration, Recovery of Heart Rate, p. 1352.
TREADMILL_SPEED_KMH = 2.4  # Printed rounded equivalent of 1.5 mi/h, not a conversion factor.
TREADMILL_GRADE_PERCENT = 2.5
PROTOCOL = "cole-1999"
BOUNDARY = (
    "边界: 本结果仅按原研究的跑台主动恢复方案计算心率下降量与分档，"
    "不是个人死亡概率、寿命预测或疾病诊断；不能由此推断提高心率恢复值会降低死亡风险，"
    "不能据此开始、停止或调整药物。"
)


def classify(hrr_bpm):
    return "abnormal" if hrr_bpm <= ABNORMAL_CUTOFF_BPM else "normal"


def calculate(peak_hr_bpm, recovery_hr_1min_bpm):
    hrr = peak_hr_bpm - recovery_hr_1min_bpm
    return {"hrr_1min_bpm": hrr, "hrr_category": classify(hrr)}
