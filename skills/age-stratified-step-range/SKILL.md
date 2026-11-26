---
name: age-stratified-step-range
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Compares an adult's device-recorded average daily steps with the age-specific plateau
  ranges reported in a human cohort meta-analysis. Use when a person asks how their daily steps relate
  to their age or wants to compare a chosen step-count target. Reports range position and arithmetic
  differences in Chinese.
---

# 按年龄比较日均步数

用户命令：`用我的年龄和日均步数，看看相对研究中的步数范围处在什么位置。`

输入：实足年龄（岁）及个人设备的日均步数。数据类型为可穿戴设备/计步器。
日均数按有效佩戴日的总步数除以有效日数；正文以一周设备观察为基础。
有效日标准随研究不同，不能把漏戴日记成零，也不能用一次散步或一周总步数代替日均步数。

准备 CSV，表头 `marker,value,unit`，例如：

```csv
marker,value,unit
daily_steps,6000,1
```

`daily_steps` 固定表示一天窗口的平均步数计数，机器单位 `1`，报告显示为步/日。
当前仓库单位表没有步/日，因此不宣称支持该单位字符串的自动换算。
只接受计数值，不把距离、步频、万步、周总量换成日均步数。支持中英文别名见 skill.json。
没有可靠有效日平均数时先请用户提供，不能猜。

```bash
python3 scripts/personal_report.py --measurements my_steps.csv --age 60 --out out
```

可选 `--targets my_target.csv` 使用同样的表头，只接收用户指定的日均步数目标；年龄保持不变。
`--sex` 可接收上下文，不影响本方法。没有其他模型参数需要用户选择。
输出 `out/report.md`、`out/result.json`、`out/levers.json`；错误或缺项退出 3，写 `out/problems.json` 和空结果。
脚本无需联网。不得要求用户寻找论文、附录、队列数据、研究代码或风险系数。

范围的选择与端点均来自 `scripts/presets.py`。分档只是把当前值与约略范围比较，不是论文验证的诊断分类。
验证仍为草稿：测试核查印出的常量和软件行为，但论文没有个人分档算例。
假设目标只显示步数差和范围位置，不显示风险获益、寿命变化或自动生成的运动目标。

每份报告先放论文卡片；必须保留以下边界句：

边界: 这是观察性人群研究中日均步数与死亡的关联范围，不是个人死亡风险、因果效应或运动处方；高于范围不表示有害或应减少步数，也不能据此开始或停止任何药物。
