"""Sun et al., Lancet Public Health 2022, Methods / Table 1 / Tables S3-S4.

All study constants are transcribed, not estimated. Frequencies are days
within a fixed seven-day week, summarizing habitual intake over 12 months.
"""
FREQUENCY_UNIT = "d"
# key, Chinese name, inclusive minimum and maximum days meeting the criterion
FOODS = (
    ("fresh_vegetables_days_per_week", "新鲜蔬菜", 7, 7),
    ("fresh_fruit_days_per_week", "新鲜水果", 7, 7),
    ("red_meat_days_per_week", "红肉", 1, 6),
    ("legumes_days_per_week", "豆类", 4, 7),
    ("fish_days_per_week", "鱼", 1, 7),
)
LOW_RISK_MIN = 4
DERIVATION_AGES = (30, 79)
OUTCOMES = (("all_cause", "全因死亡"), ("cvd", "心血管病死亡"), ("cancer", "癌症死亡"))
TABLES = {"pooled": "Table 1", "male": "Table S3", "female": "Table S4"}
POPULATIONS = {"pooled": "男女合并", "male": "男性", "female": "女性"}
REFERENCE = ((1.00, None, None),) * 3  # No confidence interval printed for referent.
# Rows: diet score 0-1, 2, 3, 4, 5. Columns: all-cause, CVD, cancer.
# Each cell: HR, lower 95% CI, upper 95% CI. These are Cox HRs, not Table S7 sHRs.
HAZARD_RATIOS = {
    "pooled": (
        REFERENCE,
        ((0.90, 0.88, 0.92), (0.88, 0.84, 0.91), (0.95, 0.91, 0.99)),
        ((0.84, 0.81, 0.87), (0.81, 0.77, 0.85), (0.92, 0.87, 0.98)),
        ((0.80, 0.76, 0.84), (0.73, 0.67, 0.79), (0.92, 0.85, 1.00)),
        ((0.74, 0.65, 0.85), (0.62, 0.49, 0.80), (0.80, 0.64, 0.99)),
    ),
    "male": (
        REFERENCE,
        ((0.90, 0.87, 0.93), (0.86, 0.81, 0.91), (0.96, 0.91, 1.02)),
        ((0.87, 0.83, 0.90), (0.84, 0.78, 0.90), (0.96, 0.89, 1.03)),
        ((0.85, 0.79, 0.91), (0.79, 0.71, 0.89), (0.94, 0.85, 1.05)),
        ((0.78, 0.65, 0.94), (0.64, 0.46, 0.89), (0.90, 0.68, 1.20)),
    ),
    "female": (
        REFERENCE,
        ((0.90, 0.87, 0.94), (0.91, 0.85, 0.96), (0.92, 0.85, 0.99)),
        ((0.81, 0.77, 0.85), (0.79, 0.73, 0.86), (0.87, 0.79, 0.95)),
        ((0.75, 0.70, 0.81), (0.70, 0.62, 0.80), (0.88, 0.78, 0.99)),
        ((0.71, 0.58, 0.88), (0.64, 0.44, 0.93), (0.67, 0.48, 0.93)),
    ),
}
BOUNDARY = "这是观察性研究的饮食评分和分组人群关联，不是你的死亡概率、个人预期寿命或改变饮食后的因果收益；不能据此开始或停止任何药物。"
