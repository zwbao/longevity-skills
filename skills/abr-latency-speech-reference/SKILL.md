---
name: abr-latency-speech-reference
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Queries the published age-by-click-ABR Wave I latency reference table for word and
  phoneme recognition in noise, including fitted-mean confidence intervals. Use when someone supplies
  an ABR Wave I latency and age that exactly match the printed grid, or asks to read that table. This
  preprint-based method supports only ages 45, 55, 65, 75 and latencies 1, 1.2667, 1.4, 1.48, 1.83 ms;
  it does not interpolate or reconstruct the full regression.
---

# 年龄与听觉潜伏期的言语识别原表参考

读取 Cederroth，medRxiv 2026 第三版补充表 S12（第 19 页）。这是固定其他协变量后的原表参考查询。对任意年龄或任意潜伏期的完整回归尚不能实现：S9/S10 虽印出系数，未印出完整中心化均值，不能用全队列四舍五入的描述均值代替。

## 用户命令

“我 75 岁，测量表里是右耳点击 ABR 波 I 潜伏期，请查论文原表的言语识别参考值，并说明限制。”

## 输入与运行

用户只提供自己的年龄和同一只耳的测量表（CSV 或 TSV，列为 `marker,value,unit`）。波 I 潜伏期标准键为 `w1_latency_ms`，单位为 ms；接受 s，按精确因子 1000 换算。姓名、病历全文、基因数据均不需要。

```csv
marker,value,unit
ABR波I潜伏期,1.83,ms
```

```bash
python3 scripts/personal_report.py --measurements /path/to/measurements.csv --age 75 --out /path/to/out
```

`--age` 是实足年龄，只接受 45、55、65、75 岁。潜伏期只接受 1、1.2667、1.4、1.48、1.83 ms。表中的 Q1 印为 1.2667，按印刷精度查询，不将 1.2666667 等其他数值改成它。不能取整年龄、将潜伏期归到最近一格、插值或外推；真实值不匹配时说明该表不能给出结果，不能让用户修改测量。

可选 `--sex male|female|男|女` 只作背景，不改变原表的男性参考设定。若用户需要女性个体预测，此技能无法提供。两耳分别运行，不能把两耳平均后当作一耳，也不能把波间潜伏期或振幅填成波 I 绝对潜伏期。

核对测量条件：论文采用 90 dBnHL、100 微秒交替极性点击、9.1 次/秒，在 Chartr 或 Eclipse 系统记录；言语测试为瑞典语、+4 dB 信噪比。不同测试条件不能作为个人预测直接套用。

## 数据和报告

S12 数值已随技能冻结在 `data/table_s12.csv`，来源和提取限制见 `references/contract.md`。不要向用户索要补充材料、原始队列、作者代码或中心化均值；运行不联网。

成功写 `report.md`、`result.json`。缺项、单位错误、非数值、超范围或不在原表坐标时退出 3，写 `problems.json`，结果全部为空；不在坐标范围是方法覆盖限制，不是测量异常。错误报告也保留论文卡片和边界。重复运行不会留下上一次的有效结果。

报告使用中文，开头为论文卡片，再展示原表词语/音素均值、标准误和均值的 95% 置信区间。它固定其他连续变量在中心化零值、性别为男性参考设定，未使用个人的 PTA、OAE 或其他 ABR 波测量。置信上限超过 100% 时保留原值并解释，不解释为真实得分超过满分。不能提供听力年龄、耳蜗突触病诊断、个体预测区间或治疗效果。

年龄和电生理潜伏期不是本表可操作的干预目标，不提供 `--targets` 或 `levers.json`。

每份报告必须保留：

> 边界: 预印本，未经同行评审；结果仅为原表中其他连续协变量取中心化零值、性别取男性参考设定时的模型均值，不是你的实测言语得分、个人预测区间、诊断或干预效果，不能据此开始或停止用药。

验证始终为 draft；测试核对的是原表查询，不宣称独立复现完整回归。印刷示例及误差范围见 `skill.json`。
