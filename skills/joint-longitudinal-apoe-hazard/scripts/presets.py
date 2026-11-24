"""Printed APOE log-hazard coefficients; no refitting or inferred constants.

Clapp Sullivan et al., medRxiv 2026, doi:10.64898/2026.11.06.26367441.
S1 HRS EUR, S3 HRS AFR, S4 HRS AMR: APOE e-4 status rows.
Total/level/change use Mediation Analysis; direct uses Model Parameters.
Intervals below are the printed per-allele 95% HR intervals, not recalculated.
"""

INPUT_KEY = "apoe_e4_count"
INPUT_UNIT = "1"
TITLE = "APOE ε4 与失智相对风险的认知路径"
BOUNDARY = (
    "预印本，未经同行评审；结果是所选研究人群模型中相对于 0 拷贝 APOE ε4 的关联性风险比，"
    "不是个人患病概率、诊断或因果效应，不能据此开始或停用药物。"
    "未验证东亚人群，不把祖源组别等同于国籍或自报族群。"
)
LABELS = {
    "total": "总关联",
    "level": "经病前认知水平的路径",
    "change": "经认知下降速度的路径",
    "direct": "模型中的剩余直接关联",
}
MODELS = {
    "EUR": {
        "label": "HRS 欧洲样祖源组", "table": "Table S1（与 S2 的 APOE 行一致）", "n": 10684,
        "beta": {"total": 0.683, "level": -0.013, "change": 0.633, "direct": 0.063},
        "ci_per_allele": {"total": (1.75, 2.24), "level": (0.92, 1.06),
                          "change": (1.59, 2.23), "direct": (0.92, 1.23)},
    },
    "AFR": {
        "label": "HRS 非洲样祖源组", "table": "Table S3", "n": 2240,
        "beta": {"total": 0.316, "level": 0.042, "change": 0.152, "direct": 0.122},
        "ci_per_allele": {"total": (1.11, 1.70), "level": (0.91, 1.19),
                          "change": (0.95, 1.43), "direct": (0.93, 1.38)},
    },
    "AMR": {
        "label": "HRS 美洲混合祖源组", "table": "Table S4", "n": 1697,
        "beta": {"total": 0.025, "level": -0.025, "change": 0.133, "direct": -0.084},
        "ci_per_allele": {"total": (0.74, 1.41), "level": (0.80, 1.20),
                          "change": (0.92, 1.42), "direct": (0.67, 1.26)},
    },
}
