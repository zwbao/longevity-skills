---
name: china-tobacco-mortality-lookup
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Queries published Chinese male cohort mortality rate ratios by urban or rural
  residence and last daily tobacco amount. Use for an eligible person's smoking-history lookup or
  comparison of specified amount categories; returns population associations and group-specific
  intervals, not an individual death probability or cessation benefit.
---

# 中国男性吸烟量与死亡率查表

按 Chen 等（Lancet，2015）表 2 的 CKB 2006–14 年男性结果离线查表。用户提供自己的吸烟史，固定表值由技能携带，不要向用户索要论文、附录、队列数据或代码。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 55 --sex male --area urban --smoking current --regular-six-months yes --out out
```

`measurements.csv` 使用 `marker,value,unit` 三列。必填 `tobacco_amount_g_d`（g/d 当量）：按论文把**最后规律吸烟时的每日卷烟支数与每日其他烟草克数相加**。例如纯卷烟每日20支写 `tobacco_amount_g_d,20,g/d`；这不是卷烟实际重量或尼古丁量。不把包年、每包支数不明的包数、电子烟或烟草替代品直接换算。未知不能填零。可识别“每日烟草当量”等中英文别名；别名行必须有单位。

适用条件逐项确认：

- 中国男性，当前整数周岁40–79；年龄仅作使用范围检查。
- 曾每日≥1支卷烟或≥1g烟草持续至少6个月，才传 `--regular-six-months yes`。
- `--smoking current` 为当前规律吸烟；`stopped_ill` 为因病停烟，量填写停烟前最后规律吸烟量。主动戒烟、从未规律吸烟或状态不明者不能套用。
- `--area urban/rural` 根据长期居住环境选择，不能为了较低RR选农村。迁移史复杂、不能归类时先澄清。
- 本工具接受1–200 g/d当量；上限是防误输规则，不是论文切点。分档边界为15和25；15–24按连续数值解释为15≤量<25，不四舍五入。

输出 `out/report.md`、`out/result.json` 和 `out/levers.json`。报告从论文卡片开始，列全因、肺癌、缺血性卒中或缺血性心脏病合并、论文COPD分组的死亡RR。后者按附录包含ICD-10 J40–J44及I26–I27，不能简化为严格的COPD专病定义。

`--targets targets.csv` 可接收同格式的一行烟草当量，固定城乡和其余背景，比较两档人群关联并在 `levers.json` 给出每个结局RR差及邻档敏感度。它不是改变吸烟量的因果模型，不提供目标建议；不接受零值来模拟戒烟。因病停烟者的量是历史量，情景不表示重新吸烟。分档没有连续导数，不估计差值置信区间。

缺项、错误或超范围输入退出3，写 `out/problems.json`；报告保留论文卡片和边界，所有结果为空。读 problems 后向用户明确需要补充的真实信息，不填补、不猜。

报告必须保留：

> 边界: 本结果是历史中国男性队列的分组关联，不是个人死亡概率、预期寿命或改变吸烟量后的因果效应；不能据此开始、停止或调整任何药物。

区间必须标作“组别特异性95%区间”，不能改称个人预测区间或通常的两组比较置信区间。农村非单调结果不表示多吸更安全。女性、主动戒烟者、起始吸烟年龄分层与旧队列结果不在本技能合同内；不合并成未经发表的多因素预测模型。
