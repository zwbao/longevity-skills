---
name: sasp-senescence-score
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes one person's SASP Score, a deep-learning composite of 38 plasma
  senescence-associated secretory proteins (Zhao et al., Aging Cell 2026), by running the authors'
  released pre-trained GAET model on the person's Olink Explore NPX values on the UK Biobank Pharma
  Proteomics scale, and places it against the paper's high-score cutoff of 65. Use when the user has
  Olink proteomics and asks about cellular senescence burden, SASP, senescence score, 衰老细胞负荷 or
  衰老分泌表型. Stops on concentrations (pg/mL), missing proteins or another platform's NPX scale. Does not
  compute an age gap, per-protein contributions or a personal disease risk, and the report does not
  say what to start or stop.
---

# SASP 衰老分泌表型评分

用户交一份 38 个蛋白的 Olink Explore NPX 表（marker,value,unit，单位写 NPX）。模型权重已经冻在 `data/` 里，不要向用户要论文 PDF、补充表、GitHub 仓库或 UK Biobank 数据。

38 个蛋白必须齐。单位写 pg/mL、ng/mL 的化验结果不能换成 NPX，脚本会停下（退出码 3，写 `out/problems.json`）。不在 UKB-PPP 标度上的 NPX（例如 Olink Target 96）也会停下：论文对别的平台要整组微调，一个人做不到。

## Command

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" --proteins PROTEINS.csv --out out/
```

## 报告必须保留

- 开头的论文卡片。
- 分数不是年龄，不算年龄差；65 分切点是论文的人群分组。
- 边界句：这是 UK Biobank 人群里建立的研究用评分，只适用于和 UKB-PPP 同一标度的 Olink Explore NPX 数据；它和死亡、慢病的关联是人群统计，不是你个人的诊断或预测，也不能据此开始或停止任何药物、补充剂或治疗。

产品合同和取舍见 `references/contract.md`，论文与代码的对照见 `references/claims.md`。
