"""Ding et al. 2025: Table 2 p e676 and corrected Table S8 p82, exact points only."""
import csv
from pathlib import Path

TITLE = "日均步数与健康结局查表"
INPUT_KEY = "daily_steps_per_day"
INPUT_UNIT = "1"  # Count within a fixed one-day window; not a rate conversion.
PLAUSIBLE_RANGE = (0, 100000)  # Software sanity limits, not fitted cutoffs.
BOUNDARY = "这是前瞻性观察研究荟萃分析中的人群关联，不是个人发病或死亡概率，也不证明增加步数会带来相同获益；不能据此决定开始或停止用药。"
OUTCOMES = {'all_cause_mortality': '全因死亡', 'cvd_incidence': '心血管疾病发病', 'cvd_mortality': '心血管疾病死亡', 'cancer_incidence': '癌症发病', 'cancer_mortality': '癌症死亡', 'type2_diabetes': '2型糖尿病发病', 'dementia': '痴呆', 'depressive_symptoms': '抑郁症状', 'falls': '跌倒'}
CERTAINTY = {'all_cause_mortality': '中等', 'cvd_incidence': '中等', 'cvd_mortality': '低', 'cancer_incidence': '低', 'cancer_mortality': '中等', 'type2_diabetes': '中等', 'dementia': '中等', 'depressive_symptoms': '中等', 'falls': '极低'}
TABLES = {2000: {}, 7000: {}}
with (Path(__file__).resolve().parents[1] / "data/printed_hr.csv").open() as stream:
    for row in csv.DictReader(stream):
        table = TABLES[int(row["reference_steps_per_day"])]
        cells = table.setdefault(int(row[INPUT_KEY]), {})
        cells[row["outcome"]] = tuple(float(row[k]) if row[k] else None for k in ("hr", "ci_lower", "ci_upper"))
TABLE_LABELS = {2000: "正文表 2（主要分析）", 7000: "更正后补表 8（事后分析）"}
