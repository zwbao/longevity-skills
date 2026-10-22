"""LinAge, the linear clinical clock of Fong et al., Nature Aging 2024 (doi:10.1038/s43587-024-00646-8).

Every number below is copied from the paper's supplementary files (CC BY 4.0):
PARAMS, CHRON_AGE_BETA_PER_MONTH and C1 from linAge_Paras.csv (MOESM11, the
machine-readable Supplementary Table 7: sex-specific median and MAD of the
"healthy aging" cluster and the weight of each of the 61 parameters); the
derived scores, cotinine bins, LDL formula, log transforms and the 40-84 age
window from linAge.R (MOESM12); the model equation from the Methods and the
linAge_XLS readme (MOESM7):

    deltaBioAge = C1 + beta_0 * chronAge(months) + sum(beta_i * (x_i - median_i) / MAD_i)
    LinAge = chronAge(years) + deltaBioAge

Parameters without a median (cotinine bin, basophil count, the three derived
indices) enter unnormalized, as linAge.R does (median 0, MAD 1). A missing
parameter contributes 0, the paper's rule ("a zero z-score can be substituted
for missing values after normalization", Methods); its error is of the order
of that parameter's weight.
"""

from __future__ import annotations

import math

BOUNDARY = (
    "这是研究复现意义上的个人读出，不是诊断，也不是治疗建议。不能据此开始或停止任何药物。"
    "单项权重是死亡风险模型里的统计权重，不是改善目标。体检不增删方法算出的名单。"
)

DOI = "10.1038/s43587-024-00646-8"
# linAge.R: keepMe <- (RIDAGEYR >= 40 & RIDAGEYR < 85); LinAge was trained on 40-84 years.
AGE_MIN = 40
AGE_BELOW = 85
MONTHS_PER_YEAR = 12

