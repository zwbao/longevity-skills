---
name: burden-of-proof-sbp-ihd
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Uses a person's systolic blood pressure to read the published Burden of Proof
  SBP–IHD relative-risk table, with uncertainty intervals and optional target comparisons. Triggers on
  收缩压与冠心病风险、血压相对风险、SBP–IHD or comparing a supplied blood pressure target. Labels interpolation
  explicitly and does not estimate personal event probability or treatment benefit.
---

# 收缩压与缺血性心脏病相对风险

使用 Razo 等发表于 Nature Medicine（2022）的补充表 4，将个人收缩压对应到人群平均相对风险。方法合同和来源核对见 [references/contract.md](references/contract.md) 与 [references/claims.md](references/claims.md)。

用户命令：

> 用我的收缩压报告查算缺血性心脏病相对风险；如果我提供目标血压，也比较目标值与当前的模型读数。

## 输入和执行

只需要用户自己的一个收缩压数值，CSV/TSV 表头为 `marker,value,unit`。例如 `收缩压,130,mmHg`；支持英文 `SBP`、`Systolic blood pressure` 及 `kPa`。多个不一致读数不会自动平均，先让用户明确要使用的汇总值。不要将 `130/80`、舒张压或脉压代入。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

仅当用户提供目标收缩压时加 `--targets targets.csv`，列格式相同。不自行设置目标。年龄、性别、用药不进入该表，故无需这些参数。

运行只用 Python 标准库及已随技能冻结的表格。不要向用户索取论文、补充表、GitHub 模型、IHME 数据、队列或系数文件；不要用在线可视化的新版本替换冻结表。

## 输出解释

- `report.md`：中文报告，标题后先放论文卡片；再写测量、参照、相对风险、不确定区间和读取方式。
- `result.json`：表格直接读数或插值近似；`readout_method` 为 `table_lookup` 或 `log_linear_interpolation`，并带相邻节点与证据稀疏标记。
- `levers.json`：当前 RR、插值函数局部敏感度；有目标时输出目标 RR、差和比。敏感度在节点取左右斜率平均，在端点单侧计算；它不是治疗效应。
- 缺项、错误单位、非数值、冲突读数、文件错误或超出 100–200 mmHg 表格范围：退出码 3，写 `problems.json` 与带论文卡片的中文说明，不保留旧的计算结果。数值真实但超出表格时应说明方法不适用，不让用户改成范围内的数。

每个表格节点严格使用印出数值。中间值按相邻节点分别对 RR、区间下界和上界作对数线性插值，必须称为近似；未恢复原文样条模型。107.5–165 mmHg 是论文证据较密集区间，不是临床正常范围。100 mmHg 是数学参照，不是治疗目标。五星评级描述整条证据关系，不能给个人贴上“五星风险”。

报告必须原样保留：

> 边界：这是把你的收缩压放到已发表人群曲线上的查算，不是个人发病概率、诊断或治疗建议；目标值对比不代表个人降压治疗的获益，不能据此开始、停用或调整药物。

不提供剂量。现用药、病史或其他体检数据不改变此查表结果。该表没有基线发病率、预测时间窗或个人校准项，不能换算个人十年风险或个人降压获益。
