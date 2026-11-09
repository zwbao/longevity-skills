"""Cut-offs for plasma pTau217 and pTau217/Abeta42 (Simoa) from Martino-Adami et al.

Source [P]: Martino-Adami PV, Coutinho de Alvarenga J, Freccero P, et al.
Diagnostic performance of plasma pTau217 in genetically admixed South American
populations. Nat Commun 2026;17:9464, doi:10.1038/s41467-026-76434-2.

Assays in [P] (Methods, "Biomarker measurement"): pTau217 with the ALZpath V2
Simoa assay kit, Abeta42 with the Neurology 4-plex E Simoa kit, both on a Simoa
HD-X. The cut-offs below are only meaningful for these assays.

Every number here is printed in [P]: Table 2 (Cog-Aging-Study-Brazil rows, with
the <= / >= convention), and the Results paragraphs "Data driven plasma pTau217
and pTau217/Abeta42 cut-offs in Cog-Aging-Study-Brazil" and "Data-driven plasma
pTau217 and pTau217/Abeta42 cut-offs in GeNED.ar-Argentina".
"""

from __future__ import annotations

# Two-component, equal-variance Gaussian mixtures on natural-log values (mclust "E" model),
# the best-fitting model per [P] Results. Means (low; high class), common variance and
# proportions (low; high) as printed in Supplementary Table 2 (Cog-Aging-Study-Brazil,
# pTau217 n=304, ratio n=298) and Supplementary Table 3 (GeNED.ar-Argentina, n=134 / 131),
# rows "2 Equal". The log base is not stated; natural log reproduces every printed cut-off
# (tests/test_manifest.py), log10 does not.
GMM = {
    ("ptau217", "brazil"): {"means": (-1.18, 0.09), "variance": 0.17, "proportions": (0.64, 0.36)},
    ("ratio", "brazil"): {"means": (-2.96, -1.62), "variance": 0.3, "proportions": (0.67, 0.33)},
    ("ptau217", "argentina"): {"means": (-1.20, -0.05), "variance": 0.16, "proportions": (0.77, 0.23)},
    ("ratio", "argentina"): {"means": (-2.88, -1.55), "variance": 0.16, "proportions": (0.69, 0.31)},
}

# Single GMM cut-off (intersection of the two class densities, Methods).
# Table 2: pTau217 ">=0.63" positive; pTau217/Abeta42 ">=0.12" positive.
# Results: the same 0.63 pg/mL and 0.12 in GeNED.ar-Argentina and in the pooled data.
SINGLE_CUTOFF = {"ptau217": 0.63, "ratio": 0.12}

# Two cut-offs: value <= lower -> negative, value >= upper -> positive, in between indeterminate.
# Keys: (marker, cohort, posterior probability threshold) -> (lower, upper).
# Brazil rows also in Table 2 (pTau217 <=0.52/>=0.76, <=0.50/>=0.79, <=0.47/>=0.84;
# ratio <=0.09/>=0.16, <=0.08/>=0.17, <=0.07/>=0.19). Results text for Brazil prints
# no ratio pair at 0.90; Table 2 does (0.07/0.19).
TWO_CUTOFFS = {
    ("ptau217", "brazil", 0.80): (0.52, 0.76),
    ("ptau217", "brazil", 0.85): (0.50, 0.79),
    ("ptau217", "brazil", 0.90): (0.47, 0.84),
    ("ptau217", "argentina", 0.80): (0.52, 0.77),
    ("ptau217", "argentina", 0.85): (0.50, 0.81),
    ("ptau217", "argentina", 0.90): (0.47, 0.86),
    ("ratio", "brazil", 0.80): (0.09, 0.16),
    ("ratio", "brazil", 0.85): (0.08, 0.17),
    ("ratio", "brazil", 0.90): (0.07, 0.19),
    ("ratio", "argentina", 0.80): (0.10, 0.14),
    ("ratio", "argentina", 0.85): (0.097, 0.15),
    ("ratio", "argentina", 0.90): (0.09, 0.16),
}

# Primary reading: the >=0.85 pair in Cog-Aging-Study-Brazil, the only cohort with CSF
# amyloid status; [P] Results: "For both biomarkers, the models using two cut-offs at the
# >=0.85 probability threshold provided the best overall performance".
PRIMARY_COHORT = "brazil"
PRIMARY_PROBABILITY = 0.85
PROBABILITIES = (0.80, 0.85, 0.90)
COHORTS = ("brazil", "argentina")
COHORT_ZH = {"brazil": "巴西 Cog-Aging-Study", "argentina": "阿根廷 GeNED.ar"}

# External pTau217 cut-offs of Ashton et al. (2024) as printed in [P] Table 2:
# single ">0.42"; two cut-offs "<0.40" and ">0.63".
ASHTON_SINGLE = 0.42
ASHTON_TWO = (0.40, 0.63)

# Table 2, n = 45 paired CSF-plasma, Cog-Aging-Study-Brazil (cohort statistics, not the person's).
TABLE2_PERFORMANCE_085 = {
    "ptau217": {"ppv": 0.88, "npv": 0.81, "indeterminate_pct": 11.1},
    "ratio": {"ppv": 0.89, "npv": 0.73, "indeterminate_pct": 20.9},
}

ASSAY_OK = "simoa-alzpath"
ASSAY_ALIASES = {"simoa-alzpath", "simoa", "alzpath", "quanterix", "simoa alzpath", "alzpath simoa"}

BOUNDARY = ("血浆 pTau217 分档只说明这一次化验落在论文切点的哪一侧，不是阿尔茨海默病的诊断；"
            "切点只适用于 Simoa ALZpath pTau217（和 Simoa Neurology 4-plex E Aβ42），来自南美记忆门诊人群；"
            "灰区结果需要医生决定是否做脑脊液或 PET 等确认检查。本报告不涉及任何用药的开始、停止或剂量。")
