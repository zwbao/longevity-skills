---
name: nanopore-parent-origin-methylation
description: >-
  Tier B lookup (human): what the paper reports about named entities, not a validated personal score.
  Applies the published lasso coefficients of the nanopore methylation clock (Supplementary Data 3) to
  methylation values the user supplies already standardized, and otherwise only subtracts numbers:
  methylation age minus chronological age, or paternal minus maternal methylation at a site. The
  coefficients act on values standardized with the training cohort's means and standard deviations,
  which are not published, so a person's own raw methylation proportions cannot be turned into the
  paper's methylation age, and the paper prints no per-person example. Use when the user brings
  methylation measurements, medicines, or checkup labs for this parent-of-origin methylation clock. It
  does not turn the result into advice to start or stop a medicine.
---

# 印记位点甲基化读出

用户交标准化后的甲基化，或已经算好的甲基化年龄和实足年龄，或某个位点的父本和母本甲基化，以及现用药和体检。不要向用户要 GEO、STRING 或 PDF。

标准化数值按已发表的套索系数算甲基化年龄，没测到的位点按 0 代入。训练均值和标准差不在表里，所以原始比例不会重缩放，个人自己的原始数据也就算不出论文的甲基化年龄。也可以算绝对误差和父本减母本。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --out out
```

`--measurements` 用两列 `item,value`，除非下面另说。方法说明见 [references/claims.md](references/claims.md)。
