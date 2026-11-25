"""Printed Appendix Tables 5, 7 and 8, Patterson et al., 2018.

CSV cells are transcribed from the publisher DOCX; no spline is reconstructed.
"""
import csv
from pathlib import Path

EXPOSURES = {'sitting': '总久坐', 'tv': '看电视'}
OUTCOMES = {'all_cause': '全因死亡', 'cvd': '心血管死亡',
            'cancer': '癌症死亡', 't2d': '新发2型糖尿病'}
THRESHOLDS = {
    ('sitting', 'all_cause'): (8, (1.01, 1.00, 1.01), (1.04, 1.03, 1.05)),
    ('sitting', 'cvd'): (6, (1.01, 0.99, 1.02), (1.04, 1.03, 1.04)),
    ('tv', 'all_cause'): (3.5, (1.03, 1.01, 1.04), (1.06, 1.05, 1.08)),
    ('tv', 'cvd'): (4, (1.02, 0.99, 1.04), (1.08, 1.05, 1.12)),
}
TABLES = {}
for exposure in EXPOSURES:
    TABLES[exposure] = {o: [] for o in OUTCOMES}
    with (Path(__file__).resolve().parents[1] / 'data' / f'{exposure}.csv').open() as f:
        for row in csv.DictReader(f):
            TABLES[exposure][row['outcome']].append({s: float(row[s]) for s in ('hours','rr','lci','uci')})

TITLE = '久坐与看电视时长的研究查表报告'
BOUNDARY = ('这是成人前瞻性队列荟萃分析的人群关联查表，不是个人发病或死亡概率、预期寿命、'
            '安全时长界限或减少久坐的因果效果；不能据此开始、停止或调整药物。')
NOTE = ('目标比较只是在同一张表上比较两个时长，不预测行为改变的个人收益。'
        '总久坐与看电视分别分析，风险不能相加或相乘。')
