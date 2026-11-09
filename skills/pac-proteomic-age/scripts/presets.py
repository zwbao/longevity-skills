"""Constants for the PAC proteomic age (Kuo et al., Aging Cell 2024), as run
by Zhavoronkov et al., Nature Biotechnology 2026 (doi:10.1038/s41587-026-03286-y).

Every number here is copied from released code the 2026 paper names under
"Code availability":
- kuo-lab-uchc/PAC, pac_proteomic_age.R (commit e15edb66800f876a928cec9c8856500048c46fea):
  shape, rate, shape0, rate0, beta_age and the 129 betas (age + 128 proteins).
- Insilico-org/proteoclock, proteoclock/materials/simple_clocks/kuo_2024/weights/
  kuo_conventinal.txt (commit d078b246c9a834bb1eaa54a79381b6c6c14245f7, MIT):
  the same 129 coefficients, identical to the last printed digit; only the
  Gompertz rate is rounded there to 2.32E-04, so the R value is used here.

The 2026 paper's Supplementary Table 2 labels this clock "Kuo_2024(none)":
raw NPX, no scaling, which is also what the original R code does.
"""

TITLE = "PAC 蛋白质组年龄（Olink NPX）"

BOUNDARY = (
    "这是用 Olink 蛋白数据按英国生物银行死亡模型换算的模型年龄，不是诊断，也不是对你寿命的预测；"
    "不同批次、不同实验室的 NPX 之间有系统偏移，单次绝对值的意义有限，同一批次里前后两次的变化更可比。"
    "论文中的变化来自一项药物试验的事后探索分析，不说明任何药物对你有效；"
    "不要据此开始、停用或调整任何药物，用药请和医生商量。"
)

# Gompertz model with age and 128 proteins (10-year all-cause mortality, UK Biobank PPP).
SHAPE = 0.148766187078631
RATE = 0.000231560557596016
# Gompertz model with age only, used to turn the 10-year risk back into an age.
SHAPE0 = 0.1200806
RATE0 = 0.000004885383
BETA_AGE0 = 0.1087932
# Coefficient of chronological age inside the 128-protein model.
BETA_AGE = 0.029353964
HORIZON_YEARS = 10.0

# Ages of the UK Biobank Pharma Proteomics Project participants PAC was fit on (README of kuo-lab-uchc/PAC).
TRAINING_AGE_RANGE = (39, 70)

