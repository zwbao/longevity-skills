---
name: accelerometry-mortality-dose-response
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Reads the published accelerometry dose-response table for total activity, light,
  low-light, high-light or moderate-to-vigorous activity, or sedentary time, and reports cohort hazard
  ratios with confidence intervals. Use when a person aged at least 40 has daily averages processed
  with the paper's trunk-worn accelerometer protocol and asks how their activity or sedentary time
  corresponds to mortality associations, or supplies a target scenario. Between printed doses it shows
  the two neighbouring rows without interpolation.
---

# 加速度计活动与久坐的死亡关联查表

读取 Ekelund 等在 BMJ 2019（10.1136/bmj.l4570）补充表 5 印出的数值。
每次计算一种暴露；多种活动须分别运行。报告是队列关联查表，不能把 HR 相乘形成个人综合死亡风险。

## 一条用户命令

“我 62 岁，使用躯干部位佩戴的 Actigraph，确认符合下列处理协议；请用我的日均久坐表 `measurements.csv` 查死亡关联，并比较我自己提供的 `targets.csv` 目标。”

## 先核实数据口径

本方法不能直接读取普通手腕手环的“活动分钟”、步数、自报运动或坐着的时间、MET 分钟，也不能把三轴向量模长当作垂直轴计数。
用户只提供自己的处理后测量、年龄、设备及处理协议信息；不要向用户索要论文 PDF、补充表、NHANES 数据或代码。
公开补表已转录在 `data/dose_response.csv`，运行时不联网。

`--protocol vertical-60s-harmonised` 是对以下全部条件已经核实的声明，不能仅凭一个活动数字自动添加：

- 躯干部位佩戴（原研究为右髋或下背部）；垂直轴数据，60 秒 epoch。
- 非佩戴：连续 90 分钟零计数，允许最多 2 分钟非零中断，且中断上游或下游有连续 30 分钟零计数。
- 至少 4 个有效日，每个有效日佩戴至少 10 小时；使用有效日的每日平均。
- Actigraph：久坐 ≤100 cpm；LPA 101–1951；低 LPA 101–759；高 LPA 760–1951；MVPA ≥1952。
- 总活动是总计数除以佩戴分钟数。MVPA 为累计时间，不是只算连续 10 分钟活动段。
- Actical 仅能用于 MVPA 列，严格保留正文的 >1535 cpm 定义；其他列的剂量反应分析排除了 Actical。

若用户不能确认这些条件，运行时省略或如实填写 `--protocol`，取得 `problems.json` 后说明缺少什么。
不从原始信号重新生成这些测量，也不推断设备兼容性。

## 文件和执行

CSV 表头为 `marker,value,unit`，**每次仅一项**；例如 `久坐时间,10,h`。
时间单位 `min` / `h` 指每天的平均分钟或小时，可按精确因子 60 相互换算。
总活动单位使用 `/min`，含义是设备 counts/min，不能用步频代替。

| 输入键 | 补表覆盖范围 | 单位列 |
|---|---:|---|
| total_activity_cpm | 75–375 | /min |
| light_min_day | 150–450 | min |
| low_light_min_day | 100–325 | min |
| high_light_min_day | 10–120 | min |
| mvpa_min_day | 0–24 | min |
| sedentary_h_day | 6–12 | h |

范围之外不外推，也不意味着测量本身不正常。年龄须 ≥40；120 岁是程序的宽松合理性上限，不是论文报告的年龄上限。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 62 --device actigraph --protocol vertical-60s-harmonised --targets targets.csv --out out
```

无目标时省略 `--targets`；目标文件只有与当前同一种测量的一行。`--sex` 可选，仅接受 male/female/男/女，不改变结果。
脚本使用标准库。输入缺失、单位错误、超范围、未知项目或协议不符时退出 3，写 `out/problems.json` 和带论文卡片的中文说明，不留下旧计算结果。

## 读出规则

- 精确命中印出剂量时，报告该行 HR 及 95% CI。Reference 编码为 HR=1，不编造置信区间。
- 落在两行之间时，只展示较低与较高**暴露**行的原值，输入点 HR 留空；这两行不是输入点的置信区间或风险上下界。
- 参照使用补表 5 自身的 Reference 行。MVPA 的 0 分钟不同于补表 3 的 1.5 分钟；不混用。久坐 12 小时 CI 上限按补表 5 的 3.82，正文为 3.83。
- `result.json` 给出上述值，`levers.json` 给出同一指标的目标情景和相邻印出行。未公布的样条导数为 null；两端都精确命中时才计算 HR 的算术差，不计算差值置信区间。
- 不优化目标，不把最低 HR 对应时长写成运动处方，不推算绝对风险、寿命或因果获益。

每份报告开头保留论文卡片，并原样保留：

> 边界: 这是观察性人群的相对危险比查表，不是你的死亡概率、寿命预测或改变活动后的因果获益；不能据此开始、停用或调整药物。

参数来源、原文差异及实现范围见 [合同](references/contract.md) 和 [证据核对](references/claims.md)。
