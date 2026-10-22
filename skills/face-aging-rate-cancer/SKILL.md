---
name: face-aging-rate-cancer
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. Divides the difference between two FaceAge values the user already
  has by the years between the photographs (the Face Aging Rate definition in Haugg et al., Nature
  Communications 2026, doi:10.1038/s41467-025-66758-w) and places it beside the printed interval
  cutoffs (above 20, 10, or 1). FaceAge itself is a deep-learning output that is not run here, so a
  photograph is not scored. Use when the user mentions FAR, FaceAge, or serial face photographs in
  cancer care. The cohort hazard ratio is not a personal hazard; labs do not change the rate.
---

# 面容老化速率

用户交两次面容年龄和间隔天数、现用药和体检。不要向用户要照片模型或 PDF。不能从照片估计面容年龄。

报告算两次面容年龄的差除以间隔的历法年数，并对照这一档印出的界。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --age 60 \
  --out out/
```

`measurements.csv` 用两列 `name,value`，需要 `face_age_1`、`face_age_2` 和 `interval_days`。方法说明见 [references/claims.md](references/claims.md)。
