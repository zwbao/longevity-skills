---
name: omniage-mitotic-clonal-hematopoiesis
description: >-
  Computes the epiTOC2 total number of stem-cell divisions from CpG beta values using the formula and coefficients in Duzhaozhen/OmniAge. Use when the user mentions OmniAge, epiTOC2, mitotic age, or Du et al., Nature Communications 2026 (doi:10.1038/s41467-026-76038-w). Missing probes are left out of the mean, as in that package. The report does not assign a clonal-hematopoiesis probability, and checkup labs do not change the value.
---

# 干细胞分裂次数

用户交探针甲基化值、可选年龄、现用药和体检。不要向用户要原始测序或 PDF。

报告只按公式算出总干细胞分裂数。没有对上的探针时不算。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

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

`measurements.csv` 用两列 `name,value`，探针名以 cg 开头。`--age` 用来把总分裂数除以年龄。方法说明见 [references/claims.md](references/claims.md)。
