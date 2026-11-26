---
name: daily-steps-health-lookup
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. 根据成人设备记录的日均步数，查询九类健康结局的人群危险比及置信区间。 适用于询问每日步数与死亡、心血管疾病、癌症、糖尿病、痴呆、抑郁症状或跌倒的关系。
  区分正文主要分析与更正后的事后分析，仅匹配已印出的步数点，并支持用户指定目标情景。
---

# 日均步数与健康结局查表

用户命令：

> 用我的设备日均步数查这篇研究的健康结局关联；如果我提供目标步数，也展示同一张表的目标情景。

将测量保存为 `item,value,unit` CSV，例如日均7000步为 `daily_steps_per_day,7000,1`。这里的单位 `1` 是固定一日窗口内的计数，报告显示步/日；不接受周总数、万步、步频或距离。用户应提供设备已统计的日均步数，不把单日偶然记录解释为通常活动水平。

运行 `python3 scripts/personal_report.py --measurements measurements.csv --out out`。
可选 `--age`、`--sex male|female` 仅作成人背景检查，不改变查表值。

- 默认 `--reference-steps 2000` 查询正文表2，接受2000至12000步/日、每1000步一个印出点。
- 只有明确查看相对7000步的事后分析时，使用 `--reference-steps 7000` 查询更正后补表8，接受7000至12000步/日、每1000步一个点。两表不能直接比较；严禁将正文HR相除来替代补表。
- `--targets targets.csv` 使用相同列和单位；在同一张表中展示用户指定目标，不把目标写为运动建议。
- 缺项、错误单位、超范围、未印出的步数点均退出3，写 `out/problems.json`。保留真实步数，不能为了跑通把7500改成7000；此时明确说明方法不支持精确查表。

输出中文 `out/report.md`、机器结果 `out/result.json` 和 `out/levers.json`。后者给出相邻印出点的HR差、目标结果和单项目标差异，没有连续敏感度或因果获益。参照点置信区间未印出，保留为空。

数值已冻结在 `data/printed_hr.csv`；不要要求用户寻找PDF、附录、原始队列或作者代码。运行不联网。材料核对见 [sources.md](references/sources.md)，产品合同见 [contract.md](references/contract.md)，研究边界与冲突见 [claims.md](references/claims.md)。

每份报告先放论文卡片。保留证据确定性、设备差异、跌倒仅来自老年人、残余混杂等限制。不得将HR改称个人患病概率、寿命增益或增加步数的治疗效果，不生成最佳步数或药物剂量。

必须原样保留：

> 边界: 这是前瞻性观察研究荟萃分析中的人群关联，不是个人发病或死亡概率，也不证明增加步数会带来相同获益；不能据此决定开始或停止用药。
