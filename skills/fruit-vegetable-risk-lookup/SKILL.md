---
name: fruit-vegetable-risk-lookup
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. 按日均果蔬摄入克数查询 Aune
  等的非线性剂量反应表，分别返回水果与蔬菜合计、水果或蔬菜对应的心血管疾病、总癌症及全因死亡人群相对风险。用户询问自己的果蔬摄入量与这些结局的研究关联，或比较自设摄入目标时使用。
---

# 果蔬摄入量与相对风险查表

用户命令：「用我的日均果蔬摄入量查这篇研究里的相对风险。」

先确认选择哪一组食物、日均摄入克数、想查的结局。将用户的长期平均摄入量写成 CSV；单日记录不能直接视为长期平均。文件列为 `marker,value,unit`，一行例如 `intake_g_d,500,g/d`。这里的 500 只是演示输入，不是建议摄入量。食物定义与生熟重量在不同队列中存在差异，记录不明确时先核实；不从照片、杯、盘、份或未经说明的果汁体积猜克数。

```bash
python3 scripts/personal_report.py --measurements intake.csv --out out
```

默认查询「水果与蔬菜合计—全因死亡」。以下选项只改变查哪一列，不更改原表数值：

| 参数 | 可选值 |
|---|---|
| `--food-group` | `combined`（合计，默认）、`fruit`（水果）、`vegetables`（蔬菜） |
| `--outcome` | `all_cause_mortality`（默认）、`coronary_heart_disease`、`stroke`、`ischemic_stroke`、`hemorrhagic_stroke`、`cardiovascular_disease`、`total_cancer` |
| `--endpoint` | `mixed`（发病或死亡合并）、`incidence`、`mortality` |
| `--targets` | 用户自己设定的目标 CSV，与测量表相同列、相同食物组 |

全因死亡仅支持 `mortality`；缺血性与出血性卒中仅支持 `mixed`。其余结局支持三种分析。未指定 `--endpoint` 时，全因死亡用 `mortality`，其余用 `mixed`。水果和蔬菜的结果不能相乘，也不能把发病和死亡的列混用。

测量、单位或选择错误时退出码为 3，读取 `out/problems.json` 告诉用户要补哪项信息。仅接受 g/d（乘数 1），键名含单位时允许省略单位列的值。0–3000 g/d 仅为录入检查范围，不是有效模型范围；每列表格可查范围见 `references/contract.md`。

读 `out/report.md` 和 `out/result.json`。命中印出摄入点才有精确查表 RR；中间摄入点只有相邻两行，RR 为 null。超出表范围或原表空白也为 null，不能改成零风险。参照行未印 CI，保留 null。结果不是个人概率，也没有固定预测年限。

`out/levers.json` 总会输出当前查表结果与相邻印出行的有限差分；有目标时加目标结果。只有当前和目标都命中印出行才计算 RR 差，不合成差值的置信区间，不据此选「最佳」摄入量。有限差分不是原样条曲线导数。

禁止向用户索取论文 PDF、补充表、队列原始数据或代码仓库。已冻结补充表8–18的数值，正常运行完全离线，仅用 Python 标准库。食物亚类表19–27和人群归因死亡数不在本技能合同内。

报告必须以论文卡片开头，并原样保留：

> 边界：这是前瞻性人群研究的观察性关联查表，不是个人患病或死亡概率，也不能证明改变摄入量会带来相同变化；不能据此开始或停止用药。

不输出剂量、用药开始或停止指示。详见 `references/contract.md`、`references/claims.md`、`references/sources.md`。
