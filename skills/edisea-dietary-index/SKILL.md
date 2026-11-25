---
name: edisea-dietary-index
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes one person's EDISEA (Empirical Dietary Index for Slower Epigenetic Aging, Lai
  et al., Nature Communications 2026) from usual servings per day of ten food groups (tea, whole
  grains, fruit, fries, liquor, beer, processed meat, sugar-sweetened and artificially sweetened
  beverages, margarine), optionally rescaled to servings per 2000 kcal with total energy, using the
  full-precision Source Data Fig. 2b weights. Reports each food's contribution beside the paper's
  printed Q1/Q5 median intakes and writes per-serving levers for target intakes. Does not give a
  cohort percentile, years of GrimAge2 acceleration, or a mortality or disease risk. Use when the user
  asks whether their diet matches an epigenetic-aging diet score, EDISEA, or how tea, alcohol, fries
  or sweet drinks weigh in a diet index linked to slower biological aging.
---

# 表观衰老饮食指数 EDISEA

用户交十类食物平时每天吃几份（不吃填 0），可选每日总能量（千卡）和性别。权重已经在技能里，不要向用户要论文、补充表、HRS 或 GitHub 文件。

## Command

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" --intake INTAKE.csv --sex SEX --targets TARGETS.csv --out out/
```

`INTAKE.csv` columns are `item,value,unit`. Items: `tea_serv_d`, `whole_grains_serv_d`, `fruits_serv_d`, `fries_serv_d`, `liquor_serv_d`, `beer_serv_d`, `processed_meat_serv_d`, `ssb_serv_d`, `asb_serv_d`, `margarine_serv_d` (servings per day, leave the unit empty), and optional `energy_kcal_d` (kcal per day). Chinese names work too (茶, 全谷物, 水果, 薯条, 烈酒, 啤酒, 加工肉, 含糖饮料, 代糖饮料, 人造黄油, 总能量); `skill.json` lists every accepted name and range. All ten foods are required: a missing food, a value outside 0–30 servings/day, energy outside 500–6000 kcal (kJ entered as kcal lands here), or any unit stops the computation; the report says why and the script exits 3.

`--sex` only flags energy outside the paper's plausibility range. `--targets` takes target servings per day in the same columns and writes `out/levers.json`. `out/result.json` holds `edisea`.

Without total energy the servings are used as given, as if the day were 2000 kcal; the report says so. The paper adjusted energy by the residual method, whose cohort coefficients are not published; this skill rescales to servings per 2000 kcal instead (see [references/contract.md](references/contract.md)).

引用 `out/report.md`，包括 `边界:` 那一行。不要把分数说成“慢几岁”或死亡风险；论文的年数和风险比是人群分位比较。方法说明见 [references/claims.md](references/claims.md)。
