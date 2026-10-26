---
name: calf-circumference-decline-falls
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Groups the change between two of one person's own calf circumference measurements with
  the cut points of Zhang et al. (JAMA Network Open 2026, Chinese Longitudinal Healthy Longevity
  Survey 2018-2021, adults aged 60 and over) and reports the printed odds ratios of incident falls for
  that group versus no decrease (Tables 2-4, fully adjusted). Use for 小腿围, 小腿围变细, 腿变细, 跌倒风险, 肌少症筛查,
  老人跌倒. States that the odds ratios are population associations over about 3 years, not a personal
  fall probability, and does not diagnose sarcopenia.
---

# 小腿围变化分档与跌倒比值比（CLHLS 队列）

用户交自己前后两次量的小腿围（同一条腿、同样姿势），性别和年龄可选。不要向用户要论文或 PDF，切点和比值比已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements calf.csv --sex female --age 78 --out out
```

`calf.csv` 的列是 `item,value,unit`：

- 基线小腿围（第一次，必填）、随访小腿围（第二次，必填）：cm，也接受 mm、in。
- 名称也认 calf baseline、calf followup、第一次小腿围、第二次小腿围 等，`skill.json` 列出全部。

报告给出绝对变化（cm）、相对变化（%），按论文切点分档（绝对：没有减少、不到 3 cm、3 到不到 5 cm、5 cm 及以上；相对：没有减少、不到 10%、10% 到不到 20%、20% 及以上），以及该档在论文表 2、表 3（模型 4）里的跌倒比值比和置信区间。给了性别或年龄时，另外列出表 4 对应分层的比值比。

缺任何一次小腿围、单位不认识、数值超出 15–50 cm（论文的异常值界）或性别写错时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `calf_change_cm`、`calf_change_pct`、`absolute_category`、`absolute_or`、`relative_category` 和 `relative_or`。

## 报告里必须保留的话

- 比值比是论文人群（中国 60 岁及以上社区老人，两次测量间隔约 3 年）里该档相对小腿围没减少者的关联，不是个人跌倒概率，也不能说明因果；置信区间跨过 1 的档没有统计学差异。
- 小腿围分不清肌肉、脂肪和水肿；两次间隔明显不是约 3 年时比值比不一定适用。
- 明显变细或近期跌过倒时，建议请医生评估肌肉、平衡和用药；不写诊断。

验证状态是草稿：论文没有印出个人算例，测试只核对分档查表。引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
