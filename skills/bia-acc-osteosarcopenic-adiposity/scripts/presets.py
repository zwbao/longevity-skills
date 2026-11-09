"""Operational thresholds of the BIA-ACC-based osteosarcopenic adiposity (OSA) phenotype.

Ilich JZ, Mills J, Cvijetic S, Barlow EM, Galijasevic S, Boschiero D, Harman J.
Sex- and age-specific patterns in bone, muscle, and fat across adulthood and their
relation to osteosarcopenic adiposity phenotype: a cross-sectional study.
GeroScience (2026). doi:10.1007/s11357-026-02496-1.
Section "Anthropometric and bioimpedance measurements" (Methods), quoted in
references/contract.md.

The T- and S-scores themselves come from the BIA-ACC device (BioTekna). Their
prediction equations and reference databases are proprietary and not printed
in the paper, so this skill reads the scores off the person's BIA-ACC report and
only applies the printed cut-offs.
"""

from __future__ import annotations

# Methods: "The BIA-ACC T-score ≥ − 1.0 indicated estimated bone mass within the reference
# range, a score < − 1.0 and > − 2.5 as moderately reduced estimated bone mass, and a score
# ≤ − 2.5 as markedly reduced estimated bone mass."
T_REFERENCE_LOWER = -1.0   # T >= -1.0: within reference range
T_MARKED = -2.5            # T <= -2.5: markedly reduced

# Methods: "An S-score ≤ − 1.0 was used as the prespecified operational threshold for
# reduced BIA-ACC-estimated skeletal muscle mass"
S_REDUCED = -1.0           # S <= -1.0: reduced

# Methods: "Adiposity was defined as total fat mass ≥ 25% of body weight in men and ≥ 32% in women"
FAT_PCT_ADIPOSITY = {"male": 25.0, "female": 32.0}

BONE_LABELS = ("在参考范围内", "中度降低", "明显降低")
YES_NO = ("未达到", "达到")
OSA_LABELS = ("不符合", "符合")

# Study population (Results): 9717 Caucasian adults aged 20-90, 6412 women; Italy 2010-2014.
STUDY = {"n": 9717, "women": 6412, "men": 3305, "ages": (20, 90)}

BOUNDARY = ("这是按论文切点对 BIA-ACC 体成分报告的操作性分档，不是骨质疏松、肌少症或肥胖的临床诊断；"
            "T 值和 S 值只适用于 BIA-ACC 设备，不能换成双能 X 线骨密度 T 值或其他体脂秤读数；"
            "不据此开始或停止任何药物，结果请带去和医生讨论。")
