"""Constants for the GAET SASP Score (Zhao et al., Aging Cell 2026; doi:10.1111/acel.70737).

Every number here has a source:
- PROTEINS, the embedding order: shangshuzhao/sasp utils.embed_protein / proteins_info.protein_list
  (commit 34d5f1b). The paper lists the same 38 gene symbols in Methods 2.3 (it prints SERPINE1 as "SERPIN1").
- Model shape (d_model 128, 8 heads, 2 layers, latent 6): example.ipynb loads TGAE(d_model=128, latent_dim=6,
  nhead=8, num_layers=2); feed-forward 2048 and LayerNorm eps 1e-5 are the PyTorch defaults the checkpoint was
  saved with (linear1.weight is 2048 x 128).
- UKB_MEAN_SD: proteins_info.match_ukb_dist (code, not printed in the paper). Used here only to check that the
  input looks like UKB-PPP NPX and to describe each protein; the score itself takes the NPX values as they are.
- CUTOFF: paper Results 3.5 / Methods 2.6 ("high (> 65) SASP Score groups"; 90th percentile in the training
  sample without a major chronic condition at baseline).
"""

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_FILE = SKILL_DIR / "data" / "gaet_pretrained_encoder.npz"
WEIGHTS_SOURCE = (
    "https://github.com/shangshuzhao/sasp/blob/34d5f1becd2f9d7378feec870b59e459fe451d0c/tgae_pre_trained.pth"
)
WEIGHTS_SOURCE_SHA256 = "b34230d43085b8fe670dbce2769ba20b90f7b3e5a960fb67ec0dd591786e41c5"

N_LAYERS = 2
N_HEADS = 8
D_MODEL = 128
LATENT_DIM = 6
LAYER_NORM_EPS = 1e-5

PROTEINS = [
    "ANG", "CCL13", "CCL2", "CCL20", "CCL3", "CCL4", "CHI3L1", "CSF2",
    "CXCL1", "CXCL10", "CXCL8", "CXCL9", "FGA", "FGF2", "FSTL3", "GDF15",
    "HGF", "ICAM1", "IGFBP2", "IGFBP6", "IL1B", "IL4", "IL5", "IL6",
    "IL6ST", "LEP", "MIF", "MMP12", "PGF", "PLAUR", "SERPINE1", "TF",
    "TIMP1", "TNFRSF11B", "TNFRSF1A", "TNFRSF1B", "TNFSF10", "VEGFA",
]

# skill.json input key for each protein
KEYS = {name: name.lower() + "_npx" for name in PROTEINS}

UKB_MEAN_SD = {
    "ANG": (0.008412209, 0.3955384),
    "CCL13": (0.022755328, 0.7855913),
    "CCL2": (0.023904332, 0.5965727),
    "CCL20": (0.151260181, 1.0096516),
    "CCL3": (0.064064144, 0.7045312),
    "CCL4": (0.065627897, 0.7433986),
    "CHI3L1": (0.133817108, 0.9136581),
    "CSF2": (0.00986164, 0.3452719),
    "CXCL1": (0.110607086, 1.0677707),
    "CXCL10": (0.082652478, 0.7815331),
    "CXCL8": (0.042198496, 0.7725987),
    "CXCL9": (0.097004956, 0.7935531),
    "FGA": (0.01239111, 0.316729),
    "FGF2": (0.078542032, 0.7595377),
    "FSTL3": (0.031882412, 0.402156),
    "GDF15": (0.073444923, 0.5895939),
    "HGF": (0.032068841, 0.440271),
    "ICAM1": (0.012879968, 0.3362013),
    "IGFBP2": (-0.050848724, 0.8046838),
    "IGFBP6": (0.023432412, 0.3838551),
    "IL1B": (0.073486292, 0.6282647),
    "IL4": (-0.141638803, 0.9842809),
    "IL5": (0.26841099, 1.5453851),
    "IL6": (0.124677371, 0.8839393),
    "IL6ST": (0.0012994, 0.1975127),
    "LEP": (-0.08276832, 1.2912836),
    "MIF": (-0.02221921, 0.768743),
    "MMP12": (0.043234173, 0.6566276),
    "PGF": (0.020601765, 0.3272117),
    "PLAUR": (0.020406817, 0.3394527),
    "SERPINE1": (-0.041613098, 0.7684842),
    "TF": (-0.002692966, 0.2136098),
    "TIMP1": (0.022978616, 0.3305618),
    "TNFRSF11B": (0.014422148, 0.3596158),
    "TNFRSF1A": (0.029982814, 0.3629309),
    "TNFRSF1B": (0.034870779, 0.4259883),
    "TNFSF10": (-0.006918623, 0.2934764),
    "VEGFA": (0.088493049, 0.6615517),
}

# Plausible NPX range for every protein (skill.json inputs[].range). UKB-PPP NPX are centred near 0.
NPX_RANGE = (-10.0, 15.0)
# Stop when the median |z| against the UKB-PPP mean/SD is above this: the file is then almost surely not on the
# UKB-PPP NPX scale (Olink Target 96 NPX sit around 2-12, linear NPX or pg/mL are far off).
SCALE_MEDIAN_ABS_Z = 3.0
# Describe single proteins this far from the UKB-PPP mean.
FLAG_ABS_Z = 3.0

CUTOFF = 65.0  # paper: high SASP Score > 65, low <= 65

# Population numbers the paper prints (UK Biobank test sample n = 7639). Never the person's result.
PAPER = {
    "n_ukb_ppp": 50997,
    "n_train": 43358,
    "n_test": 7639,
    "n_medex": 585,
    "rho_age_test": 0.70,
    "hr_mortality_per_sd": 1.41,
    "hr_mortality_ci": (1.25, 1.60),
    "mean_follow_up_years": 13.3,
}

UNITS_NPX = ("npx", "olinknpx", "npx(log2)", "log2npx")

TITLE = "SASP 衰老分泌表型评分（GAET，38 个血浆蛋白）"
BOUNDARY = (
    "这是 UK Biobank 人群里建立的研究用评分，只适用于和 UKB-PPP 同一标度的 Olink Explore NPX 数据；"
    "它和死亡、慢病的关联是人群统计，不是你个人的诊断或预测，也不能据此开始或停止任何药物、补充剂或治疗。"
)
