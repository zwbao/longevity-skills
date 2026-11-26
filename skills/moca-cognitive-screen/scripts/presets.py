"""Frozen scoring constants: Nasreddine et al., JAGS 2005, pp. 697-698."""

SCORE_UNIT = "score"
TASK_MAXIMA = {
    "delayed_recall_score": 5,
    "clock_drawing_score": 3,
    "cube_copy_score": 1,
    "alternation_score": 1,
    "phonemic_fluency_score": 1,
    "abstraction_score": 2,
    "sustained_attention_score": 1,
    "serial_subtraction_score": 3,
    "digits_forward_score": 1,
    "digits_backward_score": 1,
    "naming_score": 3,
    "sentence_repetition_score": 2,
    "orientation_score": 6,
}
MAX_TOTAL = 30
EDUCATION_THRESHOLD_YEARS = 12
EDUCATION_BONUS = 1
NORMAL_CUTOFF = 26
# Input sanity bound, not a study eligibility limit or a fitted constant.
EDUCATION_RANGE = (0, 40)
BOUNDARY = (
    "本报告仅核对已完成标准施测的原版完整 MoCA 得分；筛查分档不能诊断或排除轻度认知障碍或痴呆，"
    "不能区分两者，也不能预测个人未来痴呆风险、衰老速度或寿命；不能据此开始或停止药物。"
)


def score(values):
    """Sum already-scored tasks, then apply the printed education correction."""
    raw = int(sum(values[key] for key in TASK_MAXIMA))
    bonus = (EDUCATION_BONUS if values["education_years"] <= EDUCATION_THRESHOLD_YEARS
             and raw < MAX_TOTAL else 0)
    adjusted = raw + bonus
    return {
        "raw_score": raw,
        "education_bonus": bonus,
        "adjusted_score": adjusted,
        "screening_category": ("低于原文筛查切点" if adjusted < NORMAL_CUTOFF
                               else "未低于原文筛查切点"),
    }
