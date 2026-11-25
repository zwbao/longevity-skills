---
name: finnish-diabetes-risk-score
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes the original seven-item Finnish Diabetes Risk Score from age,
  sex-specific waist circumference, BMI, and questionnaire answers. Use for a non-laboratory diabetes
  risk screening score or user-supplied BMI, waist, activity, and diet target scenarios in adults
  within the paper's population. Reports Chinese component scores and the screening cutoff; does not
  estimate an individual's diabetes probability.
---

# 原版七项芬兰糖尿病风险评分

用户命令：「用我的年龄、腰围、BMI和问卷，算原版七项糖尿病风险评分；如果我给了目标，也比较目标情景。」

使用 Lindström 与 Tuomilehto，Diabetes Care，2003 的原版。适用于35–64岁、评估时未接受降糖药治疗的人。论文结局是随访时进入药物治疗登记，并非所有糖尿病发病。已知仅饮食治疗的糖尿病在原研究中未排除；不能把本技能用于判断已确诊者是否患病。

## 收集个人输入

把个人数据整理成CSV，表头为 `marker,value,unit`；从用户资料提供 `--age` 周岁和 `--sex male|female`（也接受男/女）。性别只决定腰围阈值。问卷答案填0或1，不知道就是缺项，不能按否处理。

| marker | 内容 | 单位或编码 |
|---|---|---|
| bmi_kg_m2 | BMI，体重kg除以身高m的平方 | kg/m^2 |
| waist_cm | 最低肋骨与髂嵴之间中点的腰围 | cm；也接受m、mm、in |
| bp_medication_ever | 是否曾用过降压药 | 0=从未，1=曾经 |
| high_glucose_history | 是否曾被医务人员告知糖尿病或潜在糖尿病 | 0=无，1=有；包含临界或暂时血糖升高、妊娠糖尿病、仅饮食治疗的糖尿病 |
| low_activity | 是否属于原文低活动类别 | 1=闲暇以阅读、看电视和不费力家务为主、活动不足4小时/周且工作主要坐着而不需多走动；0=不属于 |
| daily_produce | 是否每天吃蔬菜、水果或浆果中的至少一类 | 0=不是每天，1=每天 |
| antidiabetic_treatment | 评估时是否接受降糖药治疗 | 0=否，1=是；只检查适用性，不计分 |

活动恰好4小时/周按表1脚注「至少4小时」类别处理。不能换成后续版本的每日30分钟问题。高血糖史不是一项血糖化验值；不要凭某次化验自行替用户回答病史。

## 执行

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 45 --sex male --out out
```

若用户给了目标，追加 `--targets targets.csv`，列格式相同，可以只给一项。只接受BMI、腰围、活动和蔬果答案。年龄、性别、既往病史和用药适用条件不是可改变目标。不得主动推荐目标或通过停药改变历史答案。

输出 `report.md`、`result.json` 和 `levers.json`。后者包含当前分值、逐项跨类别的分差，以及目标单独和共同代入后的总分；离散评分不提供误导性的连续导数。无目标时仍输出各输入的类别敏感度。

缺项、未知项目、读不出的数、错误单位、超范围、问卷非0/1或不适用时退出3，写 `problems.json` 和含论文卡片的中文问题报告，不保留先前的计算结果。

## 资料与解释

只向用户索取个人测量和问卷，不索取全文、补充表、队列数据或代码。运行无需联网。原文评分已冻结在 `scripts/presets.py`，来源与表格歧义见 `references/contract.md` 和 `references/claims.md`。

报告先放论文卡片，再写七项得分、总分和切点。表1饮食行标签容易误读，按第727页正文，每天吃蔬果为零分。BMI恰25为零分，恰30为一分。不得混入家族史分值、65岁以上年龄分档或后续版本的风险百分比。

每份报告必须原样保留：

> 边界：这是芬兰人群研究中的筛查评分，适用范围为35–64岁、评估时未接受降糖药治疗者；结局是随访期间开始药物治疗的糖尿病，不是全部新发糖尿病。分数不是个人患病概率，也不能诊断或排除糖尿病；在中国人群中的准确性未由本论文验证。目标情景只表示评分规则下的变化，不代表干预效果，不能据此开始或停止任何药物。

不提供药物剂量，不以低分建议省略已安排的检查。
