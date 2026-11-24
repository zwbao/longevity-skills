---
name: vegetable-tmrel-gap
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Compares a person's recorded average daily vegetable intake with the published Burden
  of Proof theoretical minimum risk exposure range, reporting signed differences in grams per day and
  optional user-supplied intake scenarios. Use when a person asks how their vegetable intake compares
  with this study or wants to compare dietary records. Applies the paper's vegetable definition.
---

# 蔬菜摄入参考范围差距

适用于能提供饮食记录日均蔬菜克数的人。按 Stanaway 等，Nature Medicine，2022
公开的参考端点进行算术比较，不运行人群风险曲线。

用户命令：

> 帮我用饮食记录算蔬菜摄入与这篇研究参考范围的差距。

## 输入与口径

使用 `marker,value,unit` CSV，指标为 `vegetables_g_d` 或“蔬菜摄入量”，单位为 `g/d`。
每份输入只保留一个完整记录期间的日均值。计算日均值前纳入已记录的零摄入日，
缺失日不能填零；保留记录时间段和称重口径供用户核对。

计入新鲜、冷冻、烹调、罐装或干制蔬菜；排除豆类、盐渍或腌制蔬菜、蔬菜汁、
坚果种子，以及土豆、玉米等淀粉类蔬菜。不能用“蔬果合计”替代。
不按菜名猜重量，不将碗、杯换成克，不自行换算生熟或干鲜重量。
论文的无份量信息时每份假定重量用于研究数据标准化，本技能不将它作为个人通用换算。

输入防错范围为 0–3000 克/日，属于实现约束，不是健康标准。
规范键自身含单位；用普通别名时必须明确写单位。只接受 `g/d`，换算因子为 1。
没有已确认的对应 LOINC，不填写。

## 执行

```bash
python3 scripts/personal_report.py --intake intake.csv --out out
```

仅当用户提供了想比较的摄入量时加 `--targets targets.csv`，表头与输入表相同。
`--age` 和 `--sex` 仅兼容调用方的上下文参数，不读取进公式，也不分层解释。
无需用户提供论文 PDF、补充表、作者代码或 VizHub 数据；端点已冻在 `presets.py`。
运行不联网，除 Python 标准库外没有依赖。

输出 `report.md`、`result.json` 和 `levers.json`。缺项、错误单位、范围错误、
数值不可读或文件不可读时退出 3，写 `problems.json`，不保留先前计算结果。

## 报告要求

报告先显示论文卡片，再报告当前日均量、相对两个端点的有符号差值、
低于下端点的非负距离和 below/within/above 位置。
两端点属于范围内；高于上端点不等于有害，也不表示应该减少摄入。
目标情景只重算克数差距，不转为疾病风险变化、个人营养处方或健康获益。
论文没有独立个人差距算例，报告必须明确仍在验证。

每份报告原样保留：

> 边界: 这里只比较饮食记录与论文的人群参考范围，不预测个人疾病风险，不证明改变摄入会带来相应获益，也不能据此开始或停止药物。

材料核查、计算合同和验证缺口分别见 `references/claims.md`、
`references/contract.md` 和 `references/sources.md`。

