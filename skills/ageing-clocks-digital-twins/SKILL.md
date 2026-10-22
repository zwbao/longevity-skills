---
name: ageing-clocks-digital-twins
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. For biological ages that other clocks already produced, it computes
  the unscaled within-person stability index described in Pusparum et al., npj Digital Medicine 2025
  (DOI 10.1038/s41746-025-01911-9): the reciprocal of the mean absolute pairwise difference between
  time points. It does not compute any clock; the paper publishes no new clock coefficients, does not
  print its 0–1 scaling, and prints no per-person example to reproduce. Use when the user brings
  repeated biological-age estimates and asks about this digital-twin clock comparison or the IAM
  Frontier analysis. For the Skin and Blood clock, a supplied time in years is compared with the
  printed technical-replicate limit of 2.56 years plus elapsed time.
---

# 时钟稳定度

用户交已经算好的生物年龄、现用药和体检。不要向用户要 GEO、STRING 或 PDF。

同一时钟至少两个时间点时，报告只把你交来的数相减：算两两绝对差均值的倒数，即论文稳定度的未缩放形式。论文没有写出缩放到 0–1 的方法，也没有印出个人示例，所以这个数不能和论文图里的稳定度直接比较；它也不重新计算任何时钟。对不上的时钟不进名单。药名对不上时保留「不能据此停」。体检不增删方法算出的名单。

## Command

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements MEASUREMENTS.csv \
  --medications MEDS.txt \
  --labs CHECKUP.csv \
  --out out/
```

`MEASUREMENTS.csv` needs columns `clock` and `biological_age`, with one row per time point. An optional `time_years` column is used only for the Skin and Blood clock. Clocks that appear once are listed and not given a stability number.

`biological_age` is the clock's age in years at that time point, not an age gap and not a pace such as DunedinPACE; an optional `unit` column may only say years. The `phenoage` clock is the paper's DNA-methylation PhenoAge. A phenotypic age from nine blood chemistries (the `phenoage` output of accelerated-biological-aging-risk) goes under the clock name `血检表型年龄`, or in an `item,value,unit` table with rows `phenoage_visit1` to `phenoage_visit4`, oldest first. It is listed as outside the paper's clock table. `skill.json` declares these inputs, their unit and the 0–130 year range. A value out of range, an unknown unit, a value or time that is not a number, or a table without a `biological_age` column stops the computation: the report lists why and the script exits 3. Rows for clocks outside the list are ignored, as before. `out/result.json` holds `stability_index_<clock>` for every listed clock (null when not computed).

`--medications` is optional, one name per line. `--labs` is optional. Abnormal checkup rows are printed and do not add or remove names from the method list. A medicine that is not on that list keeps the sentence 不能据此停.

## Report

Copy `out/report.md`, including its final `边界:` line. The report gives the unscaled stability index for clocks with at least two time points. Cohort correlations stay in [references/claims.md](references/claims.md). It may not tell the user which clock to act on.

Method notes: [references/contract.md](references/contract.md), [references/claims.md](references/claims.md). The command is also in [examples.md](examples.md).
