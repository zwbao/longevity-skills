---
name: daily-step-health-lookup
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. 根据成人设备记录的日均步数，定位 Ding 等发表的步数与九项健康结局的人群危险比及置信区间。 用户问每日步数、手环活动量与死亡、慢病、痴呆或跌倒的关联时使用。
  命中原表步数时直接查表，位于两行之间时分别展示原值，不插值、不外推，也不预测个人风险。
---

# 日均步数与健康结局查表

用户提供一份单人的设备日均步数 CSV 和实足年龄；公开查表数据已随技能附带，无需联网运行。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 50 --out out
```

CSV 表头为 `marker,value,unit`，例如一行 `日均步数,7000,1`。
`1` 是仓库标准中的计数单位，日时间窗由 `steps_per_day` 限定，报告显示为“步/日”。
接受中文日均步数、每日步数、英文 daily steps、Steps/day 等别名；不把公里、分钟或周总步数换算成日均步数。
应使用设备记录的典型多日平均；不要把单次运动步数或一天的最高值当作通常水平。
论文没有规定统一的个人采集天数，不另设未发表的采集门槛。

- `--age` 必需，仅确认成人适用范围；18 岁以下不读出。
- `--sex` 可选，仅兼容个人背景输入，不改变合并表值。
- `--targets targets.csv` 可选，列与测量文件相同，只接受用户提出的日均步数目标，不自动设定目标。
- 输入必须在原表 2000–12000 步范围内。非整千步展示上下相邻表行；这两行不是个人 HR 的置信区间，也不是估计上下界。
- 输入缺失、格式或单位错误、超出表格范围时退出 3，写 `out/problems.json`，不保留上次成功的数值结果。

`out/report.md` 是中文报告，以论文卡片开头；`out/result.json` 提供输入定位与两侧表行的 HR 和 CI。
恰好命中表行时，`lower` 与 `upper` 相同。2000 步是参照，HR 为 1，CI 未报告，因此为 null。
`out/levers.json` 总是标明没有连续导数；有目标时附目标查表结果。
只有当前与目标都命中表行才提供同一参照下的 HR 数值差，不计算目标相对当前的风险比、获益百分比或差值置信区间。

所有结局以 2000 步/日为共同参照。不能将正文表 2 与附录表 8（另以 7000 步为参照的事后分析）混用。
保留原表非单调曲线，不能把步数增加解读为所有结局都会持续改善。
跌倒证据来自老年人群、确定性极低；不能用于判断个人行走安全。
身体功能没有合并查表值。没有年龄、性别、健康状态或设备佩戴部位的个体校准。

禁止向用户索要论文 PDF、补充表、研究队列或作者代码。来源与表内差异见
[references/contract.md](references/contract.md) 和 [references/claims.md](references/claims.md)。

报告必须原样保留：

> 边界：这是按你的日均步数定位的人群观察性关联，不是个人发病概率、寿命预测或增加步数的因果效果；不能据此开始、停用或调整药物。
