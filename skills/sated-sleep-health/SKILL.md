---
name: sated-sleep-health
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes the original five-item SATED sleep-health score from an adult's
  self-reported response categories. Use for SATED scoring or a brief sleep-health self-assessment;
  distinguishes reproduced scoring from the unvalidated status of the scale in the 2014 paper.
---

# 原始 SATED 睡眠健康自评

适用于愿意完成五项自评的成人，原题面针对典型夜间单段睡眠。遇到儿童、轮班或分段睡眠，先说明原题面的适用限制，不替换时间阈值或推断其健康好坏。

用户命令：

> 用我填写的五项 SATED 回答计算各项分数和总分，说明这个分数能说明什么。

## 收集回答

请用户按实际情况回答以下五项。中文为工作译文，不是经验证的中文版量表。

| CSV marker | 题意 |
| --- | --- |
| satisfaction_score | 你对自己的睡眠感到满意吗？ |
| alertness_score | 你能整天保持清醒而不打瞌睡吗？ |
| timing_score | 凌晨 2:00 至 4:00 之间，你在睡觉或尝试入睡吗？ |
| efficiency_score | 你夜间清醒总时间少于 30 分钟吗，包括入睡所需时间和睡后醒来的时间？ |
| duration_score | 你每天睡眠在 6 至 8 小时之间吗？ |

各项编码：0=很少／从不，1=有时，2=通常／总是。将明确回答录为 `marker,value,unit` CSV，单位为 `score`。不得把小时、分钟、手表分数或自己推断的频率填成档位；原图没有规定回忆周期或每周天数界值，不自行补充。时长题是原始历史题面，不是睡眠时长建议。

## 执行

```bash
python3 scripts/personal_report.py --measurements answers.csv --out out
```

可选 `--age`、`--sex` 不影响分数；年龄提供时仅限成人。`--targets targets.csv` 接受同列格式的一项或多项目标回答，只计算回答变化的分差。`out/levers.json` 列出每项可选档位的离散分差和目标情景，不能据此推断干预效果。

五项必须齐全。缺项、错单位、非整数、超范围、未知项目和文件无法读取均退出 3，查看 `out/problems.json` 后说明需要补充或改正的回答。成功后读取 `out/report.md`、`out/result.json`；不要另用心算生成结果。不要向用户索取论文、补图、队列或代码仓库。

## 报告约束

报告先放论文卡片，再列回答、分值和总分。仅复现 Figure S1 的选项分值，不声称复现了个人病例或证明了临床效度。不要添加中间分数的好坏分档、诊断阈值、疾病概率、预期寿命、剂量或启停药建议。

每份报告保留以下边界原句：

> 边界：这是 Buysse 2014 提出的原始五项 SATED 自评计分，原论文中尚未经过心理测量学验证；分值不是睡眠障碍诊断、疾病概率或寿命预测，不能据此开始或停止药物。原题面针对成人典型夜间单段睡眠，不直接推广至儿童、轮班或其他睡眠文化。
