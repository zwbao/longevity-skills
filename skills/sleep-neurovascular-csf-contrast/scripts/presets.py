"""Frozen S3 coefficients; see references/contract.md for scope and provenance."""
TITLE = "NREM 神经血管模型的脑脊液功率对比"
BOUNDARY = "这是横断面研究模型在同年龄组、同测量流程下的条件功率对比，不是个人实测脑脊液流量、废物清除效率、脑龄或痴呆风险，也不能预测改善睡眠或任何干预的效果；不能据此开始或停止药物。"
COEFFICIENTS = {"eeg_nrem_power_ratio": 0.804, "bold_nrem_power_ratio": 0.610}
RATIO_KEYS = tuple(COEFFICIENTS)
# Engineering input guard, not a clinical cutoff: permits +/-30 dB.
RATIO_RANGE = (0.001, 1000)
# Methods, nighttime retained sample; excludes unstudied middle-age gap.
AGE_GROUPS = ((18, 39), (60, 83))
EEG_BAND_HZ = (0.5, 4)
BOLD_BAND_HZ = (0.01, 0.1)
FRONTAL_ELECTRODES = ("F3", "F4", "F7", "F8", "Fz", "FT9", "FT10")

