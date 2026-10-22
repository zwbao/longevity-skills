---
name: plasma-protein-risk-score
description: >-
  Tier B lookup (human): what the paper reports about named entities, not a validated personal score.
  Sums the published Cox, LASSO, and elastic-net protein betas (Nature Aging 2024 hip-fracture protein
  score) over per-standard-deviation protein values the user supplies, and computes heel-ultrasound
  bone density from BUA and SOS when both are given. The paper's protein values are log-transformed
  and normalised within the study cohort on a SomaScan assay, so one person's own values are not on
  that scale and the sum is not a validated personal risk. Use when the user asks about this
  hip-fracture protein score. Does not turn the score into advice to start or stop a medicine.
---

# 髋部骨折蛋白读出

用户交自己的蛋白表、可选的足跟超声 BUA 和 SOS、现用药和体检。不要向用户要 GEO、STRING 或 PDF。

给了按标准差计的蛋白时，用已发表的加权、套索和弹性网系数算风险分，没测到的蛋白按 0 代入。论文的蛋白值是研究队列里对数转换、再在队列内标准化的适配体测量，个人化验拿不到同一尺度的数，所以这个分数只是按系数求和，不是论文验证过的个人风险。给了 BUA 和 SOS 时，按印出的式子算超声骨密度。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --out out
```

`--measurements` 用两列 `item,value`。超声用 `bua` 和 `sos`。蛋白行可以带 `deprecated`、`nonhuman` 或 `poor_quality` 标记（值为 1 则按方法排除）。`--medications` 每行一个药名。`--labs` 原样写入报告。

方法说明见 [references/claims.md](references/claims.md) 和 [references/contract.md](references/contract.md)。
