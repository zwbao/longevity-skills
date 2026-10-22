---
name: retinal-aging-biomarkers-longitudinal
description: >-
  Tier B lookup (human): what the paper reports about named entities, not a validated personal score.
  Subtracts chronological age from a retinal age the user already has, or from the expectation over
  the 77 age-bin probabilities the model outputs, and places that gap beside the published 2.79-year
  mean absolute error. The retinal age model from this npj Digital Medicine 2025 paper is released
  only on request and its weights are not here, so the script does not run it or check the retinal
  age. Use when the user mentions retinal age, RLDL, label distribution learning, or this paper. Labs
  do not change the gap. The report does not say what to start or stop.
---

# 视网膜年龄差

用户交现用药、体检、实足年龄，以及视网膜预测年龄或年龄箱概率。不要向用户要 GEO、STRING 或 PDF。

论文的视网膜年龄模型要向作者申请，这里不运行它。两项年龄都有时，报告用视网膜年龄减去实足年龄。缺一项时名单是空的。药名对不上时保留「不能据此停」。体检不增删方法算出的名单。

## Command

```bash
python "$SKILL/scripts/personal_report.py" \
  --medications meds.txt \
  --labs checkup.csv \
  --retinal-age 60 \
  --age 50 \
  --out out/
```

另可给 `--probs probs.txt`，77 行且和为 1，对应仓库里 0 到 76 的移位年龄，再加回 15 岁。

把 `out/report.md` 整段交给用户，包括最后一行 `边界:`。
