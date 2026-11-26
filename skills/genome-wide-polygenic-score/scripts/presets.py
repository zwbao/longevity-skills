"""Published v3 model inventory; source and checksums in references/weights.json."""
import json
from pathlib import Path

MODELS = json.loads((Path(__file__).resolve().parents[1] / "references/weights.json").read_text())
DOSAGE_UNIT = "1"
DOSAGE_RANGE = (0, 2)
TITLE = "全基因组多基因原始评分"
BOUNDARY = ("这是研究用的原始遗传加权分数，不是个人患病概率、风险百分位或单基因突变诊断；"
            "不能据此开始或停止用药，也不能据此决定筛查方案。")
