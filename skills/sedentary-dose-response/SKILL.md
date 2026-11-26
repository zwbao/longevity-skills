---
name: sedentary-dose-response
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Reads an adult's average daily sitting and television viewing time against
  published physical-activity-adjusted relative-risk tables and exposure thresholds. Use for questions
  about personal sitting hours, TV viewing hours, mortality associations, incident type 2 diabetes, or
  comparisons with a target duration. Returns printed values or adjacent printed rows without
  interpolating a risk curve.
---

# 久坐与看电视时长查表

输入来自个人问卷或日常记录：成人年龄，以及平均每天清醒时的总久坐或坐着看电视时长（至少一项）。总久坐包含看电视，不能把两者相加。每日平均时长用 `h` 或 `min` 表示，不输入单次连续坐着的时长、睡眠或每周累计时间。表格列为 `marker,value,unit`；支持中文名称“总久坐时间”“看电视时间”和英文别名。数据类型为 questionnaire / home_measurement。

用户命令：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 50 --out out
```

在技能目录执行。年龄只确认成人范围；可选 `--sex` 不改变查表值。用户提供目标时长时，加 `--targets targets.csv`，列与测量文件相同，可只改一项。必须有该项当前测量；当前、单项改变及全部目标场景均须满足看电视不超过总久坐。

技能已冻结出版商附表5、7–8需要的数字，不向用户索要论文、补充表、研究队列或代码。运行不联网，不安装第三方依赖。

报告与文件：

- `out/report.md`：中文，标题后先放论文卡片，再给当前/目标表值和边界。
- `out/result.json`：每种暴露和结局的原表RR、95%CI、参照时长、查表状态、相邻印刷行及附表5分段。
- `out/levers.json`：当前表值、相邻点割线敏感度、有目标时的各目标单独及一起改变结果。只能称为表值比较。
- 输入缺失、单位错误、数值错误或范围错误时退出3，只写问题报告和 `out/problems.json`；不补零。已提供另一种暴露时，缺少的一种保持未计算。

附表7–8给出的是非线性模型在已印出时长上的输出。仅命中印刷行才给当前RR；其余返回相邻行或超范围说明，不插值、不外推、不用附表5平均梯度重建曲线。四个阈值分别判断，等于阈值属于较低时长段；阈值不是“安全”界限。各结局保留自己的参照时长。总久坐和电视的RR不能相加或相乘；CI不是个人预测区间。原文摘要与正文的电视—癌症线性RR不一致，见 `references/claims.md`；本技能用附表8。

每份报告必须原样保留：

> 边界：这是成人前瞻性队列荟萃分析的人群关联查表，不是个人发病或死亡概率、预期寿命、安全时长界限或减少久坐的因果效果；不能据此开始、停止或调整药物。

不提供药物剂量或启停建议，不将目标变化称为干预效果。论文未提供个人基线危险率、绝对风险期限或完整样条系数，不能计算这些输出。

验证依据和操作定义见 `references/contract.md`；材料与研究设计见 `references/claims.md`、`references/sources.md`。
