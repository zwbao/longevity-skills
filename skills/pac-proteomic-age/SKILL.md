---
name: pac-proteomic-age
description: >-
  Tier A personal readout, checked against independent implementations: the paper prints no worked
  example, so no printed result was reproduced. Computes one person's PAC proteomic age (Kuo 2024
  Gompertz mortality clock) from the 128 Olink Explore NPX values it uses plus chronological age, as
  run in the rentosertib phase 2a trial re-analysis (Zhavoronkov et al., Nature Biotechnology 2026).
  Reports PAC age, PAC minus chronological age, the model's 10-year mortality estimate, and, when an
  earlier sample is given, the change between the two samples (the paper's ΔBioAge). All 128 proteins
  are required; none is imputed. Use when the user has an Olink Explore 3072 export (NPX) and asks for
  a proteomic age, a blood protein clock, or a before/after protein-clock comparison. Does not compute
  ProtAge, OrganAge, ipfP3GPT or PAOPAC, does not evaluate any drug, and never says to start or stop a
  medicine.
---

# PAC 蛋白质组年龄

用户交一份 Olink Explore 的 NPX 表（每行一个蛋白）和采血那天的实足年龄；可以再交同一个人更早的一份 NPX 和那时的年龄，看前后变化。不要向用户要补充表、OMIX 数据、GitHub 代码或 PDF：128 个系数和 Gompertz 参数已经在 `scripts/presets.py` 里。

## Command

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --measurements NPX.csv \
  --age AGE \
  --baseline BASELINE_NPX.csv \
  --baseline-age BASELINE_AGE \
  --medications MEDS.txt \
  --labs CHECKUP.csv \
  --out out/
```

- `NPX.csv` 列为 `marker,value,unit`：`marker` 写 Olink 的基因符号（如 `LTBP2`、`GDF15`、`FUT3-FUT5`），`value` 是 NPX，`unit` 留空或写 `NPX`。文件里多出的蛋白会忽略。pg/mL、ng/mL 等浓度不能换算成 NPX，会被拒绝。
- IL6 在 Olink Explore 的几个面板里各测一次，导出表可能有几行 IL6；数值不同时脚本会停下，请只保留一行（论文和 PAC 代码都没写用哪一个面板）。
- 128 个蛋白必须全部有值；缺一个就不算，报告列出缺哪些（Olink Target 96 面板一般不够，需要 Explore 3072 或含这些检测的 Explore 面板）。
- `--baseline` 和 `--baseline-age` 只在要看前后变化时给，两者要一起给；两份样本最好在同一 Olink 批次测。
- `--medications`、`--labs` 只作背景，不改变结果。
- 输入有错（单位、超范围、缺蛋白、缺年龄、给了 xlsx/PDF）时脚本退出 3，写 `out/problems.json`，报告写明原因，不出数字。正常时 `out/result.json` 含 `pac_age`、`pac_age_gap`、`pac_mortality_10y_pct`、`baseline_pac_age`、`pac_age_change`。

引用 `out/report.md`，包括开头的论文卡片和 `边界:` 那一行。方法与出处见 [references/claims.md](references/claims.md)，产品合同见 [references/contract.md](references/contract.md)。
