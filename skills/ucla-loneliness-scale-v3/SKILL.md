---
name: ucla-loneliness-scale-v3
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the UCLA Loneliness Scale Version 3 total and item scores from a
  person's complete original questionnaire responses. Use for UCLA第三版孤独感量表、 孤独感计分 or scoring an
  already completed 20-item UCLA V3 questionnaire. Shows reverse scoring and explains the result in
  Chinese without diagnostic cutoffs.
---

# UCLA 第三版孤独感量表

依据 Russell（1996），计算第三版完整问卷的逐题得分与总分。

## 用户命令

“按 UCLA 第三版帮我给这份完整问卷计分，显示反向计分后的得分，并用中文解释总分。”

## 输入与运行

需要本人在第三版完整问卷中的原始回答。先核对版本与题序，不能用初版、修订版、3题或10题短版替代。
原问卷见[期刊版表1，第23页（PDF第5页）](https://www.iscet.pt/uploads/obSolidao/artigo_base_ucla_loneliness_scale_v3.pdf#page=5)。
让用户填写的是自己的回答；不要向用户索要论文、补充表、代码或队列原始数据。
不复印完整问卷，也不将自行翻译的题干冒充经验证的中文量表。

把答案填入 `assets/answers-template.csv` 的副本，CSV 表头为 `marker,value,unit`：

- 每题编码为 1=从不（Never）、2=很少（Rarely）、3=有时（Sometimes）、4=总是（Always）；单位为 `score`。
- 填原始回答，脚本负责反向计分。不要填已经反转过的分值。
- 原文没有规定回顾时间窗，不擅自添加“过去两周”等条件。
- 20题必须齐全。不猜缺题，不用均值填补，不由一个总分倒推答案。
- 可选 `--age`、`--sex` 仅作上下文，不改变分数。

```bash
python3 scripts/personal_report.py --measurements answers.csv --out out
```

输出 `out/report.md` 和 `out/result.json`。输入有误时退出码为 3，输出
`out/problems.json` 和说明缺项的中文报告，不输出分数。
运行仅需 Python 标准库，不联网。

## 解读规则

原文表1列出的星号题反向计分，随后求和。分数越高表示自报孤独感越强。
报告先展示论文卡片，再展示个人总分、原始回答及每题得分。
20–80分为完整量表按题数与单题范围推得的理论区间，不是临床正常范围。
不输出轻中重分档、诊断、百分位、疾病风险、预期寿命或药物建议。
不使用表8因子载荷加权，不将教师短版均分当作完整量表常模。
本技能是问卷计分，不是可用输入目标模拟干预收益的风险模型，不提供目标推演。

每份报告保留以下边界句：

> 边界: 本结果仅描述自报的孤独感，不是精神疾病诊断，不提供轻中重分档、个人疾病风险或寿命预测；不能据此开始、停用或调整药物。

中文说明不是经过验证的中文问卷；这篇论文不能证明中文译本与英文原版等效。
如用户另有危机表达，需另行处理，不能用孤独感总分判断危机风险。

## 核对记录

- [产品合同与常数出处](references/contract.md)
- [研究与版本边界](references/claims.md)
- [全文和补充材料检索记录](references/sources.md)

验证复现的是表1原文印出的逐项反向计分映射，不是完整个人总分示例。
