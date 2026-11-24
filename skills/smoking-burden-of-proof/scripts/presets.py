"""Dai et al. 2022, Table 2: frozen printed predictions, no interpolation."""
import json
from pathlib import Path

TABLE = json.loads((Path(__file__).resolve().parents[1] / "data/table2.json").read_text())
OUTCOMES = {row["key"]: row for row in TABLE["records"]}
INPUT_UNITS = {"pack_years": "a", "cigarettes_per_day": "1", "age": "a"}
# Operational typo guards, NOT fitted model coefficients or study exposure limits.
INPUT_RANGES = {"pack_years": [0, 300], "cigarettes_per_day": [0, 200], "age": [30, 110]}
TITLE = "吸烟烟史与疾病相对风险查表"
BOUNDARY = "这是当前吸烟者对应暴露水平的人群关联，不是个人患病概率、诊断或预期寿命；不能推算减量或戒烟后的获益，也不能据此开始或停止任何药物。"
SCENARIO_NOTE = "仅比较不同暴露史对应的表内人群关联；不代表同一个人改变吸烟后的效果。累计包年不能通过减量或戒烟倒退。论文没有局部导数，敏感度仅列邻近印出点的离散比较。"
