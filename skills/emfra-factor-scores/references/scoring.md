# 固定权重与计分来源

来源：[补充 R Quarto Script，第 5.3 节表 64](https://www.medrxiv.org/content/medrxiv/early/2026/11/16/2026.11.11.26367642/DC1/embed/media-1.pdf?download=true)。
列名原文为 `Item name`, `MR1`, `MR2`；表题为
“Factor score regression weights for Reduced Model C (tenBerge method).”

| 原版条目编号 | Item name | MR1 | MR2 |
| --- | --- | ---: | ---: |
| 1 | Grip strength | 0.233 | -0.011 |
| 2 | Gait speed | 0.405 | 0.034 |
| 5 | Fatigue | -0.054 | 0.157 |
| 6 | Arithmetic money | 0.172 | -0.009 |
| 7 | Atten-Inhib | 0.179 | 0.032 |
| 11 | Loneliness | 0.024 | 0.388 |
| 12 | Sadness | 0.009 | 0.510 |
| 15 | Life satisf. | 0.038 | -0.157 |
| 19 | Socio-Ludic act. | 0.234 | -0.068 |

原始编号及 `EMFRA_itemN_trait` 对应关系见补充第 1.1 节字典。
MR1 = Autonomy；MR2 = Psychological distress。
每个因子：对负权重对应的原始条目先算 `2-X`，再用权重绝对值加权求和。
正权重条目保持原值；两个因子都包含全部九项。没有标准化或额外截距。
脚本中的唯一计算权重源是 `scripts/presets.py`；本表保留出处以供人工核对。

表 65 列名原文：`Factor`, `Factor name`, `Minimum possible score`, `Maximum possible score`。

| Factor | Factor name | Minimum possible score | Maximum possible score |
| --- | --- | ---: | ---: |
| MR1 | Autonomy | 0 | 2.696 |
| MR2 | Psychological distress | 0 | 2.732 |

端点指每个因子各自重编码后的所有项全为 0 或全为 2，不是原始条目统一全为 0 或 2。
这两个因子的极值不要求在同一原始向量上同时实现。
