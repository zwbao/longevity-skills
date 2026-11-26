---
name: ipaq-activity-score
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes the pace-specific short IPAQ weekly activity score from recalled activity
  days, duration, and walking pace. Use for a personal activity questionnaire readout or comparison of
  repeated questionnaires using the same recall period and scoring branch. Reports Chinese component
  scores and a total, with sitting time kept separate.
---

# IPAQ 短表每周活动量

读取 Craig 等（2003）的短表按步行速度计分分支。它是自报活动量汇总，主要用于人群监测；作者建议后续问卷删除速度问题。本技能不声称是后来的标准 IPAQ 评分器。

用户命令：

> 用我过去七天的体力活动记录，按 IPAQ 短表和我自报的步行速度算每周活动量，单列坐姿时间；如果我给了目标，也比较同一公式下的变化。

执行：

```bash
python3 scripts/personal_report.py --measurements activity.csv --age 40 --walking-pace moderate --out out
```

年龄和步行速度应替换为用户实际提供的资料，不能照搬示例。`--walking-pace` 必须是 `slow`（慢）、`moderate`（中等）或 `vigorous`（快／高强度），均为主观分类；不能从步数或时速推断。`--sex male/female` 可省略，不改变分数。正文研究适用范围为 18–65 岁，超出则停止。

CSV 使用 `marker,value,unit` 三列：

| marker | 含义 | 单位 |
|---|---|---|
| walking_days | 过去七天有合格步行的天数 | d |
| walking_min | 上述活动日平均步行时长 | min 或 h |
| moderate_days | 中等强度活动天数，不含步行 | d |
| moderate_min | 上述活动日平均中等强度活动时长 | min 或 h |
| vigorous_days | 高强度活动天数 | d |
| vigorous_min | 上述活动日平均高强度活动时长 | min 或 h |
| sitting_weekday_min | 可选：工作日平均坐姿时长 | min 或 h |

只统计每次持续至少 10 分钟的活动，覆盖工作、交通、家务和休闲。同一活动不要重复填入不同强度。天数为 0–7 的整数；活动时长是“有活动的日子平均多少分钟”，不是全周总分钟。无活动须明确填写天数和时长均为零；不知道或拒答不是零。不接受问卷中的 8/9、998/999 等缺失编码。可用清单所列中英文别名；有单位歧义时必须填写单位。

已完成问卷是首选输入；不要把本文件当作经验证的中文问卷译本。无需用户提供全文、补充表、队列或代码；权重已内置。只实现短表，不接受长表各领域数据混填。不使用后期 IPAQ 的分档和截断规则，也不输出健康达标判断。

目标文件用相同列，`--targets targets.csv` 可只给改变的数值。其余保持当前值，步行速度保持不变。目标要满足与当前输入相同的检查；同时改变天数与时长的情景可计算，单项变化若形成矛盾则在 `levers.json` 中标为不可计算。敏感度是公式斜率，天数仍只能取整数。

成功写入 `out/report.md`、`out/result.json` 和 `out/levers.json`。错误或缺项退出 3，写 `out/problems.json`，结果值为空，并清除本输出目录中旧的结果。不要把 null 当作零。报告从论文卡片开始，随后解释个人结果及 draft 验证限制。

每份报告保留原样边界句：

> 边界: 这是自报活动量的加权汇总，不是实际热量消耗、健康达标判断、疾病风险或寿命预测；目标情景只是算术比较，不能据此开始或停止用药。

来源、范围及未复现事项见 [references/contract.md](references/contract.md)；研究证据与样本见 [references/claims.md](references/claims.md)。
