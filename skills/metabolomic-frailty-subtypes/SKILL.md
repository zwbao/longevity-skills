---
name: metabolomic-frailty-subtypes
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. In Xiao et al., npj Digital Medicine 2025 the four frailty subtypes
  come from K-means clustering on the first two principal components of eleven standardized NMR
  metabolites in frail participants; the PCA loadings and cluster centres are not published, so a
  person cannot be assigned the way the paper did. The script only finds which Table 2 subtype mean
  the eleven supplied Nightingale NMR metabolites are nearest to, an approximation of its own, not the
  paper's classifier. Use when the user mentions metabolomic frailty subtypes, GlycA, LGVF, HALF,
  LALF, HGVF, or this 11-metabolite panel. Current medicines and checkup labs are context. The report
  does not say what to start or stop.
---

# 代谢衰弱亚型

论文的亚型是在衰弱者里先做主成分、再在前两个主成分上 K 均值聚类得到的，载荷和聚类中心没有公布。这里按表二的亚型均值找最近的一个，只是近似，不等于论文的分型。

用户交十一个核磁共振代谢物、现用药和体检。不要向用户要英国生物银行、GEO 或 PDF。未公布的聚类中心不要写成已经跑过。

报告只算到四个已发表亚型均值的距离。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --metabolites mets.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --out out/
```

`mets.csv` 用两列 `name,value`。可选 `--fi` 和 `--diet` 不改变亚型。方法说明见 [references/claims.md](references/claims.md)。
