---
name: ulk1-autophagy-alzheimers
description: >-
  Tier B lookup (human, cultured cells, mouse, C. elegans): what the paper reports about named
  entities, not a validated personal score. Pan et al., Nature Aging 2026 reports that serum and CSF
  ULK1 fall with ageing and Alzheimer disease in cohorts, plus mouse, worm and cell experiments; it
  defines no personal score, and ULK1 is a research assay. The script only does generic arithmetic,
  the percent change between a supplied baseline and follow-up ULK1, shown beside the paper's cohort
  declines, and lists the four ULK1 compounds named in the paper. Use when the user mentions ULK1,
  autophagy or mitophagy in Alzheimer disease, Rac-BL-918, or LYN-1604. Current medicines and checkup
  labs are context. The report does not say what to start or stop.
---

# 血清和脑脊液里的自噬激酶

论文没有给个人计算方法；这里只把你给的两次 ULK1 算成百分比变化，是普通算术，再和论文的队列下降并排。ULK1 是研究用检测。

你交 ULK1 的基线和随访。两个数都有时，报告写出变化百分比，旁边放论文里对应的一次下降。名单里的化合物是细胞实验里的名字，不是给你的剂量。基线和随访缺一个时，报告说明没有算出变化。

不要向用户要 GEO 或 PDF。不要把下降写成一套系数。现用药对不上时写「不能据此停」。体检不增删化合物。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --out out
```

方法说明见 [references/claims.md](references/claims.md) 和 [references/contract.md](references/contract.md)。

