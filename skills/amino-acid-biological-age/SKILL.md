---
name: amino-acid-biological-age
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. The amino-acid clock of Ding et al., Nature Communications 2026
  (doi:10.1038/s41467-026-73371-y) is a random forest whose trained model is not published (the code
  repository has only training code), so the script cannot compute an amino-acid age or age gap. It
  only divides each of the eight amino-acid concentrations of the simplified model by their sum, which
  are input features of that model, not a score. Use when the user mentions AmiAge, an amino-acid age
  clock, or this paper. Checkup labs do not change the amino-acid list.
---

# 氨基酸比例

论文的氨基酸年龄是随机森林模型，训练好的模型没有公开，所以这里算不出年龄，也没有年龄差。脚本只做一件事：把八种氨基酸各自除以八种之和。这些比例是模型的输入特征，不是评分。

用户交氨基酸浓度、现用药和体检。不要向用户要随机森林权重或 PDF。生物年龄算不出来。

八个浓度都有时，报告把每个浓度除以这八个的和。缺任何一个就不算比例。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --age 60 \
  --out out/
```

`measurements.csv` 用两列 `name,value`。方法说明见 [references/claims.md](references/claims.md)。
