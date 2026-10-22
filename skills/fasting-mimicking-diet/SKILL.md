---
name: fasting-mimicking-diet
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. Subtracts two biological ages the user already has (computed
  elsewhere by the same method) and sets the difference beside the trial's reported change. It cannot
  compute the paper's Klemera-Doubal biological age: Supplementary Table 2 prints the seven slopes,
  intercepts and residuals, but the age-gap variance s_BA^2 the equation needs is printed nowhere.
  When chronological age is supplied it also shows the trial-cohort regression of change on baseline
  age from the authors' Zenodo note, which is a group fit, not a personal model. Use when the user
  mentions a fasting-mimicking diet, FMD biological age, or this kind of trial. Current medicines and
  checkup labs are context. The report does not say what to start or stop.
---

# 临床生物年龄的前后差

你交两次生物年龄，或一次生物年龄加实足年龄，以及现用药和体检。报告只写后一次减前一次；有实足年龄时再列出作者 Zenodo 说明里按试验人群拟合的变化回归，那是群体拟合，不是个人模型。七项化验的斜率、截距和残差在补充表里，但年龄差方差没有印出，所以不把化验重算成生物年龄。报告最后一行是固定边界，不能据此开始或停止任何药物。

不要向用户要 GEO、STRING、UK Biobank 或 PDF。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --age 50 \
  --out out
```
`--measurements` 用 `item,value,unit`，单位列可以空着，空着就按 `skill.json` 里的单位读。`biological_age_baseline` 和 `biological_age_followup` 是前后两次生物年龄（岁），两次要用同一种方法算，比如都用表型年龄技能输出的 `phenoage`；不要填生物年龄减实足年龄的差。可选的 `glucose_mg_dl`（空腹血糖，写 mmol/L 时单位列要写明）和 `bmi` 只照录，不进计算。`skill.json` 列出能认的名字、单位和范围。数值不在合理范围、单位不能换算或写不成数时，报告只列原因、不计算，命令返回 3。`out/result.json` 写 `bioage_change` 和 `bioage_change_predicted`。
