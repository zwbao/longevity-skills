"""Cut-offs and diagnostic accuracy printed for the ItFNAT delayed free recall and the MoCA.

[P] Scaramuzzi GF, Ventrella T, Iacobellis S, et al. Delayed associative memory and
    recall error patterns in mild cognitive impairment: discriminant capacity of the
    Italian face-name association test. GeroScience. 2026.
    doi:10.1007/s11357-026-02599-9

Table 4 (ROC, Youden-optimal cut-offs on adjusted scores):
  ItFNAT DFR  AUC 0.711 [0.621, 0.801]  cut-off <= 3.21   sens 60.00  spec 80.56  acc 71.21
  MoCA        AUC 0.705 [0.614, 0.796]  cut-off <= 23.99  sens 65.00  spec 72.22  acc 68.94
  DFR vs MoCA  dAUC 0.006 [-0.119, 0.131], DeLong p = .925

Data analysis: ROC analyses "were performed using adjusted scores derived from the most
recent available Italian normative data (MoCA: 3, 34)": the ItFNAT DFR score is the
age-adjusted score of the ItFNAT norms (ref 3, Manippa et al., Clin Neuropsychol 2025)
and the MoCA total is age- and education-adjusted with the Italian MoCA 8.1 norms
(ref 34, Dapor et al., Neurol Sci 2025). The adjustment equations are in those papers,
not in [P]; this skill takes the adjusted scores as printed on an Italian report.

Results text prints PLR = 3.086 for the DFR and NLR = 0.485 for the MoCA; both follow
from the Table 4 sensitivity and specificity (PLR = sens / (1 - spec),
NLR = (1 - sens) / spec). The Results text also states MoCA sensitivity 78.1% and
specificity 65.0%, which disagree with Table 4; Table 4 is used because it reproduces
the printed NLR and accuracy (see references/claims.md).
"""

from __future__ import annotations

# Table 4, "Cut-off" column: positive (MCI-like) when the adjusted score is <= the cut-off.
DFR_CUTOFF = 3.21
MOCA_CUTOFF = 23.99

# Table 4: (sensitivity %, specificity %, accuracy %, AUC, AUC 95% CI).
TABLE4 = {
    "dfr": {"sens": 60.00, "spec": 80.56, "acc": 71.21, "auc": 0.711, "auc_ci": (0.621, 0.801),
            "sens_ci": (47.54, 72.44), "spec_ci": (69.53, 88.94)},
    "moca": {"sens": 65.00, "spec": 72.22, "acc": 68.94, "auc": 0.705, "auc_ci": (0.614, 0.796),
             "sens_ci": (51.60, 77.87), "spec_ci": (60.41, 82.14)},
}
DELONG = {"delta_auc": 0.006, "ci": (-0.119, 0.131), "p": 0.925}

# Table 1 / Participants.
COHORT = {
    "n": 136,
    "n_ch": 72,
    "n_mci": 64,
    "women": 77,
    "mean_age": 63.37,
    "sd_age": 9.71,
    "mean_education": 11.85,
    "sd_education": 4.51,
    "region_zh": "意大利南部普利亚大区",
}

# ItFNAT: 16 face-name pairs (Procedure), so the raw DFR score is 0-16.
ITFNAT_PAIRS = 16

BOUNDARY = (
    "这是意大利南部一个 136 人小样本里得出的初步切点，论文自己说应视为初步；"
    "切点只适用于按意大利常模校正过的 ItFNAT 延迟自由回忆分和 MoCA 分，不能直接套原始分或中文版 MoCA。"
    "结果只是筛查线索，不是轻度认知障碍或痴呆的诊断；"
    "担心记忆下降，请到神经内科或记忆门诊做完整的神经心理评估。"
)
