---
name: physical-activity-frailty-index
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes the weighted weekly physical activity of Ji (GeroScience 2026, CHARLS
  2011-2020, Chinese adults aged 60 and over) as 2 x vigorous + moderate + 0.5 x light minutes, places
  it and each intensity in the 0 / 1-149 / 150-299 / >=300 min/week groups, and looks up the printed
  frailty phenotype and frailty index betas and 10-year mortality hazard ratios for those groups. Also
  scores the paper's 48-item frailty index from questionnaire answers and four lab values, and the two
  frailty phenotype items that need no cohort cut-off. Use for 衰弱, 衰弱指数, frailty index, 运动量够不够,
  每周运动多少分钟, 老人运动, 体力活动与寿命. States that the numbers are cross-sectional population associations, not a
  diagnosis or a personal death probability.
---

# 体力活动剂量与衰弱指数（CHARLS 中国老人队列）

用户交自己每周高、中、低强度活动的分钟数；想算衰弱指数时，再交 43 道问卷题的答案代码、体重身高和四项化验。不要向用户要论文、补充表或 CHARLS 数据，公式、计分和查表数都在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements pa.csv --sex female --age 68 --out out
```

`pa.csv` 的列是 `item,value,unit`：

- 必填：每周高强度、中等强度、低强度活动分钟数（HPA、MPA、LPA；`min`，也接受 `h`）。每次连续至少 10 分钟才算；没有就填 0。
- 可选，衰弱指数用：43 道问卷题（日常活动、工具性活动、身体功能、14 种医生诊断的慢病、8 道过去一周情绪题、自评健康、生活满意度），值填答案代码，每题的代码含义写在 `skill.json` 的 `note_zh`；体重、身高；糖化血红蛋白（%）、血红蛋白（g/dL 或 g/L）、C 反应蛋白（mg/L，必须写单位）、血肌酐（mg/dL 或 µmol/L，必须写单位）。血红蛋白一项需要 `--sex`。

报告给出加权总活动量、各强度分档、该档在论文图 6、图 7 的 β 和补充表 1、2 的 10 年全因死亡风险比；48 项齐全时给出衰弱指数和分档（≤0.10 健康、0.10–0.21 衰弱前期、>0.21 衰弱），缺项时只给可能的最小和最大值并列出缺哪几项；衰弱表型只算 BMI 和耐力两项，握力、步速、体力活动三项的队列切点论文没印出，不算。

活动分钟数缺项、单位不认识、数值超出范围、答案代码不是整数或不在选项里、性别写错时不计算：报告写明原因，脚本退出码 3。

## 报告里必须保留的话

- β 和风险比是论文人群里该档相对每周 0 分钟者的关联，衰弱分数部分是横断面比较，作者明确写不能证明因果，也不是个人死亡概率。
- 衰弱指数和衰弱表型不是诊断；只算得出衰弱表型的两项。
- 不建议开始或停止任何药物；运动安排结合自身情况和医生意见。

验证状态是草稿：论文没有印出个人算例，测试只核对公式、计分、切点和查表。引用 `out/report.md`，包括 `边界:` 那一行。来源和操作定义见 [references/contract.md](references/contract.md)。
