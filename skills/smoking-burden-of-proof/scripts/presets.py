"""Frozen Table 2 risks; source and scope are documented in references/."""
import json
from pathlib import Path

TABLE = json.loads((Path(__file__).resolve().parents[1] / "data/table2.json").read_text())
INPUT_UNITS = {
    "current_smoker": "1",
    "equivalent_smoking_years": "a",
    "daily_cigarette_count": "1",
    "age": "a",
}
TITLE = "吸烟暴露与疾病相对风险查表"
BOUNDARY = "本结果是当前吸烟者相对于从不吸烟者的人群关联，不是个人发病概率；不能预测减量或戒烟后的获益，不能据此开始或停止任何药物。"


def lookup(outcome, exposure):
    """Return only an exactly printed point. No rounding or interpolation."""
    row = TABLE[outcome]
    for point, values in row["points"].items():
        if exposure == float(point):
            return {**values, "star_rating": row["star_rating"]}
    raise ValueError("暴露值不在表2印出的点上")
