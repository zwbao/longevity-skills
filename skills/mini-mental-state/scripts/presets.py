"""Scoring constants: Folstein et al. 1975, p. 190 and Appendix pp. 196–198."""

PART_ONE = (
    "time_orientation_score", "place_orientation_score", "registration_score",
    "attention_score", "recall_score",
)
PART_TWO = (
    "naming_score", "repetition_score", "command_score", "reading_score",
    "writing_score", "copying_score",
)
MAXIMUM_SCORES = dict(zip(PART_ONE + PART_TWO, (5, 5, 3, 5, 3, 2, 1, 3, 1, 1, 1)))
PART_ONE_MAXIMUM = 21
PART_TWO_MAXIMUM = 9
TOTAL_MAXIMUM = 30
INPUT_UNITS = {key: "score" for key in MAXIMUM_SCORES}
INPUT_UNITS["registration_learned"] = "1"
INPUT_RANGES = {key: (0, maximum) for key, maximum in MAXIMUM_SCORES.items()}
INPUT_RANGES["registration_learned"] = (0, 1)  # Interface flag; never added to scores.
BOUNDARY = "本报告只汇总已完成施测的认知得分，不能据此诊断或排除痴呆、判断民事行为能力，也不能据此开始或停止药物。"
