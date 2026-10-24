---
name: digital-telomere-measurement-sequencing
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. Gives plain descriptive statistics (minimum, quartiles, median,
  mean, maximum) of the per-read telomere lengths a person supplies, as measured by the digital
  telomere method of Sanchez et al., Nature Communications 2024. That is generic arithmetic, not the
  paper's model: the paper's logistic-regression weights for telling healthy aging from telomere
  disease are not published. Use when the user mentions Telometer, digital telomere measurement, or
  this nanopore telomere paper. Medicines and checkup labs stay context.
---

# 端粒长度分布

你交端粒长度。至少有两条时，报告写出最小值、四分位、中位数、平均数和最大值。少于两条时，报告说明没有算出分布。

不要向用户要 BAM 或 PDF。逻辑回归系数不在仓库里，不要另造。现用药对不上时写「不能据此停」。体检不增删这些概括数。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --age 50 \
  --out out
```

方法说明见 [references/claims.md](references/claims.md) 和 [references/contract.md](references/contract.md)。
