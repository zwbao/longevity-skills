---
name: blood-epigenetic-intrinsic-capacity
description: >-
  Tier A personal readout, checked against independent implementations: the paper prints no worked
  example, so no printed result was reproduced. Computes the blood DNA-methylation intrinsic-capacity
  score (DNAm IC) of Fuentealba et al., Nature Aging 2025, from a person's beta values at the 91 CpGs,
  using the intercept and elastic-net coefficients printed in Supplementary Table 1. Every site must
  be supplied. Use when the user mentions the IC clock, DNAm intrinsic capacity, or a blood epigenetic
  intrinsic-capacity clock. Current medicines and checkup labs are context. The report does not say
  what to start or stop.
---

# 甲基化内在能力

你交血液甲基化芯片（Illumina EPIC）上 91 个位点的 β 值，以及现用药和体检。报告按补充表 1 的截距和系数算甲基化内在能力（截距加每个位点系数乘 β 值）。位点缺一个、β 值不在 0 到 1 之间，或单位写成百分比，报告只列原因、不计算，命令返回 3。论文没有印出可以复现的个人示例，所以这个读出仍是草稿。不做死亡预测。报告最后一行是固定边界，不能据此开始或停止任何药物。

不要向用户要 GEO、STRING、UK Biobank 或 PDF。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --out out
```

`--measurements` 用 `item,value,unit`，`item` 是 cg 号，`value` 是 β 值，单位列可以空着。`skill.json` 列出 91 个位点和范围。`out/result.json` 写 `dnam_ic`。

方法说明见 [references/claims.md](references/claims.md) 和 [references/contract.md](references/contract.md)。