# Olink Explore assay names as gene symbols, in the order of pac_proteomic_age.R.
# FUT3-FUT5 is one Olink assay; the R code writes it fut3_fut5.
PAC_PROTEIN_COEFFICIENTS = (
    ("ADA2", 0.099491261),
    ("ADAMTS13", -0.128153586),
    ("ADAMTS16", 0.097070584),
    ("ADGRG2", -0.005514185),
    ("ADM", 0.191335791),
    ("AGER", -0.276924813),
    ("AGR2", 0.034399365),
    ("APOE", -0.075457263),
    ("AREG", -0.005805245),
    ("ART3", -0.215725117),
    ("BAG3", -0.064391821),
    ("BCAM", 0.194400347),
    ("BCAN", -0.01494478),
    ("BRK1", 0.099807081),
    ("C7", 0.050241198),
    ("CA14", -0.029057558),
    ("CA4", -0.103814564),
    ("CALCA", 0.070480748),
    ("CBLIF", -0.034660872),
    ("CD248", -0.15575238),
    ("CD34", -0.001621645),
    ("CDCP1", -0.01565701),
    ("CEACAM5", 0.119829451),
    ("CEACAM6", 0.071034581),
    ("CELA2A", -0.050333113),
    ("CHAD", -0.055156094),
    ("CNDP1", -0.078615313),
    ("COL24A1", 0.098018235),
    ("CPA2", -0.006973108),
    ("CRH", -0.045531367),
    ("CRISP3", -0.227985467),
    ("CRTAC1", -0.137532908),
    ("CTHRC1", 0.090923928),
    ("CTRC", -0.037373094),
    ("DCXR", -0.108456609),
    ("DDC", -0.062976739),
    ("DKK4", -0.084424204),
    ("DSG4", -0.04803032),
    ("EDA2R", 0.167737797),
    ("EGFR", 0.005878648),
    ("EPHA4", -0.007561524),
    ("FAP", -0.137882529),
    ("FASLG", -0.016749283),
    ("FCRL1", -0.018107792),
    ("FGFBP1", -0.068519646),
    ("FGFBP2", -0.027362969),
    ("FLT3", -0.125079859),
    ("FUT3-FUT5", 0.026829529),
    ("GALNT5", 0.138523985),
    ("GALNT7", -0.126913742),
    ("GDF15", 0.107668152),
    ("GFAP", 0.209132471),
    ("GP2", 0.096307256),
    ("GZMA", -0.152706324),
    ("HAVCR1", 0.053938526),
    ("HGF", 0.110094224),
    ("HPGDS", -0.012193783),
    ("ICAM3", 0.288576126),
    ("ICAM5", 0.043023223),
    ("IGFBP3", -0.030544583),
    ("IGFBP7", 0.111604776),
    ("IL1RL1", -0.001024753),
    ("IL22", 0.028680301),
    ("IL6", -0.013744572),
    ("ITGA2", -0.013033678),
    ("ITGAM", -0.139848216),
    ("ITGAV", 0.006030185),
    ("IZUMO1", -0.159282896),
    ("KIT", -0.047343343),
    ("KLK3", 0.029428855),
    ("KLK4", 0.015070364),
    ("KRT19", 0.068816751),
    ("LCP1", -0.085180823),
    ("LRRN1", 0.052069065),
    ("LRTM2", -0.208651159),
    ("LTBP2", 0.457163801),
    ("LTO1", -0.136903943),
    ("MEP1B", -0.019177778),
    ("MEPE", -0.083227652),
    ("MET", -0.080694831),
    ("MMP10", -0.113440341),
    ("MMP12", 0.14737764),
    ("MMP9", 0.058012728),
    ("NCAN", -0.126449842),
    ("NEFL", 0.325071818),
    ("NPPB", 0.023575072),
    ("NTF4", -0.132356723),
    ("NTPROBNP", 0.01812172),
    ("OCLN", 0.046941782),
    ("ODAM", -0.048970791),
    ("OPTC", -0.083726604),
    ("PEPD", -0.096547934),
    ("PRG3", -0.071408718),
    ("PRSS8", 0.111906716),
    ("PTGR1", -0.062176138),
    ("PTN", 0.027498932),
    ("RBFOX3", 0.116975605),
    ("REG3G", 0.123769062),
    ("REN", 0.068896784),
    ("SCG2", -0.137662829),
    ("SCG3", -0.047219443),
    ("SCGB1A1", -0.056378508),
    ("SCGB3A1", 0.265602762),
    ("SDC4", -0.115249658),
    ("SELENOP", -0.080153962),
    ("SELL", 0.014768758),
    ("SEZ6L", -0.045588135),
    ("SFRP1", 0.069474034),
    ("SFTPD", 0.037816669),
    ("SKAP1", -0.055014204),
    ("SLITRK1", 0.067015239),
    ("SLITRK2", -0.104542859),
    ("SOST", -0.123590138),
    ("SPOCK1", 0.164663205),
    ("SPON1", 0.130347786),
    ("SPP1", 0.123681499),
    ("TFF3", 0.11867381),
    ("TNC", 0.031169845),
    ("TNFRSF10B", 0.063336979),
    ("TNFRSF6B", 0.034805482),
    ("TNN", -0.098905845),
    ("TNR", -0.144461235),
    ("TPK1", -0.12734439),
    ("TTR", -0.020352303),
    ("TXNDC15", 0.079187131),
    ("VGF", -0.305091894),
    ("WFDC2", 0.11880077),
    ("XG", -0.08933844),
)

PAC_PROTEINS = tuple(symbol for symbol, _beta in PAC_PROTEIN_COEFFICIENTS)


def input_key(symbol: str) -> str:
    """skill.json key for one assay: lower case, '-' to '_', and the unit."""
    return symbol.lower().replace("-", "_") + "_npx"
