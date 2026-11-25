---
name: new-chinese-diabetes-risk-score
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Uses age, sex, waist circumference, BMI, systolic blood pressure and first-degree
  family history to calculate the New Chinese Diabetes Risk Score for adults without diagnosed
  diabetes. Use for nonlaboratory diabetes screening, 新中国糖尿病风险评分, or asking how personal measurements
  affect this score. Reports points and the published screening threshold in Chinese, with optional
  user-supplied target scenarios.
---

# 新中国糖尿病风险评分

按 Zhou 等（Diabetes Care，2013）的 Table 2 计算六项分数，总分0–51，≥25分为达到筛查阈值。用于中国未确诊糖尿病成人20–74岁；不是既往青岛四变量评分，也不是糖尿病诊断或个人三年发病率模型。

用户命令：

> 用我的年龄、性别、腰围、BMI、收缩压和一级亲属糖尿病史，算新中国糖尿病风险评分；如有我提供的目标，比较目标下的分数。

先确认是否已由医生诊断糖尿病，已确诊不运行评分。年龄用已满周岁整数；未知家族史不能代填“无”。性别按原文Men/Women分类传male/female；无法映射时先说明方法限制，不猜测。

## 输入与运行

测量CSV为`marker,value,unit`，需要腰围、BMI、收缩压和一级亲属糖尿病史四行。腰围测下肋缘与髂嵴之间中点处；收缩压使用测量均值（推导组两次、验证组三次）；BMI为体重kg除以身高m的平方。家族史指父母、兄弟姐妹或子女中有人患糖尿病，填1（有）或0（无），单位1。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 50 --sex male --known-diabetes no --out out
```

目标比较时加`--targets targets.csv`，表头相同，仅允许腰围、BMI和收缩压。目标由用户给出，禁止把年龄、性别、家族史作为干预目标。单位、别名、范围由`skill.json`和`skillkit`处理；不自行补缺项。

输入缺失、单位错误、超范围、未知项目、家族史非0/1或不适用时退出3，并写`out/problems.json`和含论文卡片的中文错误报告；不保留上一次的评分文件。

## 输出与解释

- `out/report.md`：先论文卡片，再逐项得分、总分和筛查分层。
- `out/result.json`：总分、分层和六项得分。
- `out/levers.json`：当前六项输入的有限变化敏感度、可改变指标的相邻分档边界；有目标时增加单项与全部目标情景。

分数是阶梯函数，同档内改变可能为零。相邻低分档的上界是严格小于，不能把边界本身算进低分档。BMI和腰围等单独变化只是数学情景，不代表独立可行的干预。使用者无需提供论文、公共队列或补充文件；正文计算常数已内置，运行无需联网。

补充材料的DC1链接受限、未取得；详见`references/sources.md`。只复现正文表2的逐项分数，不声称复现AUC、敏感度或三年发病率。超出推导组保留测量范围会提示外推；年龄超过范围直接停止。

每份报告必须保留：

> 边界：本评分用于中国成人未诊断糖尿病的筛查分层，不是诊断，也不是个人三年发病概率；低于阈值不能排除糖尿病，目标情景的分数变化不代表干预效果，不能据此开始或停止药物。
