"""Constants for the PhenoAge acceleration and CVD hazard readout.

Paper: Yu et al., GeroScience 2026, doi:10.1007/s11357-026-02543-x.

PhenoAge: Supplementary Methods ("Assessment method of biological aging")
prints the Levine formula with rounded weights and says the calculation was
done in R with the BioAge package. The weights below are the unrounded ones
in BioAge R/phenoage_calc.R (orig = TRUE, commit b1f9fc0). Each rounds to the
printed value except the log numerator: the supplement prints -0.0053, the
code uses -0.0055305 (Levine 2018 prints -0.00553). That number only shifts
every phenotypic age by the same constant. ALP is printed 0.00188 while the
code's 0.001868778 rounds to 0.00187 (under 0.04 years at 300 U/L). See
references/contract.md.

Units follow Supplementary Table S1 (albumin g/L, creatinine umol/L, glucose
mmol/L, CRP mg/dL entered as ln, WBC 1000 cells/uL).

Hazard ratios: Results, "Relationship between biological aging acceleration
and CVD outcomes (path 2)", per one-year increase in PhenoAgeAccel.
"""

from __future__ import annotations

DOI = "10.1007/s11357-026-02543-x"
FULL_TEXT_READ = True

TITLE = "表型年龄与心血管风险"

BOUNDARY = (
    "这是按论文方法算出的个人读出和队列关联的模型换算，不是诊断，也不是治疗建议。"
    "风险比来自英国生物银行观察队列，不能证明改变某项化验就会改变心血管风险。"
    "不能据此开始或停止任何药物。"
)

# BioAge R/phenoage_calc.R, orig = TRUE (dayoonkwon/BioAge b1f9fc02f086cd4aa74185f2335ab1366082e7fe)
PHENOTYPE_INTERCEPT = -19.90667
PHENOTYPE_WEIGHTS = {
    "albumin_gL": -0.03359355,
    "creat_umol": 0.009506491,
    "glucose_mmol": 0.1953192,
    "lncrp": 0.09536762,
    "lymph_pct": -0.01199984,
    "mcv_fl": 0.02676401,
    "rdw_pct": 0.3306156,
    "alp_u_l": 0.001868778,
    "wbc_10e3": 0.05542406,
    "age": 0.08035356,
}
MORTALITY_NUMERATOR = -1.51714  # -(exp(120 * GAMMA) - 1)
GAMMA = 0.007692696
PHENOAGE_LOG_NUMERATOR = -0.0055305
PHENOAGE_LOG_DENOMINATOR = 0.090165
PHENOAGE_OFFSET = 141.50225

# Supplementary Methods, as printed. Tests check the code weights round to these.
PAPER_PRINTED = {
    "intercept": -19.907,
    "albumin_gL": -0.0336,
    "creat_umol": 0.0095,
    "glucose_mmol": 0.1953,
    "lncrp": 0.0954,
    "lymph_pct": -0.0120,
    "mcv_fl": 0.0268,
    "rdw_pct": 0.3306,
    "alp_u_l": 0.00188,
    "wbc_10e3": 0.0554,
    "age": 0.0804,
    "gamma": 0.0076927,
    "offset": 141.50225,
    "log_denominator": 0.090165,
    "log_numerator": -0.0053,
}

# Results, path 2: HR (95% CI) per one-year increase in PhenoAgeAccel.
HR_INCIDENT_CVD = (1.033, 1.028, 1.038)
HR_CVD_DEATH = (1.070, 1.058, 1.083)

# Results, path 1: beta (95% CI) of PhenoAgeAccel per one point of each diet score.
# Cohort associations. Not applied to one person; used only by the consistency test.
PATH1_BETA_PHENOAGEACCEL = {"HEI": -0.036, "AHEI": -0.039, "DASH": -0.178, "MDS": -0.254}

# Results, "Participant characteristics" (PhenoAgeAccel cohort). Context only.
COHORT_N = 52718
COHORT_AGE_MEAN = 55.83
COHORT_AGE_SD = 8.15
COHORT_PHENOAGE_MEAN = 49.69
COHORT_PHENOAGE_SD = 9.78
COHORT_FOLLOWUP_YEARS = 12.11
COHORT_CVD_EVENTS = 4292
COHORT_CVD_DEATHS = 442

PHENOAGE_BIOMARKERS = (
    ("albumin_gL", "白蛋白", "g/L"),
    ("creat_umol", "肌酐", "µmol/L"),
    ("glucose_mmol", "血糖", "mmol/L"),
    ("crp_mg_dl", "C反应蛋白", "mg/dL"),
    ("lymph_pct", "淋巴细胞百分比", "%"),
    ("mcv_fl", "平均红细胞体积", "fL"),
    ("rdw_pct", "红细胞分布宽度", "%"),
    ("alp_u_l", "碱性磷酸酶", "U/L"),
    ("wbc_10e3", "白细胞", "10^3/µL"),
)
