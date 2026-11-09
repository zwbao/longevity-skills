---
name: planetary-health-diet-index
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Scores one person's diet with the Planetary Health Diet Index (PHDI, 0-140) from daily
  intakes of 15 food groups, using the cutoffs and weights printed in Supplementary Table 1 of
  Diez-Echave et al. (J Gerontol A 2026, Seniors-ENRICA cohorts of Spanish adults aged 60 and over),
  lists per-component points and the components furthest from full score, and places the total next to
  the cohort's printed tertile means and the frailty odds ratios (highest vs lowest tertile, per 20
  points). Use for 地球健康饮食, EAT-Lancet 饮食, 植物为主饮食评分, 饮食与衰弱, planetary health diet, PHDI. States that
  tertile cut points are not printed, that the odds ratios are population associations rather than a
  personal frailty probability, and does not prescribe a diet or medicine.
---

# 地球健康饮食指数（PHDI）与衰弱

用户交 15 类食物的每日平均摄入和性别，年龄可选。不要向用户要论文、PDF 或补充表，切点和权重已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements diet.csv --sex female --age 68 --out out
```

可选 `--targets targets.csv`（同样的列，写目标摄入）：`out/levers.json` 给出每项每单位摄入值几分、每个目标单独达成和全部达成时 PHDI 的变化。

`diet.csv` 的列是 `item,value,unit`：

- 第 1–12 项按克/天（`g/d`）：全谷物、薯类、蔬菜（不含土豆）、完整水果、奶类、红肉和加工肉、禽肉、蛋、鱼和贝类、坚果、非大豆豆类、大豆和豆制品。
- 第 13–15 项按占总能量的百分比（`%`，也接受小数 `1`）：不饱和植物油、饱和与反式脂肪、添加糖和果汁糖。用中文名写这三项时必须写单位，防止把克数当成百分比。
- 名称也认 蔬菜、水果、红肉、坚果、植物油、添加糖 等，`skill.json` 列出全部。

何时选参数：性别必填（全谷物满分线女性 75 克/天、男性 90 克/天）；年龄只用于提示是否在论文人群（60 岁及以上）内。

15 项缺任何一项、单位不认识、数值超出范围或性别没写时不计算：报告写明哪一项、为什么，脚本退出码 3，助手据此告诉用户还要估哪一项。`out/result.json` 给出 `phdi_total` 和 15 个 `score_*`。

## 报告里必须保留的话

- 论文没有印出三分位切点，报告不判断个人属于哪个三分位，只列 Table 1 的三分位平均分。
- 比值比是西班牙社区老人队列里的人群关联（GEE 模型 3），不是个人衰弱概率，也不说明因果。
- 不给饮食处方，不叫人开始或停止任何药物；有慢病或特殊饮食需要时先问医生或营养师。

验证状态是草稿：论文没有印出个人算例，测试核对切点与补充表 S1 一致、分数范围 0–140。引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
