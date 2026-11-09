---
name: mci-two-year-dementia-conversion
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Estimates, for a person already diagnosed with mild cognitive impairment, the
  calibrated probability of converting to dementia within 24 months from six memory-clinic scores
  (MMSE, CDR global, CDR sum of boxes, ADAS-Cog 11, ADAS-Cog 13, FAQ), using the cognitive-scores
  XGBoost model the authors of Simkhada et al., GeroScience 2026 published with their ADNI analysis.
  States whether the probability is above that model's own threshold. The paper's headline multimodal
  model (APOE ε4, education and 323 FreeSurfer MRI measures) is not computed. Use when the user asks
  whether their MCI will progress, about dementia conversion risk, or brings MMSE, CDR, ADAS-Cog or
  FAQ results. Medicines and checkup labs do not change the result. The report does not say what to
  start or stop.
---

# 轻度认知障碍两年内转为痴呆的概率

用户交一份六项量表成绩表，可选现用药和体检。不要向用户要 ADNI 数据、磁共振原始图像、FreeSurfer 输出、论文 PDF 或补充材料；模型已经在技能里（`data/cog_model.json`）。

六项必须是同一次就诊测得的。缺一项就没有概率，不要用别的数代替。这个模型只为已由医生诊断为轻度认知障碍的人定义。

## Command

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --scores SCORES.csv \
  --medications MEDS.txt \
  --labs CHECKUP.csv \
  --out out/
```

`SCORES.csv` columns are `marker,value,unit`; leave `unit` empty or write `score` (a unit such as 分 or mg/dL stops the run). Required rows, by key or any alias in `skill.json`:

- `mmse_score` (MMSE, 简易精神状态检查, integer 0–30)
- `cdr_global_score` (CDR, CDR 全局分, only 0/0.5/1/2/3)
- `cdr_sb_score` (CDR-SB, 0–18, multiple of 0.5)
- `adas11_score` (ADAS-Cog 11, 0–70)
- `adas13_score` (ADAS-Cog 13, 0–85, 0–15 above ADAS-Cog 11)
- `faq_score` (FAQ, 功能活动问卷, integer 0–30)

A value out of range, a fractional MMSE or FAQ, an impossible CDR global, a CDR-SB that is not a multiple of 0.5, or ADAS-Cog 13 not 0–15 above ADAS-Cog 11 stops the run: `out/problems.json` says why and the script exits 3. A missing score also exits 3 with the report saying which one. `out/result.json` holds `conversion_probability_pct`, `model_group` and `model_threshold_pct`.

`--medications` is one name per line; `--labs` is `项目,结果,单位`. Both are printed as context only.

PDF and scanned reports are not read; ask for the six numbers.

引用 `out/report.md`，包括 `边界:` 那一行。队列里的准确率放在「队列里的表现」一节，不要写成这个人的准确率。方法说明见 [references/claims.md](references/claims.md) 和 [references/contract.md](references/contract.md)。
