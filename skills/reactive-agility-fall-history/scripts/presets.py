"""Exploratory cutoffs printed in the SKILLCOURT fall-history study.

[P] Giesche F, Abobakr AH, Banzer W, Groneberg DA, Vogt L, Hoffmann M, Albert I,
    Huelsduenker T. Reactive agility and motor-cognitive assessments for
    distinguishing community-dwelling older adults with and without a history of
    falls: a dual-centre cross-sectional study. GeroScience 2026.
    doi:10.1007/s11357-026-02477-4 (open access; only the printed cutoffs and
    summary numbers needed for the readout are extracted).

Results, "Discrimination analyses":
  "For clinical interpretability, an exploratory cutoff of 28.6 s was derived from
  the unadjusted Random Star Run analysis (Table 4), which yielded an AUC value of
  0.66, with 55% sensitivity and 76% specificity."
  "For comparison, the unadjusted ROC analyses based on the original SKILLCOURT
  reaction times yielded AUC values of 0.63 and 0.61 for the simple and choice
  reaction tasks, respectively, with exploratory cutoff values of 0.62 and 0.88 s."

Longer completion / response times were associated with higher odds of a history
of falls (OR per 1 SD: 1.82 Random Star Run, 1.58 simple, 1.42 choice). The paper
does not say whether a value equal to the cutoff counts as positive; this skill
puts a value equal to the cutoff on the "at or above" side (references/contract.md).
"""

from __future__ import annotations

# key -> (cutoff seconds, label, unadjusted AUC, sensitivity %, specificity %)
CUTOFFS = {
    "random_star_run_s": {
        "cutoff_s": 28.6,
        "label_zh": "随机星形跑完成时间",
        "unadjusted_auc": 0.66,
        "sensitivity_pct": 55,
        "specificity_pct": 76,
        "output": "random_star_run_side",
    },
    "skillcourt_simple_reaction_s": {
        "cutoff_s": 0.62,
        "label_zh": "简单踏步反应时间",
        "unadjusted_auc": 0.63,
        "sensitivity_pct": None,  # in Table 6, whose cells were not readable
        "specificity_pct": None,
        "output": "simple_reaction_side",
    },
    "skillcourt_choice_reaction_s": {
        "cutoff_s": 0.88,
        "label_zh": "选择踏步反应时间",
        "unadjusted_auc": 0.61,
        "sensitivity_pct": None,  # in Table 7, whose cells were not readable
        "specificity_pct": None,
        "output": "choice_reaction_side",
    },
}

# Adjusted models (age, study site; Random Star Run also x age), Results and abstract.
ADJUSTED = {
    "random_star_run_s": {"or_per_sd": 1.82, "auc": 0.73, "sensitivity_pct": 70, "specificity_pct": 71},
    "skillcourt_simple_reaction_s": {"or_per_sd": 1.58, "auc": 0.72, "sensitivity_pct": 63, "specificity_pct": 75},
    "skillcourt_choice_reaction_s": {"or_per_sd": 1.42, "auc": 0.70, "sensitivity_pct": 71, "specificity_pct": 67},
}
TUG_ADJUSTED_AUC = 0.63

SIDE_ABOVE = "达到或超过切点（有跌倒史的人更常落在这一侧）"
SIDE_BELOW = "低于切点（没有跌倒史的人更常落在这一侧）"

COHORT = {
    "n": 231,
    "fallers": 103,
    "non_fallers": 128,
    "mean_age": 71.9,
    "min_age": 60,
    "rsr_n": 172,
    "rsr_fallers": 80,
    "rsr_non_fallers": 92,
}

BOUNDARY = (
    "这是德国和卢森堡社区老人一次性测量里“过去一年有没有跌倒过”的横断面比较，切点是论文自己称为探索性的界值，"
    "落在切点哪一侧不等于你会不会跌倒，也不是诊断；只适用于按论文流程在 SKILLCOURT 上测得的成绩。"
    "近期跌过倒、走路不稳或担心跌倒，请找医生或康复治疗师做跌倒风险评估。"
)
