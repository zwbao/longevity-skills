---
name: phq-9
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates PHQ-9 total and depressive symptom severity from one adult's nine item
  scores for the past two weeks. Use for PHQ-9 scoring, 抑郁筛查, 九项抑郁问卷, or recording repeated symptom
  assessments. Separately highlights any nonzero response to item nine for timely human support
  without diagnosing depression or grading suicide risk.
---

# PHQ-9 抑郁症状严重度

采用 Kroenke 等发表于 Journal of General Internal Medicine（2001）的计分方法。
先确认使用者为成人，且九题来自同一次、针对过去两周的完整回答；年龄未知时先确认成人身份。
将自己的回答整理成 `marker,value,unit` CSV 后，在本技能目录运行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

## 输入

每题只选一个频率：完全没有、有几天、超过一半天数、几乎每天。
对应的整数得分见 `skill.json` 的各输入说明；单位为 `score`。
不要把发生天数、PHQ-2 得分、总分或其他量表得分填进题目得分。
不知道或未回答时保持缺失，不能按“完全没有”处理。
下面是题意解释，不能当作经过验证的中文版问卷；已有规范问卷时直接录入其九项得分。

| marker | 题意（过去两周） |
| --- | --- |
| phq9_q1_score | 做事缺乏兴趣或乐趣 |
| phq9_q2_score | 情绪低落、抑郁或绝望 |
| phq9_q3_score | 难以入睡、睡眠中断或睡得过多 |
| phq9_q4_score | 疲倦或缺乏精力 |
| phq9_q5_score | 食欲差或进食过量 |
| phq9_q6_score | 对自己失望、觉得失败或让自己或家人失望 |
| phq9_q7_score | 难以集中注意力，例如阅读或看电视 |
| phq9_q8_score | 别人可察觉的动作或说话迟缓，或比平常明显坐立不安、活动增多 |
| phq9_q9_score | 觉得不如死去，或想到以某种方式伤害自己 |

附录的生活困难追问不计入总分，可在交流中单独记录；不要当作第十个计分项。
`--age`（岁）、`--sex` 为可选上下文，不影响分数；未成年人不按本文提供个人读出。
这是症状测量，不是可设定输入目标的风险方程，不提供 `--targets` 或优化回答的建议。

## 报告与支持

读取 `out/report.md`、`out/result.json`。报告先放论文卡片，再给出总分、分档及九项回答。
计分规则集中在 `scripts/presets.py`；复现的是 Table 2 的印出分档，不是某位患者的九题算例。
退出码 3 时读取 `out/problems.json`，解释缺项或输入错误，补齐后重跑；错误时不发布总分。

第九题非零时，先关心使用者现在是否安全，再解释总分；总分低也不能淡化该回答。
鼓励及时联系专业人员和可信任的人。如目前有自伤计划、已行动或无法保证安全，
应立即联系当地急救或到急诊，并请可信任的人陪伴。
交互助手应按用户所在地区核实危机支持渠道；不要仅凭第九题判断即时危险或诊断，
也不要为了等完整问卷而延迟支持。脚本在其他题缺失时仍保留已读取的第九题支持提示。

不向用户索要论文、附录、公开数据、代码或血液检查；运行完全离线。
不把研究的敏感度、特异度或群体功能状况写成个人确诊概率。
多次施测可分别记录，但本文未确证治疗反应阈值，不判断治疗成功、用药或因果收益。

每份报告必须保留：

> 边界: PHQ-9 反映过去两周的抑郁症状严重度，不能单独确诊或排除抑郁症，也不能判断自杀风险等级、推算个人寿命或衰老速度；本研究为成人门诊人群的横断面验证；不能据此开始、停止或调整药物。

材料核查见 `references/claims.md`，实现范围见 `references/contract.md`。
