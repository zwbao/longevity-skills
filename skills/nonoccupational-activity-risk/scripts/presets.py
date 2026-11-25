"""Garcia et al., BJSM 2023: Methods intensity assumptions and Table 1 curves."""
from pathlib import Path

TITLE = "非职业活动量与人群相对风险"
BOUNDARY = '这是一般成年人人群观察研究的活动量—相对风险关联，不是个人患病概率、寿命或改变活动后的因果获益预测；不能据此开始或停止用药，也不构成运动处方。'
INTENSITIES = {"light_min_week": 1.5, "moderate_min_week": 3.5, "vigorous_min_week": 7.0}
MINUTES_PER_HOUR = 60
MAX_WEEK_MINUTES = 7 * 24 * 60  # Physical input sanity limit, not a paper risk threshold.
HIGH_ACTIVITY = 17.5
SPARSE_ACTIVITY = 35.0
TABLE_LEVELS = (4.375, 8.75, 17.5)
DATA = Path(__file__).resolve().parents[1] / "data"
OUTCOMES = {'all_cause_mortality': ('全因死亡', 'all-cause-mortality-fatal.csv'), 'cvd_mortality': ('心血管疾病死亡', 'all-cause-cvd-fatal.csv'), 'cancer_mortality': ('癌症死亡', 'all-cause-cancer-fatal.csv'), 'cvd_incidence': ('总心血管疾病发生', 'all-cause-cvd-fatal-and-non-fatal.csv'), 'chd_incidence': ('冠心病发生', 'coronary-heart-disease-fatal-and-non-fatal.csv'), 'stroke_incidence': ('卒中发生', 'stroke-fatal-and-non-fatal.csv'), 'heart_failure_incidence': ('心力衰竭发生', 'heart-failure-fatal-and-non-fatal.csv'), 'cancer_incidence': ('总癌症发生', 'all-cause-cancer-fatal-and-non-fatal.csv'), 'head_neck_incidence': ('头颈部癌发生', 'head-and-neck-cancer-fatal-and-non-fatal.csv'), 'myeloid_leukaemia_incidence': ('髓系白血病发生', 'myeloid-leukemia-fatal-and-non-fatal.csv'), 'myeloma_incidence': ('骨髓瘤发生', 'myeloma-fatal-and-non-fatal.csv'), 'gastric_cardia_incidence': ('胃贲门癌发生', 'gastric-cardia-cancer-fatal-and-non-fatal.csv'), 'lung_incidence': ('肺癌发生', 'lung-cancer-fatal-and-non-fatal.csv'), 'liver_incidence': ('肝癌发生', 'liver-cancer-fatal-and-non-fatal.csv'), 'endometrial_incidence': ('子宫内膜癌发生（女性研究）', 'endometrial-cancer-fatal-and-non-fatal.csv'), 'colon_incidence': ('结肠癌发生', 'colon-cancer-fatal-and-non-fatal.csv'), 'breast_incidence': ('乳腺癌发生（女性研究）', 'breast-cancer-fatal-and-non-fatal.csv'), 'bladder_incidence': ('膀胱癌发生', 'bladder-cancer-fatal-and-non-fatal.csv'), 'rectum_incidence': ('直肠癌发生', 'rectum-cancer-fatal-and-non-fatal.csv'), 'oesophageal_incidence': ('食管癌发生', 'esophageal-cancer-fatal-and-non-fatal.csv'), 'prostate_incidence': ('前列腺癌发生（男性研究）', 'prostate-cancer-fatal-and-non-fatal.csv'), 'kidney_incidence': ('肾癌发生', 'kidney-cancer-fatal-and-non-fatal.csv')}