PARAMS = (
    # (NHANES name, key here, transform, (median, MAD, beta) men, (median, MAD, beta) women)
    ('BPXPLS', 'pulse_per_min', None, (66.0, 8.9, 0.8006), (68.0, 8.9, 1.0792)),
    ('BPXSAR', 'sbp_mmhg', None, (127.0, 16.31, 1.7638), (125.0, 20.76, 1.2637)),
    ('BPXDAR', 'dbp_mmhg', None, (75.0, 10.38, -0.485), (73.0, 8.9, 0.0068)),
    ('BMXBMI', 'bmi_kg_m2', None, (26.3, 2.43, -0.0569), (24.57, 2.08, -0.4598)),
    ('LBDIRNSI', 'iron_umol_l', None, (16.65, 5.57, 0.2438), (15.57, 6.09, 0.0743)),
    ('LBDTIBSI', 'tibc_umol_l', None, (62.47, 9.01, 0.2293), (66.59, 10.48, -0.4431)),
    ('LBXPCT', 'tsat_pct', None, (26.5, 8.9, 0.189), (23.55, 9.12, 0.2854)),
    ('LBDFERSI', 'ferritin_ug_l', None, (134.0, 103.78, -0.3941), (64.5, 58.56, 0.2913)),
    ('LBDFOLSI', 'folate_nmol_l', None, (31.0, 15.12, 0.6654), (35.3, 16.75, -0.371)),
    ('LBDB12SI', 'b12_pmol_l', None, (333.58, 130.2, -0.0174), (389.66, 189.29, -0.0203)),
    ('LBXCOT', 'cotinine_ng_ml', 'cotinine_bins', (None, None, 0.9828), (None, None, 1.1906)),
    ('LBDTCSI', 'tc_mmol_l', None, (5.33, 0.92, 0.3847), (5.38, 0.85, -0.151)),
    ('LBDHDLSI', 'hdl_mmol_l', None, (1.17, 0.31, 0.5512), (1.5, 0.39, 0.9171)),
    ('LBXWBCSI', 'wbc_10e9_l', None, (6.6, 1.63, 0.3903), (6.3, 1.63, 0.3447)),
    ('LBXLYPCT', 'lymph_pct', None, (28.3, 7.41, -0.0078), (31.4, 7.56, 0.0362)),
    ('LBXMOPCT', 'mono_pct', None, (8.5, 1.78, -0.3965), (7.7, 1.63, -0.2868)),
    ('LBXNEPCT', 'neut_pct', None, (59.2, 8.15, 0.0868), (57.3, 8.38, 0.0015)),
    ('LBXEOPCT', 'eos_pct', None, (2.5, 1.33, -0.1064), (2.0, 1.19, 0.419)),
    ('LBXBAPCT', 'baso_pct', None, (0.6, 0.3, 0.6472), (0.6, 0.3, -0.3984)),
    ('LBDLYMNO', 'lymph_10e9_l', None, (1.8, 0.59, 0.3601), (1.9, 0.59, 0.4247)),
    ('LBDMONO', 'mono_10e9_l', None, (0.6, 0.15, -0.0739), (0.5, 0.15, -0.0627)),
    ('LBDNENO', 'neut_10e9_l', None, (3.8, 1.19, 0.3672), (3.6, 1.19, 0.2602)),
    ('LBDBANO', 'baso_10e9_l', None, (None, None, 0.029), (None, None, -0.0024)),
    ('LBXRBCSI', 'rbc_10e12_l', None, (4.93, 0.37, -0.3623), (4.4, 0.33, 0.0468)),
    ('LBXHGB', 'hgb_g_dl', None, (15.2, 0.89, -0.0076), (13.7, 1.04, 0.3208)),
    ('LBXHCT', 'hct_pct', None, (45.1, 2.67, 0.0234), (40.3, 2.97, 0.4149)),
    ('LBXMCVSI', 'mcv_fl', None, (91.5, 3.85, 0.7502), (91.6, 3.93, 0.6093)),
    ('LBXMCHSI', 'mch_pg', None, (31.0, 1.48, 0.6207), (31.3, 1.48, 0.411)),
    ('LBXMC', 'mchc_g_dl', None, (33.8, 0.74, -0.1101), (34.0, 0.74, -0.2698)),
    ('LBXRDW', 'rdw_pct', None, (12.5, 0.59, 1.9329), (12.4, 0.59, 1.4199)),
    ('LBXPLTSI', 'plt_10e9_l', None, (237.0, 50.41, -0.4788), (264.0, 65.23, -0.1163)),
    ('LBXMPSI', 'mpv_fl', None, (8.2, 0.89, 0.8348), (8.1, 0.74, -0.1797)),
    ('LBXCRP', 'crp_mg_dl', 'ln', (-1.97, 1.03, 0.9396), (-1.56, 1.1, 0.9428)),
    ('LBDFBSI', 'fibrinogen_g_l', None, (3.4, 0.61, 1.0257), (3.46, 0.62, 1.2387)),
    ('LBXGH', 'hba1c_pct', None, (5.4, 0.3, 0.044), (5.3, 0.3, 0.1086)),
    ('SSBNP', 'ntprobnp_pg_ml', 'ln', (3.81, 1.19, 1.7226), (4.3, 0.91, 1.7577)),
    ('LBDSALSI', 'albumin_g_l', None, (44.0, 2.97, -0.4833), (43.0, 2.97, -0.6401)),
    ('LBXSATSI', 'alt_u_l', None, (24.0, 7.41, -1.6351), (18.0, 5.93, -1.0532)),
    ('LBXSASSI', 'ast_u_l', None, (24.0, 5.93, 1.1366), (22.0, 5.93, 1.5262)),
    ('LBXSAPSI', 'alp_u_l', None, (70.0, 20.76, -0.1903), (67.0, 19.27, 0.4288)),
    ('LBDSBUSI', 'urea_mmol_l', None, (5.4, 1.48, -0.3801), (4.64, 1.54, 0.3013)),
    ('LBDSCASI', 'calcium_mmol_l', None, (2.35, 0.07, 0.4501), (2.35, 0.11, -0.0054)),
    ('LBXSC3SI', 'bicarbonate_mmol_l', None, (24.0, 2.97, -0.3404), (24.0, 1.48, 0.3577)),
    ('LBXSGTSI', 'ggt_u_l', None, (25.0, 11.86, 0.1972), (18.0, 7.41, 0.0745)),
    ('LBDSGLSI', 'glucose_mmol_l', None, (5.16, 0.49, 0.3585), (4.91, 0.45, 0.4584)),
    ('LBXSLDSI', 'ldh_u_l', None, (137.0, 25.2, 0.2753), (137.0, 28.17, -0.0588)),
    ('LBDSPHSI', 'phosphorus_mmol_l', None, (1.1, 0.15, 0.1301), (1.16, 0.14, 0.1654)),
    ('LBDSTBSI', 'tbil_umol_l', None, (11.97, 2.56, 0.1548), (10.26, 2.54, -0.7655)),
    ('LBDSTPSI', 'total_protein_g_l', None, (74.0, 4.45, 0.3662), (74.0, 4.45, -0.9744)),
    ('LBDSTRSI', 'tg_mmol_l', None, (1.42, 0.75, 1.1103), (1.2, 0.6, -0.5964)),
    ('LBDSUASI', 'uric_acid_umol_l', None, (345.0, 79.32, 0.6415), (261.7, 61.68, 0.9131)),
    ('LBDSCRSI', 'creatinine_umol_l', None, (79.6, 13.2, -0.3536), (61.88, 13.11, -0.1335)),
    ('LBXSNASI', 'sodium_mmol_l', None, (139.5, 2.22, -0.2775), (139.0, 2.97, 0.5501)),
    ('LBXSKSI', 'potassium_mmol_l', None, (4.11, 0.31, 0.4169), (4.0, 0.3, 0.7207)),
    ('LBXSCLSI', 'chloride_mmol_l', None, (102.7, 2.52, -0.47), (102.6, 2.52, 0.3513)),
    ('LBDSGBSI', 'globulin_g_l', None, (30.0, 4.45, 0.6748), (30.0, 4.45, -0.5466)),
    ('fs1Score', 'comorbidity_index', None, (None, None, 0.0492), (None, None, 0.0717)),
    ('fs2Score', 'self_health_index', None, (None, None, 0.6674), (None, None, 1.3017)),
    ('fs3Score', 'healthcare_use_code', None, (None, None, -0.048), (None, None, 0.9043)),
    ('LDLV', 'ldl_mmol_l', None, (3.76, 0.87, 0.0337), (3.53, 0.78, -0.3884)),
    ('crAlbRat', 'acr_mg_g', None, (5.3, 3.15, 0.001), (7.1, 4.7, 0.0044)),
)
CHRON_AGE_BETA_PER_MONTH = {'male': -0.0183, 'female': -0.0075}
C1 = {'male': 7.46, 'female': -1.71}

