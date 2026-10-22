---
name: lung-parenchyma-aging-clock
description: >-
  Tier B lookup (human): what the paper reports about named entities, not a validated personal score.
  Subtracts a lung-parenchyma predicted age the user already has from chronological age (plain
  arithmetic), with context from Nature Communications 2026. The paper's XGBoost clock was not
  released as a fitted model, so this does not compute the paper's clock. Use when the user brings a
  predicted lung age, chronological age, medicines, or checkup labs. It does not turn a residual into
  advice to start or stop a medicine.
---

# 肺实质年龄残差

用户交已经算好的肺预测年龄和实足年龄，以及现用药和体检。不要向用户要 GEO、STRING 或 PDF。

配套仓库里没有保存好的预测模型，所以不从基因表达重算年龄。报告只算实足年龄减预测年龄。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --out out
```

`--measurements` 用两列 `item,value`，除非下面另说。方法说明见 [references/claims.md](references/claims.md)。
