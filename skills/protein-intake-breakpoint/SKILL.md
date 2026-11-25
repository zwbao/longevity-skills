---
name: protein-intake-breakpoint
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Compares recorded total daily protein intake per body weight with the breakpoint
  printed in a resistance-training meta-analysis. Use when an adult provides food-record protein
  totals and body weight and asks where intake sits relative to the study plateau; reports scope and
  uncertainty in Chinese and accepts user-supplied scenarios.
---

# 总蛋白摄入与研究拐点

用户命令：“用我的每日总蛋白质记录和体重，看看与抗阻训练研究的蛋白摄入拐点是什么位置。”

输入 CSV 或 TSV，列名 `marker,value,unit`。必需两项：`protein_g_day`（g/d，每日平均食物与补充来源的蛋白质合计）和 `weight_kg`（kg，同期实际体重）。中文别名见 skill.json。体重也接受 g 或 lb。不要把蛋白粉的重量或血清总蛋白填成总摄入量。

```bash
python3 scripts/personal_report.py --measurements my-record.csv --age 40 --context healthy-ret --out out
```

`--age` 为实际年龄；不要照抄示例年龄。`--sex` 可选，不参与计算。`--context healthy-ret` 只在用户资料确认健康、非能量限制，且抗阻训练至少六周、每周至少两次时使用。不符合用 `other`，未确认用 `unknown`；不能默认符合。

`--targets my-scenario.csv` 接受相同表头的用户自填情景，可只填其中一项。不得由 agent 自动填一个“应达到”的蛋白量或体重。结果始终写入 `out/report.md`、`out/result.json`、`out/levers.json`。后者含当前值、两项输入对相对摄入量的局部敏感度、各项单独变化及合并情景的算术结果。没有目标文件时不生成目标建议。

缺项、错单位、越界、文件读入失败或无效参数值会退出 3，生成 `out/problems.json`，结果数值置空。读入范围是防错的工程范围；论文研究范围与临床正常范围不是同一件事。

使用 Morton 等发表于 British Journal of Sports Medicine 2018 的组水平拐点。计算所需常数随技能冻结于 `scripts/presets.py`；运行不联网，不向用户要论文、附件、队列或代码。只按印出拐点比较位置，不复拟合散点图，不预测去脂体重或力量增加，不用组水平年龄或训练经验斜率校正个人。

未确认研究情境或相对摄入量超出论文拐点分析的观察范围时，只输出摄入量除以体重，不分档。置信区间不是“合理摄入区间”，高于拐点也不证明个人已达到平台。论文没有完整的个人换算示例，验证保持 draft。

每份报告均以论文卡片开头，保留这句：

> 边界：仅将记录的总蛋白摄入与健康、非能量限制且持续抗阻训练成人研究中的组水平拐点比较；不是个人蛋白需要量、安全上限、增肌预测或补剂剂量建议，不能据此开始或停止药物。

来源、计算合同与未实现部分见 [references/contract.md](references/contract.md)、[references/claims.md](references/claims.md) 和 [references/sources.md](references/sources.md)。
