---
name: biological-age-ct-cardiometabolic
description: >-
  Tier B lookup (human): what the paper reports about named entities, not a validated personal score.
  Places one person's abdominal CT cardiometabolic biomarkers next to the Table 2 median values of
  people who survived or died within five years of CT, from Pickhardt et al., Nature Communications
  2025 (doi:10.1038/s41467-025-56741-w). The paper's CT biological age model (Cox with splines) has no
  published coefficients, so the script does not compute it. Use when the user mentions CT biological
  age, CTBA, muscle density, aortic calcium, or this paper. The report lists biomarkers nearer the
  died-within-five-years median, ordered by Table 1 IPA drop; "nearer" is a plain distance check by
  this skill, not the paper's model. It does not estimate survival or say which medicine to start or
  stop.
---

# 腹部影像生物标志

用户交腹部影像测量、年龄、性别、现用药和体检。不要向用户要样条系数或 PDF。论文的 CT 生物年龄模型系数没有公开，所以 CT 生物年龄和生存概率都算不出来。

报告只把更靠近死亡中位数的标志按论文 Table 1 的贡献从大到小排列；“更靠近”是本技能的简单距离对照，不是论文的模型。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --measurements ct.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --age 55 \
  --out out/
```

`ct.csv` 用两列 `name,value`，并写上 `sex`。`--age` 用来选年龄段。方法说明见 [references/claims.md](references/claims.md)。
