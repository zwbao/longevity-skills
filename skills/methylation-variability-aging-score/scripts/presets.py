"""Vishnyakova et al., J Gerontol A Biol Sci Med Sci 2026;81(11):glag234, doi:10.1093/gerona/glag234.

The weights live in ../data/, frozen from two sources:

- table_s15_dmp_dvp_epic.csv: Supplementary Table S15 ("CpG predictors and weights
  for methylation-based health scores"), the integrated DMP-DVP biomarker trained in
  CLSA on EPIC data (789 distinct CpGs, Supplementary Note 2).
- DVP_DMP_450K.csv: the 450K-restricted DMP-DVP model used for BLSA validation,
  from the authors' repository github.com/oliversion/epg-aging, commit
  6a3cb4443c8d5d6bda59b21b0a87cbe44a179517, eScores_weights/DVP_DMP_450K.csv.

Both files hold rows outcome,pred,w: FI/CF/PF elastic-net intercept and CpG weights,
three COX weights, and four transform constants (mean_bio, sd_bio, mean_age, sd_age).
The computation follows eScores.R in the same repository.
"""

from __future__ import annotations

import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

MODELS = {
    "epic": {
        "file": "table_s15_dmp_dvp_epic.csv",
        "output": "dmp_dvp_score",
        "label": "整合 DMP-DVP 评分（补充表 S15，EPIC 芯片模型）",
    },
    "450k": {
        "file": "DVP_DMP_450K.csv",
        "output": "dmp_dvp_450k_score",
        "label": "整合 DMP-DVP 评分（450K 限定模型，作者代码仓库）",
    },
}

HEALTH_SCORES = ("FI", "CF", "PF")

# Printed counts used by the tests.
S14_N_CPGS_EPIC = {"FI": 212, "CF": 254, "PF": 342}       # Table S14, "DMP-DVP"
S14_N_CPGS_450K = {"FI": 141, "CF": 201, "PF": 269}       # Table S14, "DMP-DVP (450K)"
DISTINCT_CPGS_EPIC = 789                                   # Supplementary Note 2 and Results
CLSA_TRAIN_N = 1091                                        # Methods, training set
CLSA_VALID_N = 187                                         # Results, validation mortality analysis
CLSA_VALID_DEATHS = 14
BLSA_N = 728
BLSA_DEATHS = 284

BOUNDARY = (
    "这是研究复现意义上的个人读出，不是诊断，也不是治疗建议。不能据此开始或停止任何药物。"
    "这个分数不是“生物年龄”，论文的“表观年龄偏差”需要的年龄回归常数没有公布。"
    "现用药和体检只作上下文，不增删方法算出的结果。"
)


def load_model(name: str) -> dict:
    """Read one weight file into intercepts, CpG weights, COX weights and transform constants."""
    path = DATA / MODELS[name]["file"]
    intercept: dict[str, float] = {}
    weights: dict[str, dict[str, float]] = {key: {} for key in HEALTH_SCORES}
    cox: dict[str, float] = {}
    transform: dict[str, float] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            outcome, pred, w = row["outcome"], row["pred"], float(row["w"])
            if outcome == "COX":
                cox[pred] = w
            elif outcome == "transform":
                transform[pred] = w
            elif pred == "Intercept":
                intercept[outcome] = w
            else:
                weights[outcome][pred] = w
    return {"intercept": intercept, "weights": weights, "cox": cox, "transform": transform}


def model_cpgs(model: dict) -> list[str]:
    """Distinct CpGs of a model, in file order."""
    seen: dict[str, None] = {}
    for key in HEALTH_SCORES:
        for cpg in model["weights"][key]:
            seen.setdefault(cpg, None)
    return list(seen)
