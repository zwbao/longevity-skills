---
name: audit-c
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes the original AUDIT-C alcohol screening score from three past-year
  response options and compares it with both published screening cutoffs. Use for AUDIT-C, 饮酒筛查, 喝酒频率,
  or 酒精使用问卷. Preserves the original male validation population and six-drink third question.
---

# AUDIT-C 饮酒筛查

把用户过去一年三题回答写成 `marker,value,unit` CSV，再运行：

```bash
python3 scripts/personal_report.py --measurements answers.csv --sex male --age 67 --out out
```

`--sex`、`--age` 是可选背景，只填本人资料；示例值不能默认套给用户。
以 `out/report.md` 和 `out/result.json` 为准。退出码 3 时读取
`out/problems.json`，向用户补问对应回答，不补零。

## 回答编码

三题都询问过去一年。单位列为 `1`，表示无量纲选项编码，**不是得分或原始杯数**。
第一、二题有六个选项；编码由本技能定义，原论文给的是回答与分数的对应关系。

| marker | value 的含义 |
| --- | --- |
| q1_response_code | 0从不；1每月或更少；2每月2–4次；3每周2–3次；4每周4–5次；5每周至少6次 |
| q2_response_code | 典型饮酒日：0为0杯；1为1–2杯；2为3–4杯；3为5–6杯；4为7–9杯；5为至少10杯 |
| q3_response_code | 单次至少六杯：0从不；1不到每月一次；2每月；3每周；4每天或几乎每天 |

原文的“杯”指一罐或一瓶啤酒、一杯葡萄酒、一份 wine cooler、一份鸡尾酒或一小杯烈酒。
没有统一乙醇克数；遇到容器大小、酒精浓度不清，先澄清份数，不能套用后来版本的标准杯换算。
不要将第三题改为单次四杯或五杯。所有题目必须明确回答，不能因第一题不饮酒而静默补齐。

## 报告解释

每题按原文计分后求和，同时展示两个切点比较。原研究的两切点用于同一男性样本，
不得解释成女性与男性各一个切点。女性或性别未知时保留数值，明确其验证适用性未确认。
阳性提示需要进一步评估；阴性不能解释为安全饮酒或排除酒精相关问题。
不把筛查性能、假设患病率的演示值或群体数据当作个人概率。

数据类型为问卷，运行不联网；不向用户索要论文、DPQ全表、补充文件、代码或队列数据。
该方法是历史饮酒筛查量表，不是可推演干预获益的风险模型，不接受目标情景。
计分来源、访问限制和复现范围见 [合同](references/contract.md) 与 [核对记录](references/claims.md)。

每份报告保留以下边界句：

边界: 这是饮酒问题筛查，不是酒精使用障碍诊断，也不预测寿命或长期风险；原研究验证样本为男性退伍军人，不能把其筛查性能直接推广到女性或其他人群。不能据此开始、停止或调整药物。
