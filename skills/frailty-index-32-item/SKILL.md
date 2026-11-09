---
name: frailty-index-32-item
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes one person's 32-item frailty index (deficit accumulation, the CHARLS item set
  of Zhang et al., GeroScience 2026) from 30 yes/no questions on doctor-diagnosed conditions, vision,
  hearing, self-rated health, daily activities and mobility, the CES-D-10 total and an optional 0-1
  cognition deficit score, and classifies it with the paper's cut points as robust (FI <= 0.12),
  pre-frail (0.12-0.25) or frail (> 0.25). For pre-frail or frail adults aged 45+ without heart
  disease, stroke or cancer it lists the printed hazard ratios of incident heart disease and stroke
  versus robust. Use for 衰弱指数, 衰弱前期, 虚弱, frailty index, 缺陷累积, CHARLS 衰弱. Does not assign a trajectory
  group or give a personal disease probability.
---

# 32 项衰弱指数与衰弱分档（CHARLS 队列）

用户交自己的 32 项问卷答案，年龄可选。不要向用户要论文、补充表或 CHARLS 数据，计分规则和切点已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements fi.csv --age 62 --out out
```

`fi.csv` 的列是 `item,value,unit`，每项一行：

- 第 1–30 项（必填）：医生诊断过的高血压、糖尿病、心脏病、中风、癌症、关节炎、慢性肺病、哮喘、精神问题、记忆相关疾病；视力问题、听力问题、自评健康一般或差；穿衣、洗澡、吃饭、上下床、上厕所、管钱、吃药、买东西、做饭、做家务有没有困难；走 100 米、久坐后起身、连续爬几层楼、提 10 斤重物、捡硬币、弯腰下蹲、手臂上举有没有困难。写 1/0 或 是/否；自评健康也可以写 好、一般、差。
- 第 31 项（必填）：CES-D-10 抑郁量表总分（0–30），超过 10 计 1 分。
- 第 32 项（可选）：认知缺损分，已经换算到 0–1。论文没有印出从记忆和定向原始分换算的方法，所以不要替用户换算。不填时报告给出指数区间，区间不跨切点时照样分档。

名称也认 高血压、中风、CES-D-10、认知缺损分 等，`skill.json` 列出全部别名。

缺任何一项（认知分除外）、是/否项不是 0 或 1、CES-D-10 超出 0–30、单位不对时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `frailty_index`、`frailty_index_low`、`frailty_index_high`、`frailty_status`、`deficit_sum_31_items`。

## 报告里必须保留的话

- 衰弱指数是 32 项缺陷的累计比例，不是诊断，也不是个人心血管病概率；风险比是论文人群（中国 45 岁及以上、CKM 0–3 期、没有心血管病和癌症）的关联。
- 已有心脏病、中风或癌症，或不到 45 岁时，只给指数和分档，不套用风险比。
- 不归入轨迹组：论文的潜类别模型参数没有印出。
- 不给剂量，不让人开始或停用药物。

验证状态是草稿：论文没有印出个人算例，测试核对计分规则和切点。引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
