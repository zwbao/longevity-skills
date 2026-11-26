"""Constants and published rows: Aune et al., BMJ 2016, Appendix 1 pp. 69–70."""
import csv
from pathlib import Path

INPUT_KEY = "whole_grain_food_g_d"
INPUT_UNIT = "g/d"
# Engineering plausibility range, NOT a clinical threshold or model support limit.
INPUT_RANGE = (0, 1500)
BOUNDARY = "这是前瞻性队列荟萃分析的群体关联查表，不是个人死亡概率、寿命预测或增加摄入后的因果收益；不能据此开始或停止药物，也不提供用药剂量或饮食处方。"
OUTCOMES = {'coronary_heart_disease': '冠心病（发病或死亡）', 'stroke': '卒中（发病或死亡）', 'cardiovascular_disease': '心血管疾病（发病或死亡）', 'cancer_mortality': '癌症死亡', 'all_cause_mortality': '全因死亡', 'respiratory_mortality': '呼吸系统疾病死亡', 'diabetes_mortality': '糖尿病死亡', 'infectious_mortality': '感染性疾病死亡', 'nervous_system_mortality': '神经系统疾病死亡', 'non_cvd_non_cancer_mortality': '非心血管、非癌症原因死亡'}
TABLES = {}
with (Path(__file__).resolve().parents[1] / "data/nonlinear_rr.csv").open() as source:
    for row in csv.DictReader(source):
        TABLES.setdefault(row["outcome"], []).append({
            "g_d": float(row["g_d"]), "rr": float(row["rr"]),
            "ci_low": float(row["ci_low"]) if row["ci_low"] else None,
            "ci_high": float(row["ci_high"]) if row["ci_high"] else None,
        })
