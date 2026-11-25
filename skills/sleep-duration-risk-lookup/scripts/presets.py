"""Yin et al., JAHA 2017, DOI 10.1161/jaha.117.005947, Table 2 only.

Each cell is (RR, 95% CI lower, 95% CI upper). None preserves unprinted cells.
These are selected predictions from a nonlinear meta-analysis, not categories.
"""
TITLE = "睡眠时长与死亡及心血管风险查表"
INPUT_KEY = "sleep_duration_h"
INPUT_UNIT = "h"
PLAUSIBLE_RANGE = (0, 24)  # Input sanity check, not a paper risk cutoff.
REFERENCE_H = 7
BOUNDARY = "这是前瞻性队列荟萃分析中的人群关联，不是个人发病或死亡概率，也不证明改变睡眠会降低风险；不能据此决定开始或停止用药。"
OUTCOMES = {
    "all_cause_mortality": "全因死亡",
    "total_cvd": "总心血管疾病（混合发病与死亡结局）",
    "chd": "冠心病（混合发病与死亡结局）",
    "stroke": "卒中（混合发病与死亡结局）",
}
TABLE_2 = {
    3: ((1.12, 1.10, 1.14), (1.14, 1.09, 1.19), None, None),
    4: ((1.08, 1.06, 1.09), (1.09, 1.06, 1.13), (1.16, 1.09, 1.23), (1.05, 0.96, 1.15)),
    5: ((1.04, 1.03, 1.05), (1.05, 1.03, 1.08), (1.11, 1.06, 1.16), (1.02, 0.96, 1.08)),
    6: ((1.01, 1.00, 1.01), (1.02, 1.00, 1.03), (1.05, 1.03, 1.08), (0.99, 0.96, 1.03)),
    7: ((1.00, None, None),) * 4,
    8: ((1.04, 1.04, 1.05), (1.03, 1.02, 1.05), (1.01, 0.99, 1.03), (1.08, 1.06, 1.11)),
    9: ((1.15, 1.14, 1.16), (1.16, 1.13, 1.19), (1.14, 1.08, 1.20), (1.30, 1.24, 1.37)),
    10: ((1.32, 1.29, 1.35), (1.37, 1.29, 1.45), (1.34, 1.20, 1.50), (1.64, 1.47, 1.82)),
    11: ((1.53, 1.47, 1.59), None, None, None),
}