# linAge.R digiCot(): 0 <= cot < 10 non-smoker 0; 10-<100 light 1; 100-<200 moderate 2; >= 200 heavy 3.
COTININE_BINS = (
    (10.0, 0, "不吸烟"),
    (100.0, 1, "轻度吸烟"),
    (200.0, 2, "中度吸烟"),
)
HEAVY_SMOKER_SCORE = 3

# linAge.R populateLDL(): LDL = TC - TG/5 - HDL, all in mmol/L, as the authors wrote it.
LDL_TG_DIVISOR = 5.0

# Methods and linAge.R popPCFIfs1(): 22 yes/no items, index = number of yes / 22.
# (key, label, NHANES 1999-2000 item the paper used, as the NHANES codebook words it)
COMORBIDITIES = (
    ("hypertension", "高血压", "BPQ020 医生说过有高血压"),
    ("diabetes_mellitus", "糖尿病", "DIQ010 医生说过有糖尿病，包括临界糖尿病"),
    ("renal_impairment", "肾功能损害", "KIQ020 医生说过肾功能弱或衰竭（不算肾结石、膀胱感染、尿失禁）"),
    ("asthma", "哮喘", "MCQ010 医生说过有哮喘"),
    ("anemia", "贫血", "MCQ053 最近三个月在治疗贫血（含饮食、铁剂、输血）"),
    ("arthritis", "关节炎", "MCQ160A 医生说过有关节炎"),
    ("coronary_heart_disease", "冠心病", "MCQ160C 医生说过有冠心病"),
    ("angina", "心绞痛", "MCQ160D 医生说过有心绞痛"),
    ("previous_myocardial_infarction", "既往心肌梗死", "MCQ160E 医生说过心脏病发作"),
    ("previous_stroke", "既往卒中", "MCQ160F 医生说过中风"),
    ("emphysema", "肺气肿", "MCQ160G 医生说过有肺气肿"),
    ("thyroid_disease", "甲状腺疾病", "MCQ160I 医生说过有甲状腺疾病"),
    ("obesity", "肥胖", "MCQ160J 医生说过超重"),
    ("chronic_bronchitis", "慢性支气管炎", "MCQ160K 医生说过有慢性支气管炎"),
    ("liver_disease", "肝病", "MCQ160L 医生说过有任何肝病"),
    ("malignancy", "恶性肿瘤", "MCQ220 医生说过有癌症或恶性肿瘤"),
    ("previous_hip_fracture", "既往髋部骨折", "OSQ010A 髋部骨折过"),
    ("previous_wrist_fracture", "既往腕部骨折", "OSQ010B 腕部骨折过"),
    ("previous_spine_fracture", "既往脊柱骨折", "OSQ010C 脊柱骨折过"),
    ("osteoporosis", "骨质疏松", "OSQ060 医生说过有骨质疏松"),
    ("cognitive_impairment", "认知损害", "PFQ056 因记忆困难或阵发糊涂而在生活中受限"),
    ("overnight_hospitalization", "过夜住院", "HUQ070 过去一年住院过夜"),
)
COMORBIDITY_DENOMINATOR = 22

