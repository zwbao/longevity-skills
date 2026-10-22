---
name: semaglutide-epigenetic-aging-trial
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. Subtracts the baseline value from the week-32 value of a clock the
  user already has (PhenoAge, GrimAge2, DunedinPACE and others, computed elsewhere) and sets the
  paper's between-arm difference for that clock beside it, from the semaglutide HIV lipohypertrophy
  trial in Nature Communications 2026. The paper reports group comparisons and no personal model; the
  skill computes no clock. Use when the user brings paired clock values, medicines, or checkup labs
  from that trial context. The skill does not turn a clock change into advice to start or stop
  semaglutide.
---

# 表观遗传时钟变化

用户交某个时钟的基线和第 32 周数值、现用药和体检。不要向用户要 GEO、STRING 或 PDF。

组间差别不是个人权重。报告只算第 32 周减基线，并在这个变化旁边放上论文里该时钟的一个组间数字。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

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

时钟用列 `clock,baseline,week32`。
