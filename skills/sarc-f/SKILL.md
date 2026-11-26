---
name: sarc-f
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the original SARC-F questionnaire's component scores, total and
  sarcopenia screening category from personal responses. Use for SARC-F, 肌少症筛查, lifting or walking
  difficulty, chair transfers, stairs and falls.
---

# SARC-F 肌少症风险筛查

按 Malmstrom 与 Morley（2013）正文和表1计分。用于整理个人问卷回答，输出中文筛查报告。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

`measurements.csv` 为 UTF-8 CSV，表头 `marker,value,unit`。五项均必填，不能把未知当作0：

| marker | 原题情境与填写方式 | unit |
| --- | --- | --- |
| strength_score | 提起并搬运10磅物品的困难：0无，1有些，2很困难或无法完成 | score |
| walking_score | 步行穿过房间：0无困难，1有些，2很困难、使用辅助器具或无法完成 | score |
| chair_score | 从椅子或床转移：0无困难，1有些，2很困难或不借助他人无法完成 | score |
| stairs_score | 上一段10级台阶：0无困难，1有些，2很困难或无法完成 | score |
| falls_past_year_count | 过去一年实际跌倒次数，非负整数；不要填跌倒项得分 | 1 |

10磅约为4.54千克；题干不能替换成5千克握力或客观起立测试。中文题意仅为说明性翻译，不声称是经过语言学验证的中文版。按日常情况回答，不要求实际试举或冒险上楼。

`--age`（18–120岁）和 `--sex`（男/女/其他/未知或male/female/other/unknown）为可选上下文，不影响分数。年龄范围是成人输入防护，不是论文的验证范围。五项都只接受整数；跌倒次数的1000上限是输入错误防护，不是临床切点。

技能随附计分规则，不向用户索要论文、补充表、队列或代码。运行时无需联网。四项困难得分与跌倒项得分相加，总分0–10；≥4为达到筛查界值，低于4不能排除肌少症。该问卷不是目标干预模型，不提供 `--targets` 或因果改善估计。

输出 `out/report.md` 和 `out/result.json`。缺项、错单位、超范围、非法编码时退出3，写 `out/problems.json` 与中文问题报告，不输出本次评分。报告先放论文卡片，再展示个人结果，并原样保留：

边界: SARC-F 是肌少症风险筛查问卷，不能单独确诊或排除肌少症，不能估计个人患病概率或预期寿命；本文仅描述初步研究，未报告完整验证样本与诊断准确度；不能据此开始、停止或调整药物。

来源与可行性审计见 [references/contract.md](references/contract.md)，证据限制见 [references/claims.md](references/claims.md)。
