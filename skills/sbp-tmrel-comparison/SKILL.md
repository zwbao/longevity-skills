---
name: sbp-tmrel-comparison
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Compares a person's brachial systolic blood pressure with the published GBD 2021
  theoretical minimum risk exposure interval, reporting endpoint differences and interval position.
  Use for questions about how a measured SBP compares with the GBD research reference; it does not
  estimate disease risk or treatment targets.
---

# 收缩压与理论最低风险区间比较

适用于用户已有上臂收缩压测量，想知道它与 GBD 2021 群体研究参照区间的数值关系。依据 GBD 2021 Risk Factors Collaborators，Lancet，2024，附录 1 表 S9 和收缩压方法章节。

用户只提供自己的测量文件，列为 `item,value,unit`，一行收缩压；接受 mmHg 或 kPa。不要把收缩压和舒张压写成一个值，不要把多次测量作为同一项目重复输入。缺少可靠汇总值时，请用户提供要比较的那次读数或已有汇总值，不替其估计长期血压。单位别名和换算以 skill.json 为准。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

输出 `out/report.md` 与 `out/result.json`。输入缺失、单位错误、重复项目或值不合理时退出码为 3，同时生成 `out/problems.json`；将其中中文原因告诉用户，不用猜测值补齐。

参数表已经核对并冻结在脚本中，运行不联网。禁止向用户索要论文、附录、GHDx 结果表或代码。年龄和性别不参与这个固定区间的算术比较。该技能没有个人风险模型，也不提供目标模拟或用药方案。

报告必须以论文卡片开头，说明 `below / within / above` 只是相对区间的位置；两端点均算区间内。这不是临床正常范围。验证仍为暂定：常数核对不等于复现论文中的个人计算示例。

每份报告保留原句：

> 边界: 这是个人收缩压与 GBD 2021 群体研究参照区间的算术比较，不是高血压诊断、个人患病概率或寿命预测；TMREL 不是降压治疗目标，低于区间不代表更健康，区间内也不代表没有风险，不能据此开始、停止或调整药物。

证据和访问记录见 [references/claims.md](references/claims.md)，计算定义见 [references/contract.md](references/contract.md)。
