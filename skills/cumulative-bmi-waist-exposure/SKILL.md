---
name: cumulative-bmi-waist-exposure
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes one person's cumulative BMI and waist-circumference exposure (cBMI, cWC) from
  three of their own measurements, with the cut points of Yu et al. (GeroScience 2026, Rugao
  Longitudinal Ageing Study, adults over 70): the amount above BMI 24 kg/m2 and waist 90 cm (men) or
  80 cm (women), times the years between visits. Also gives the latest BMI group (Chinese criteria)
  and where the values sit against the cohort median and quartiles, with the printed cohort
  associations with KDM-BA biological age. Use for 累积肥胖, 累积BMI, 累积腰围, 超重多少年, 胖了几年, 老人体重, 腰围和衰老. Does
  not compute a personal biological age or the longevity polygenic score.
---

# 累积 BMI 与腰围暴露（如皋老年队列方法）

用户交自己三次测量的 BMI 和/或腰围（按时间先后），以及两段间隔的年数；算腰围时要性别。不要向用户要论文、补充表或基因数据，切点和队列数字已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements obesity.csv --sex female --age 78 --out out
```

`obesity.csv` 的列是 `item,value,unit`：

- `BMI 1`、`BMI 2`、`BMI 3`（kg/m²）：三次 BMI，第三次是最近一次。
- `腰围1`、`腰围2`、`腰围3`（cm，也接受 mm、in）：三次腰围。
- `间隔1`、`间隔2`（年，也接受 mo、d）：第一到第二次、第二到第三次之间的时间。必填。
- BMI 和腰围至少齐一组；只齐一组时只算那一组。`skill.json` 列出全部别名。

报告给出累积 BMI 暴露（kg/m²×年）、累积腰围暴露（cm×年；女性另按 85 cm 再算一次）、最近一次的 BMI 分组，以及相对论文队列中位数和四分位数的位置；再引用补充表 2、4 里这一类人的 KDM-BA 平均差别。

某一组只给了一两次、单位不认识、数值超出范围、算腰围却没给性别时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `cbmi_kg_m2_years`、`cwc_cm_years`、`cwc_cm_years_female_85cm` 和 `baseline_bmi_group`。

## 报告里必须保留的话

- 累积暴露不是生物年龄，也不是诊断；论文的关联来自观察研究，不能说明因果，不能把每单位的系数乘上去推算个人老了几岁。
- 论文没有印出三分位界值，所以不说用户属于 T1、T2 还是 T3；长寿多基因评分的中位数没有印出，所以不算基因评分。
- 不给减重目标或方法；体重和腰围管理请和医生一起定，高龄时非故意的体重下降要请医生看。

验证状态是草稿：论文没有印出个人算例，超出量与年数怎样相乘是本技能的操作定义（梯形面积）。引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
