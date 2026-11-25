"""Definitions from Ekelund et al., BMJ 2019, Methods and Supplementary Table 5."""

TITLE = "加速度计活动与久坐的死亡关联查表"
BOUNDARY = "这是观察性人群的相对危险比查表，不是你的死亡概率、寿命预测或改变活动后的因果获益；不能据此开始、停用或调整药物。"
PROTOCOL = "vertical-60s-harmonised"
MIN_AGE = 40
EPOCH_SECONDS = 60
MIN_VALID_DAYS = 4
MIN_WEAR_HOURS = 10
NONWEAR_ZERO_MINUTES = 90
NONWEAR_ALLOWANCE_MINUTES = 2
NONWEAR_FLANK_MINUTES = 30
# Actigraph intensity cutoffs, inclusive, in vertical-axis counts/minute.
ACTIGRAPH_CUTOFFS = {"sedentary": [0, 100], "light": [101, 1951],
                    "low_light": [101, 759], "high_light": [760, 1951],
                    "mvpa_from": 1952, "vigorous_from": 5725}
# Retain the paper's strict >1535, not >=1535, for Actical MVPA.
ACTICAL_MVPA_GREATER_THAN = 1535
MEASURES = {
    "total_activity_cpm": {"label": "总身体活动", "unit": "/min", "display_unit": "counts/min", "range": [75, 375]},
    "light_min_day": {"label": "轻强度活动", "unit": "min", "display_unit": "分钟/日", "range": [150, 450]},
    "low_light_min_day": {"label": "低轻强度活动", "unit": "min", "display_unit": "分钟/日", "range": [100, 325]},
    "high_light_min_day": {"label": "高轻强度活动", "unit": "min", "display_unit": "分钟/日", "range": [10, 120]},
    "mvpa_min_day": {"label": "中高强度活动", "unit": "min", "display_unit": "分钟/日", "range": [0, 24]},
    "sedentary_h_day": {"label": "久坐时间", "unit": "h", "display_unit": "小时/日", "range": [6, 12]},
}
