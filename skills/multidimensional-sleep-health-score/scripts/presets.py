"""Constants of the six-domain sleep health score, copied from the paper.

Source: Marent et al., GeroScience 2026, doi:10.1007/s11357-026-02518-y,
Methods, "Multidimensional sleep health score". Every number below is printed
in that paragraph; nothing here is fitted or taken from another paper.

  "Favourable device-measured domains were defined as follows: sleep duration
  of 6–8 h per night, sleep efficiency ≥ 85%, sleep timing with sleep midpoint
  between 02:00 and 04:00, and sleep regularity based on night-to-night
  variability in sleep midpoint < 60 min."

  PSQI "how would you rate your sleep quality overall?": very good or fairly
  good = favourable. PSQI "trouble staying awake while driving, eating meals,
  or engaging in social activity": not during the past month or less than once
  a week = favourable. "Domain scores were summed to yield a total score
  ranging from 0 to 6".

Operational choices the paper does not fix (written in references/contract.md):
both ends of 6–8 h and 02:00–04:00 count as favourable; a midpoint written
past 24 (GGIR writes hours from midnight of the evening the night began, so
27.5 is 03:30) is folded back with modulo 24.
"""

TITLE = "六维睡眠健康评分（0–6 分）"

DURATION_LOW_H = 6.0
DURATION_HIGH_H = 8.0
EFFICIENCY_MIN_PCT = 85.0
MIDPOINT_EARLIEST_H = 2.0
MIDPOINT_LATEST_H = 4.0
MIDPOINT_SD_BELOW_MIN = 60.0

# PSQI answer codes as on the standard PSQI form (0 = best answer, 3 = worst),
# in the order the paper lists the answers.
QUALITY_ANSWERS = ("very good 非常好", "fairly good 尚好", "fairly bad 不好", "very bad 非常差")
ALERTNESS_ANSWERS = ("not during the past month 过去一个月没有", "less than once a week 每周少于 1 次",
                     "once or twice a week 每周 1–2 次", "three or more times a week 每周 3 次或以上")
FAVOURABLE_MAX_CODE = 1  # codes 0 and 1 are favourable for both PSQI items

SCORE_MAX = 6
COHORT_MEDIAN_SCORE = 5  # Results: "multidimensional sleep health score was 5 (IQR 4–6)" at baseline
COHORT_IQR_SCORE = (4, 6)

DOMAINS = (
    # key of the output flag, input key, Chinese name, favourable rule in words
    ("duration_favourable", "sleep_duration_h", "睡眠时长", "每晚 6–8 小时"),
    ("efficiency_favourable", "sleep_efficiency_pct", "睡眠效率", "≥ 85%"),
    ("timing_favourable", "sleep_midpoint_clock_h", "睡眠时点", "睡眠中点在 02:00–04:00"),
    ("regularity_favourable", "sleep_midpoint_sd_min", "睡眠规律", "各晚睡眠中点的标准差 < 60 分钟"),
    ("satisfaction_favourable", "psqi_sleep_quality_code", "主观睡眠满意度", "PSQI 总体睡眠质量答「非常好」或「尚好」"),
    ("alertness_favourable", "psqi_trouble_awake_code", "白天清醒度", "PSQI 白天犯困题答「过去一个月没有」或「每周少于 1 次」"),
)

BOUNDARY = (
    "这是论文的六维睡眠健康计分（每项有利记 1 分，合计 0–6 分），只描述你交来的这一周睡眠；"
    "论文在 55 岁及以上比利时社区成人里没有发现这个总分与记忆、执行功能或处理速度相关，"
    "所以分数不是认知或痴呆风险的预测，也不是诊断。报告不建议开始或停用任何药物或助眠产品；"
    "长期失眠、打鼾憋醒或白天嗜睡请找医生。"
)


def midpoint_clock(value_h: float) -> float:
    return value_h % 24.0


def favourable(domain_key: str, value: float) -> bool:
    if domain_key == "duration_favourable":
        return DURATION_LOW_H <= value <= DURATION_HIGH_H
    if domain_key == "efficiency_favourable":
        return value >= EFFICIENCY_MIN_PCT
    if domain_key == "timing_favourable":
        return MIDPOINT_EARLIEST_H <= midpoint_clock(value) <= MIDPOINT_LATEST_H
    if domain_key == "regularity_favourable":
        return value < MIDPOINT_SD_BELOW_MIN
    if domain_key in ("satisfaction_favourable", "alertness_favourable"):
        return value <= FAVOURABLE_MAX_CODE
    raise KeyError(domain_key)


def score(values: dict) -> tuple[int, dict]:
    """Total score and per-domain 0/1 flags. ``values`` holds all six inputs."""
    flags = {key: int(favourable(key, values[input_key])) for key, input_key, _name, _rule in DOMAINS}
    return sum(flags.values()), flags
