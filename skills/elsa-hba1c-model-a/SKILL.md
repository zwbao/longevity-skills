---
name: elsa-hba1c-model-a
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes the printed final ELSA HbA1c Model A probability of diabetes detected by the
  next health visit from HbA1c, age, sex and a specified visit interval. Use for research
  interpretation of a diabetes-free older adult's HbA1c or a user-specified HbA1c scenario. Preserves
  preprint and validation limitations.
---

# ELSA HbA1c Model A

按 Tapias 等（medRxiv，2026）的补充表 S4 计算最终 Model A。
它是随访间隔条件下的研究模型，不是糖尿病诊断工具或治疗目标计算器。
使用标准库，无需联网、安装依赖、训练模型或获取队列数据。

## 一条用户命令

“用我的 HbA1c、年龄、性别和指定访视间隔，按 ELSA Model A 算研究模型概率，并比较我指定的 HbA1c 目标情景。”

## 运行

先核实所有输入，不能根据姓名推断性别，也不能自行设定随访间隔或 HbA1c 目标。
以技能目录为当前目录执行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 67 --sex female --years-next 4 --eligible-baseline 1 --out out
```

测量文件为 CSV/TSV，列为 `marker,value,unit`，例如 `HbA1c,5.58,%`。
这是运行格式演示，不是论文中的个人预测示例。

- `--age`：当前基线年龄，接口限制为 50–110 岁；上限是输入保护，不是样本最大年龄。
- `--sex`：`female`/`女`/`1`，或 `male`/`男`/`0`，对应论文的女性指示变量。
- `--years-next`：以年为单位，必须提供。原研究通常约四年或七年。计划年数仅是条件情景，不能当复查建议。
- `--eligible-baseline 1`：用户已明确确认此前及当前无论文定义的糖尿病，并有至少三个月前、尚无糖尿病时的 HbA1c 测量。此前/当前诊断、糖尿病用药、HbA1c 达阈值或空腹血糖达到论文阈值者不符合；不知道时不能代填 1。定义见 contract.md。
- HbA1c 仅接受 NGSP/DCCT `%`；按单项名称输入时必须写单位。键 `hba1c_pct` 自带单位含义。IFCC `mmol/mol` 不可按百分数填入，本接口会拒绝；不能以单一倍数转换。若只有 IFCC 报告，说明当前接口的限制，不猜测或改写原值。
- 有用户自定的 HbA1c 目标时加 `--targets targets.csv`，表头相同。只允许 HbA1c 目标；年龄、性别、随访间隔固定。不能替用户选择治疗目标。

不能向用户索要 ELSA 数据、补充表、代码仓库、模型权重或逐折系数。
所需 Model A 参数已冻结在 `scripts/presets.py`；出处见 `references/model-s4.csv`。

## 输出和失败处理

成功生成中文 `out/report.md`、`out/result.json` 及 `out/levers.json`。
后者包含各模型输入的局部敏感度（二元性别用模型差值），有目标时包含单项及整体情景结果。
`eligible_baseline` 只是适用性确认，不是可变目标或方程输入。
HbA1c 敏感度的单位是“概率百分点 / HbA1c 百分点”，不是相对风险百分比。

缺项、错单位、超范围、不适用或无效目标，退出码为 3，生成 `out/problems.json`，结果数值为 null。
读取错误原因后告诉用户需要提供或核实什么，不用平均值、零或假定性别补齐。
失败报告也从论文卡片开始；重复运行会清除旧结果。

报告必须保留模型的访视间隔、族群外推、最终模型未单独评估和舍入参数限制。
不能把交叉验证 AUC 说成本人的准确率，不能把目标情景差值说成降糖治疗收益。
不输出个人斜率、Model B–E、Transformer 预测、诊断分档或药物剂量。

每份报告原样保留：

> 边界: 预印本，未经同行评审；这是 ELSA 队列研究模型在指定访视间隔下的估计，不是诊断、个人真实发病概率或干预效果；不据此开始、停用或调整药物。

## 验证状态

`validation.status` 为 `draft`。S1 中两组 HbA1c 均值的单位换算已在论文舍入精度内复现，
并保留在 examples 块；这不构成 Model A 个人预测示例复现。
正文、补充材料和公开代码没有提供完整个人输入对应的印出概率。
工程测试核对 S4 参数、方程、输入保护和情景输出；不宣称重跑了队列训练或外部验证。

方法范围、材料查阅记录和常数表见 [contract.md](references/contract.md) 与 [claims.md](references/claims.md)。
