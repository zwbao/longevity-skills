"""Printed lookup constants: Aune et al., IJE 2017, Tables S8–S18.

Numerical rows are in data/lookup.csv; references and column identities in
data/curves.json. INPUT_RANGE is an input-error guard, not a paper cutoff.
"""
from pathlib import Path
import csv
import json

INPUT_KEY = "intake_g_d"
UNIT = "g/d"
INPUT_RANGE = (0, 3000)
FOODS = {"combined": "水果和蔬菜合计", "fruit": "水果", "vegetables": "蔬菜"}
OUTCOMES = {
    "coronary_heart_disease": "冠心病", "stroke": "总卒中",
    "ischemic_stroke": "缺血性卒中", "hemorrhagic_stroke": "出血性卒中",
    "cardiovascular_disease": "心血管疾病", "total_cancer": "总癌症",
    "all_cause_mortality": "全因死亡",
}
ENDPOINTS = {"mixed": "发病或死亡（合并分析）", "incidence": "发病", "mortality": "死亡"}
BOUNDARY = "这是前瞻性人群研究的观察性关联查表，不是个人患病或死亡概率，也不能证明改变摄入量会带来相同变化；不能据此开始或停止用药。"
MODEL_NOTE = "目标和敏感度只比较同一张表的关联值，不是饮食处方或个人获益预测；不插值、不外推，不把相邻行当成置信区间。"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CURVES = json.loads((DATA_DIR / "curves.json").read_text(encoding="utf-8"))
with (DATA_DIR / "lookup.csv").open(encoding="utf-8", newline="") as stream:
    ROWS = list(csv.DictReader(stream))


def series(food, outcome, endpoint):
    key = (food, outcome, endpoint)
    meta = next((c for c in CURVES if (c["food_group"], c["outcome"], c["endpoint"]) == key), None)
    if meta is None:
        raise ValueError("这组结局与分析类型不存在。卒中亚型只支持 mixed，全因死亡只支持 mortality。")
    points = [
        {k: float(row[k]) if row[k] else None for k in ("intake_g_d", "rr", "ci_low", "ci_high")}
        for row in ROWS if (row["food_group"], row["outcome"], row["endpoint"]) == key
    ]
    return dict(meta), points