# Methods and linAge.R popPCFIfs2(): HUQ010 fair (4) or poor (5); HUQ020 better (1) or worse (2) than a year ago.
SELF_HEALTH_KEYS = ("fair_general_health", "poor_general_health", "better_current_health", "worse_current_health")

# Methods: healthcare use index = NHANES HUQ050 code. NHANES 1999-2000 codebook (HUQ):
# 0 none, 1 once, 2 "2 to 3", 3 "4 to 9", 4 "10 to 12", 5 "13 or more"; linAge.R sets 77/99 to 0.
HUQ050_BANDS = ((0, 0), (1, 1), (3, 2), (9, 3), (12, 4))
HUQ050_TOP = 5


def smoking_score(cotinine_ng_ml: float) -> int:
    for upper, score, _label in COTININE_BINS:
        if cotinine_ng_ml < upper:
            return score
    return HEAVY_SMOKER_SCORE


def smoking_label(score: int) -> str:
    for _upper, value, label in COTININE_BINS:
        if value == score:
            return label
    return "重度吸烟"


def comorbidity_index(present: int) -> float:
    return present / COMORBIDITY_DENOMINATOR


def self_health_index(fair: float, poor: float, better: float, worse: float) -> float:
    # Methods: ((fair x 2) + (poor x 4)) x (1 - (better x 0.5) + worse)
    return ((fair * 2.0) + (poor * 4.0)) * (1.0 - (better * 0.5) + worse)


def huq050_from_visits(visits: float) -> int:
    for upper, code in HUQ050_BANDS:
        if visits <= upper:
            return code
    return HUQ050_TOP


def ldl_mmol_l(tc: float, tg: float, hdl: float) -> float:
    return tc - tg / LDL_TG_DIVISOR - hdl


def transformed(transform, value: float) -> float:
    if transform == "ln":
        return math.log(value)
    if transform == "cotinine_bins":
        return float(smoking_score(value))
    return value


def linage(values: dict, sex: str, age_years: float) -> dict:
    """LinAge for one person.

    values: key -> value in the units of skill.json (raw, before log or bins),
    including comorbidity_index, self_health_index, healthcare_use_code,
    ldl_mmol_l and acr_mg_g. A key that is absent contributes 0.
    """
    column = 0 if sex == "male" else 1
    terms, missing = {}, []
    for code, key, transform, men, women in PARAMS:
        median, mad, beta = (men, women)[column]
        if key not in values:
            missing.append((key, abs(beta)))
            terms[key] = 0.0
            continue
        x = transformed(transform, values[key])
        z = x if median is None else (x - median) / mad
        terms[key] = beta * z
    total = sum(terms.values())
    delta = C1[sex] + CHRON_AGE_BETA_PER_MONTH[sex] * age_years * MONTHS_PER_YEAR + total
    return {"delta": delta, "linage": age_years + delta, "sum_terms": total, "terms": terms, "missing": missing}
