"""Constants for the cognitive-scores model of Simkhada et al., GeroScience 2026.

The model is the authors' published XGBoost (SMOTENC) model trained on the
six cognitive and functional scores only (the COG modality), with sigmoid
(Platt) calibration over five group-aware folds and its own Youden threshold.
It is ``models/final_model_cognitive_scores.pkl`` in
https://github.com/bipulsimkhada/mci_progression_ml at commit
c67358dbb0960b41c2b1fd775114d000bae13081. ``data/cog_model.json`` holds the
trees, the five calibration pairs and the threshold exported from that file;
references/contract.md says how, and what was checked.

The paper's headline model (DEM-COG-MRI, 50 features after selection from
334) needs 323 FreeSurfer 7 measures from ADNI's UCSF pipeline. It is not
computed here.
"""

from __future__ import annotations

DOI = "10.1007/s11357-026-02551-x"
FULL_TEXT_READ = True
CODE_COMMIT = "c67358dbb0960b41c2b1fd775114d000bae13081"
MODEL_FILE = "data/cog_model.json"
MODEL_SOURCE_SHA256 = "45bb95fd0219e38cea96bc364af284829045ea7316f20d665062ae84094daa27"

TITLE = "两年内由轻度认知障碍转为痴呆的风险（认知量表模型）"

BOUNDARY = (
    "这是研究模型的个人读出，不是诊断，也不是治疗建议。"
    "模型只在 ADNI 里已诊断为轻度认知障碍的人身上训练和检验过，没有外部队列验证。"
    "不能据此开始或停止任何药物。体检不增删方法算出的结果。"
)

# Inputs in the order of the model's feature columns (config.py `cog`).
# (skill.json key, ADNI column, Chinese label, unit)
FEATURES = (
    ("mmse_score", "MMSCORE", "简易精神状态检查（MMSE）", "score"),
    ("cdr_global_score", "CDGLOBAL", "临床痴呆评定总分（CDR 全局）", "score"),
    ("cdr_sb_score", "CDRSB", "临床痴呆评定各项之和（CDR-SB）", "score"),
    ("adas11_score", "TOTSCORE", "阿尔茨海默病评估量表认知部分 11 项（ADAS-Cog 11）", "score"),
    ("adas13_score", "TOTAL13", "阿尔茨海默病评估量表认知部分 13 项（ADAS-Cog 13）", "score"),
    ("faq_score", "FAQTOTAL", "功能活动问卷（FAQ）", "score"),
)

# CDR global takes only these values.
CDR_GLOBAL_VALUES = (0.0, 0.5, 1.0, 2.0, 3.0)
# ADAS-Cog 13 = ADAS-Cog 11 + delayed word recall (0-10) + number cancellation (0-5).
ADAS13_MINUS_ADAS11_MAX = 15.0

# Supplementary Table S2, dynamic dataset, Overall column: mean and SD.
# Used only to flag a score more than 2 SD from the training cohort's mean.
TABLE_S2_MEAN_SD = {
    "mmse_score": (27.43, 2.14),
    "cdr_global_score": (0.49, 0.13),
    "cdr_sb_score": (1.67, 1.11),
    "adas11_score": (10.37, 4.88),
    "adas13_score": (16.65, 7.31),
    "faq_score": (3.77, 4.50),
}

# Cohort facts (paper, Methods and Results). Not applied to one person.
N_SAMPLES = 2008
N_SUBJECTS = 828
N_SMCI_SAMPLES = 1306
N_PMCI_SAMPLES = 702
N_TRAIN_SAMPLES = 1607
N_TEST_SAMPLES = 401
WINDOW_MONTHS = 24
# Independent test set, DEM-COG-MRI model (Results).
HEADLINE_TEST_BALANCED_ACCURACY_PCT = 81.99
# Ablation on the test set: COG-only lowers balanced accuracy by this much.
COG_ONLY_ABLATION_DROP_PCT = 4.73
