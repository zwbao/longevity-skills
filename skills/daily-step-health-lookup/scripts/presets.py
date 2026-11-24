"""Published lookup cells: Ding et al. 2025, Table 2, p e676."""
import json
from pathlib import Path

STEP_MIN, STEP_MAX, STEP_INCREMENT = 2000, 12000, 1000
REFERENCE_STEPS = 2000
ADULT_MIN = 18  # Methods: adults aged 18 years and older.
AGE_MAX = 120  # Input sanity guard, NOT an upper study eligibility cutoff.
STEP_UNIT = "1"  # Dimensionless count in a fixed one-day window; see contract.
BOUNDARY = "这是按你的日均步数定位的人群观察性关联，不是个人发病概率、寿命预测或增加步数的因果效果；不能据此开始、停用或调整药物。"
OUTCOMES = {
    "all_cause_mortality": ("全因死亡", "中等", 14, 161176),
    "cvd_incidence": ("心血管病发生", "中等", 6, 111349),
    "cvd_mortality": ("心血管病死亡", "低", 3, 120758),
    "cancer_incidence": ("癌症发生", "低", 2, 100505),
    "cancer_mortality": ("癌症死亡", "中等", 3, 105660),
    "diabetes_incidence": ("2 型糖尿病发生", "中等", 4, 61594),
    "dementia": ("痴呆", "中等", 2, 79699),
    "depressive_symptoms": ("抑郁症状", "中等", 3, 77565),
    "falls": ("跌倒（老年人群证据）", "极低", 4, 94901),
}
TABLE = {int(k): v for k, v in json.loads(
    (Path(__file__).resolve().parents[1] / "data/table2.json").read_text()
)["rows"].items()}


def output_specs():
    specs = {
        "steps_per_day": ("输入日均步数", STEP_UNIT),
        "reference_steps_per_day": ("共同参照日均步数", STEP_UNIT),
        "lower_steps_per_day": ("下侧表行步数", STEP_UNIT),
        "upper_steps_per_day": ("上侧表行步数", STEP_UNIT),
        "lookup_mode": ("查表方式：exact 为命中，bracket 为相邻两行", ""),
    }
    for key, (label, _, _, _) in OUTCOMES.items():
        for side, side_label in (("lower", "下侧表行"), ("upper", "上侧表行")):
            for stat, stat_label in (("hr", "HR"), ("ci_low", "95% CI 下限"), ("ci_high", "95% CI 上限")):
                specs[f"{key}_{side}_{stat}"] = (f"{label}：{side_label}{stat_label}", "1")
    return specs
