---
name: blood-protein-assessment
description: >-
  Tier B lookup (human): what the paper reports about named entities, not a validated personal score.
  Sums the published elastic-net coefficients of Gadd et al., Nature Aging 2024 times protein levels
  the user supplies already transformed, for each outcome whose proteins are all present. The paper
  rank-based inverse normalises proteins within its training and test sets, so one person's Olink
  values cannot be put on that scale alone; this is a research recalculation, not a validated personal
  score. Use when the user mentions ProteinScore, blood protein incident disease, or a UK Biobank
  proteomic risk score. Current medicines and checkup labs are context. The report does not say what
  to start or stop.
---

# 血液蛋白与发病

你交已经缩放到均值 0、标准差 1 的蛋白量、现用药和体检。论文是在一整批样本内做秩逆正态变换再缩放，单个人的一份蛋白检测结果没法自己换到这个尺度上。某个结局的蛋白到齐时，报告用补充表的系数加总成线性预测值。糖化血红蛋白只写在第一段，不增删这个名单。报告最后一行是固定边界，不能据此开始或停止任何药物。

不要向用户要 GEO、STRING、UK Biobank 或 PDF。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --age 50 \
  --out out
```
`--measurements` 用 `item,value`。蛋白用基因符号，数值是模型里的缩放量。`hba1c` 的单位沿用 mmol/mol。
