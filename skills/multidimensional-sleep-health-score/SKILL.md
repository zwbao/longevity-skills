---
name: multidimensional-sleep-health-score
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Scores one person's week of sleep on the six-domain sleep health score used by Marent
  et al. (GeroScience 2026, PASOCA cohort, adults aged 55 and over): wearable sleep duration 6-8 h,
  sleep efficiency at least 85%, sleep midpoint between 02:00 and 04:00, night-to-night midpoint SD
  under 60 min, and two PSQI items (overall sleep quality, trouble staying awake), one point each,
  total 0-6. Use for 睡眠健康评分, 睡眠健康分, 手环睡眠打分, 睡眠效率, 睡眠中点, 作息规律, multidimensional sleep health. States
  that the paper found no association of this score with memory, executive function or processing
  speed, so it does not predict cognition or dementia risk, and never advises starting or stopping a
  medicine or sleep aid.
---

# 六维睡眠健康评分（0–6 分）

用户交手环或手表一周的睡眠汇总和两道 PSQI 题的答案，年龄可选。不要向用户要论文、PDF 或补充表；切点已经在 `scripts/presets.py`。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" --measurements sleep_week.csv --age 66 --out out/
```

`sleep_week.csv` 的列是 `item,value,unit`，六项都要：

- `sleep_duration_h` 睡眠时长（h；写分钟时单位列写 `min`）
- `sleep_efficiency_pct` 睡眠效率（%；写成 0.86 时单位列写 `1`）
- `sleep_midpoint_clock_h` 睡眠中点（小数钟点，03:30 写 3.5；GGIR 的 27.5 也按 03:30 读）
- `sleep_midpoint_sd_min` 各晚睡眠中点的标准差（min；写小时时单位列写 `h`）
- `psqi_sleep_quality_code` PSQI 总体睡眠质量：0 非常好、1 尚好、2 不好、3 非常差
- `psqi_trouble_awake_code` PSQI 开车、吃饭或社交时难以保持清醒：0 过去一个月没有、1 每周少于 1 次、2 每周 1–2 次、3 每周 3 次或以上

中文叫法（睡眠时长、睡眠效率、睡眠中点、睡眠中点标准差……）也认，`skill.json` 列出全部。缺一项、单位不认识、数值超出范围、答案代码不是 0–3 的整数时不计算：报告写明哪一行为什么停，脚本退出码 3，并写 `out/problems.json`。`out/result.json` 给出 `sleep_health_score` 和六个 0/1 维度标记。

想看「如果做到某个目标分数怎么变」时加 `--targets targets.csv`（同样的列），写出 `out/levers.json`：每个目标单独达成和全部达成时的分数变化。分数变化不代表认知会跟着变。

## 报告里必须保留的话

- 分数只描述这一周的睡眠；论文没有发现这个总分与认知相关，所以不是认知或痴呆风险的预测，也不是诊断。
- 消费级手环的效率和中点算法与论文的 ActiGraph + GGIR 不同，接近切点时判定可能翻转。
- 不建议开始或停用任何药物或助眠产品；长期失眠、打鼾憋醒或白天嗜睡请找医生。

验证状态是草稿：论文印出了切点但没有印出个人算例。引用 `out/report.md`，包括 `边界:` 那一行。方法与来源见 [references/contract.md](references/contract.md) 和 [references/claims.md](references/claims.md)。
