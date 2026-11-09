---
name: phenoage-acceleration-cvd-hazard
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes one person's phenotypic age (Levine PhenoAge, as printed in the Supplementary
  Methods of Yu et al., GeroScience 2026) from nine routine blood tests and chronological age, and its
  difference from chronological age. With target values it converts the change in phenotypic age into
  the paper's UK Biobank hazard ratios for incident cardiovascular disease and cardiovascular death
  per year of PhenoAge acceleration. Use when the user asks how their phenotypic age or biological
  aging relates to heart disease or stroke risk, or what reaching lab targets would mean for
  cardiovascular risk in this model. It does not compute absolute risk, the cohort residual, KDM
  biological age, or diet scores, and the report does not say what to start or stop.
---

# 表型年龄与心血管风险

用户交九项血液指标和实足年龄，可选目标值。不要向用户要论文 PDF、补充材料、英国生物银行数据或 NHANES。系数已经在技能里。

## Command

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --biomarkers BIOMARKERS.csv \
  --age AGE \
  --targets TARGETS.csv \
  --out out/
```

`BIOMARKERS.csv` columns are `marker,value,unit`. Required markers: `albumin_gL` (g/L), `creat_umol` (µmol/L), `glucose_mmol` (mmol/L), `crp_mg_dl` (mg/dL), `lymph_pct` (%), `mcv_fl` (fL), `rdw_pct` (RDW-CV, %), `alp_u_l` (U/L), `wbc_10e3` (10^3/µL). Chinese report names (白蛋白, 肌酐, 葡萄糖, 超敏C反应蛋白, 淋巴细胞百分比, 平均红细胞体积, RDW-CV, 碱性磷酸酶, 白细胞计数) and common units are accepted; `skill.json` lists every name, unit and range. CRP must state its unit (mg/L read as mg/dL shifts the age by years).

A missing marker, a missing age, an unknown unit or a value outside its range stops the run: `out/problems.json` says what to measure or fix, and the script exits 3.

`--targets` is optional, same columns, only the markers the person wants to change. Then `out/levers.json` and `out/result.json` hold the phenotypic-age change and the model hazard ratios (target state against current state, same chronological age). Without targets no personal hazard ratio is given, because the paper's PhenoAge acceleration is a cohort residual whose regression coefficients are not printed.

IDAT and PDF files are not read.

Quote `out/report.md`, including the `边界:` line. Method notes: [references/contract.md](references/contract.md), [references/claims.md](references/claims.md).
