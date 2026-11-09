"""Parental longevity (PL) grouping as printed in the Gothenburg H70 study.

[P] Seidu NM, Rydén L, Skoog J, et al. Parental longevity and polygenic longevity
    scores in relation to ageing-related factors in a population of 70-year-olds
    followed over six years: The Gothenburg H70 Birth Cohort Study. GeroScience
    (2026). doi:10.1007/s11357-026-02501-7 (open access, CC BY 4.0).

Methods, "Definition of the PL groups": both parents surviving to age 85 ->
high-PL; one parent surviving to age 85 -> medium-PL; both parents died before
age 85 -> low-PL. "The mean age of parents was calculated as a single continuous
variable ... in case of missing data for one parent's age, the other was used."

Methods, "Study population": parents' ages were "at death or current"; 34
participants with missing data on one parent were not imputed; 44 participants
"where at least one parent died before age 41 years" were excluded; "70
participants whose parents were still alive" were "classified as long-lived, as
all were above age 85".

The polygenic longevity scores (PRS-CS on GWAS catalogue GCST008598) are not
computed: the per-variant posterior weights are not published.
"""

from __future__ import annotations

# Methods "Definition of the PL groups": survival cut-off (years).
SURVIVAL_CUTOFF_YEARS = 85
# Methods "Study population": participants with a parent who died before this age were excluded.
EARLY_DEATH_EXCLUSION_YEARS = 41

# Number of parents who reached 85 -> group (Methods "Definition of the PL groups").
GROUP_BY_REACHED = {2: "high-PL", 1: "medium-PL", 0: "low-PL"}
GROUP_ZH = {"high-PL": "高（双亲都活到 85 岁）", "medium-PL": "中（一方活到 85 岁）", "low-PL": "低（双亲都没活到 85 岁）"}

# Results "Baseline characteristics at age 70" (n = 1126).
COHORT = {
    "n": 1126,
    "n_high": 194,
    "pct_high": 17.2,
    "n_medium": 488,
    "pct_medium": 43.3,
    "n_low": 444,
    "pct_low": 39.4,
    "age_mean": 70.6,
    "birth_year": 1944,
    "n_followup": 800,
    "followup_years": 6.02,
}

# Results text and Discussion, directions only (Table 3 / Table 5 numbers are not quoted here).
FINDINGS_ZH = {
    "high-PL": [
        "受教育年限更长、MMSE 认知得分更高、童年家庭经济状况更好、目前家庭收入更高",
        "总胆固醇、HDL-c 和 LDL-c 更高，BMI、同型半胱氨酸、IL-6 和 CRP 更低",
        "目前吸烟的更少、高血压更少",
        "约 6 年随访中血浆 pTau217 上升得更少",
    ],
    "medium-PL": [
        "受教育年限更长、MMSE 认知得分更高",
        "总胆固醇更高、同型半胱氨酸更低",
        "目前吸烟的更少",
    ],
}
# Results "Sensitivity analyses": no longer significant after FDR correction.
FDR_LOST_ZH = "多重比较校正（FDR）后，和 CRP、IL-6 以及 pTau217 变化的关联不再显著。"
# Results "Interaction analyses with sex at age 70" and Table S4.
SEX_INTERACTION_ZH = "中等组和 CRP、NfL 的关系存在性别交互，只在女性中出现（补充表 S4）。"

BOUNDARY = (
    "父母长寿分组只是按父母活到的年龄分档，论文里它和多项衰老相关因素有关联，"
    "这是瑞典 70 岁人群的群体关联，不是你个人的寿命预测，也不是诊断；分档低不代表你会早逝，"
    "分档高也不代表可以忽视体检和生活方式。"
)
