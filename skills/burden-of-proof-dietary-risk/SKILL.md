---
name: burden-of-proof-dietary-risk
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Reads published Burden of Proof relative risks for processed meat,
  sugar-sweetened beverages and trans-fat energy intake at the exact exposure points in Supplementary
  Tables 13–16. Use for an adult asking what their habitual intake corresponds to in these population
  associations, or comparing user-specified intake scenarios. Reports uncertainty including
  between-study heterogeneity; does not interpolate or calculate individual absolute risk.
---

# 饮食摄入量与慢病相对风险

用 Haile 等，Nature Medicine 2025 的附表 13–16，读取与用户真实摄入量相对应的风险比。已冻结 39 行数值，运行不联网，不要求用户找论文、附录或作者数据。

```bash
python3 scripts/personal_report.py --measurements intake.csv --age 50 --out out
```

`--age` 必填，只核对成人适用范围，不影响风险读数。`--sex` 可选，论文没有性别特异的风险表。`--targets targets.csv` 可选，使用相同表头，且每个目标都必须有当前值。年龄和摄入量请使用用户实际数据；命令中的年龄只是用法示例。

输入 CSV 表头为 `marker,value,unit`，三类摄入量至少交一项；缺项不能填零。食品信息来自长期习惯或具有代表性的饮食记录，不把偶尔一天当作长期习惯。

| marker | unit | 可直接读取的摄入量点 |
|---|---|---|
| processed_meat_g_d（加工肉） | g/d | 0、25、50、75、100、150、200、250、300、350、400 |
| ssb_g_d（含糖饮料） | g/d | 0、250、500、750、1000 |
| tfa_energy_pct（反式脂肪供能占比） | % | 0、1、2、3、4、5、6 |

这些数是论文表格中的报告位置，不是推荐摄入量。摄入量不在表中时，返回退出码 3 和 `out/problems.json`，说明本工具缺少相应表格点；保留用户的真实值，不能为了运行而四舍五入、改写记录或调整饮食。

加工肉指烟熏、腌制、盐渍或添加防腐剂的加工肉类。含糖饮料输入饮料总质量，不是其中糖的质量；不自动换算毫升、杯、瓶或份。反式脂肪输入其占每日总能量的百分比，不是配料表中的重量百分比；能量比例可用单位 `1`，例如比例 0.01 精确换算为 1%。不能仅凭配料表或用假设的总能量推算此输入。

加工肉 25、75 g/d 只返回缺血性心脏病读数；150 g/d 只返回糖尿病和结直肠癌读数。零摄入的 RR=1 来自参照定义，不另造不确定区间。绝不填补缺失点、内插、外推，或把 RR 相乘、相加。

输出 `out/report.md`、`out/result.json` 和 `out/levers.json`。中文报告以论文卡片开头，保留包括研究间异质性的 95% 不确定区间，并说明一星、二星描述证据而不是个人风险等级。超出论文概括证据所用摄入量密集区间时提示证据限制。

`levers.json` 保留各输入的当前值、相邻表格点的有限差值、目标分别达成和全部达成时的各项读数与 RR 差。连续导数未提供，`derivative` 为 null；有限差值明确标作割线，不冒充原始曲线灵敏度。目标只由用户提供，不生成推荐目标；不提供差值的不确定区间，因原表没有两点之间的协方差。

每份报告必须原样保留：

> 边界：这是成年人观察性研究的群体关联查表，不是个人绝对发病概率、诊断或改变饮食后的因果预测；不能相乘或相加为总风险，不能据此开始或停用药物。

材料核查见 [references/claims.md](references/claims.md)，计算范围与复现合同见 [references/contract.md](references/contract.md)。
