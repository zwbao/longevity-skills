---
name: blood-lead-conditional-survival
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional.
  根据全血铅与用户指定参考浓度，计算对数剂量模型中的条件生存时间差，分别保留五次插补在第10、25、50百分位的结果。用于理解血铅报告或比较两个血铅浓度；不预测个人寿命，不把浓度下降解释为延寿获益。
---

# 血铅条件生存时间差

采用 Fang 与 Schwartz，medRxiv 2026 的 v2 主分析表2及附录S3。预印本，未经同行评审。限定40岁及以上、非妊娠成人的研究情境；妊娠者及未满40岁者不运行本读出。

用户命令：

> 用我的全血铅报告和我指定的参考浓度，计算条件生存时间差。

把用户的测量整理成 CSV（`marker,value,unit`），两项必填：`blood_lead_ug_dl` 与 `reference_lead_ug_dl`，单位 `ug/dL`；也接受 `ug/L`、`ng/mL`（均乘0.1）。中文或英文项目名必须写单位。参考浓度须由用户指定，可为另一份全血铅结果；不要自动选“正常值”、安全阈值或零。不得把尿铅、血清铅、头发铅当成全血铅，不对低于检测限的报告擅自代值。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 55 --out out
```

年龄只用于适用性检查。`--sex` 可选，不改变同协变量浓度差。用户明确提供假设浓度时，追加 `--targets targets.csv`；目标文件采用相同表头，只允许全血铅一项，保持参考浓度不变。所有目标是模型情景，不是行动建议。

输出 `out/report.md`、`out/result.json` 和 `out/levers.json`。每个分位点保留I1–I5，不平均、不选最有利结果。原表两项中位数NE必须保留为null，即使当前与参考相等。缺项、错单位、不合范围或无效目标：退出3，写 `out/problems.json`，全部结果置null，不生成情景结果；向用户说明缺什么测量，不补值。

技能已冻结必要系数，运行不联网。不得要求用户寻找论文PDF、附录、NHANES数据或作者研究档案。正文图2的样条绝对预测、尿镉标准化、汞/砷及营养素交互不是本技能的输出。

报告必须以论文卡片开头，并在结果之前注明：主要模型未调整尿镉；镉调整后，血铅与较短生存时间的关联不再成立。第10百分位不是用户有10%的死亡概率；该时间差不是个人剩余寿命。五次插补的范围也不是置信区间。

每份报告保留以下原句：

> 边界：预印本，未经同行评审；本结果仅为观察性模型在其他协变量保持相同时的条件生存时间差，不是你的预期寿命、死亡时间或死亡概率，也不是降低血铅可获得的寿命；不能据此开始或停止药物、补剂或排铅治疗。

参数、复现范围、材料核查见 `references/contract.md`、`references/claims.md` 与 `references/sources.md`。
