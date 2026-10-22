---
name: circadian-frailty-older-adults
description: >-
  Tier B lookup (human): what the paper reports about named entities, not a validated personal score.
  Computes relative amplitude, (M10−L5)/(M10+L5), and the 0 to 2 fatigue score from the two CES-D
  items, both as defined in Cai et al., Nature Communications 2023. The paper reports per-SD hazard
  ratios, not a personal risk equation, and does not print the sex-specific quintile cutoffs for the
  frailty phenotype, so the script does not say whether someone is frail or estimate frailty risk. Use
  when the user mentions circadian rest-activity rhythms and frailty in older adults or this study.
  Medicines and checkup labs do not edit the list.
---

# 昼夜活动与衰弱

用户交最活跃十小时和最不活跃五小时的活动计数、两条疲劳问答，以及现用药和体检。不要向用户要 Rush 数据、STRING 或 PDF。

报告开头是论文卡片。论文没有个人衰弱风险方程，衰弱表型的五分位切点也没印，所以报告不判断是否衰弱。相对振幅按 (M10−L5)/(M10+L5) 计算。疲劳分是两道题的和，每题「是」记 1 分。握力、步速、体质指数和活动小时不套五分位。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" \
  --medications meds.txt \
  --labs checkup.csv \
  --age 60 \
  --measurements measures.txt \
  --out out
```

`measures.txt` 可以是带表头 `item,value,unit` 的表，也可以每行写 `名称,数值`。名称用 `m10`、`l5`、`fatigue_effort`（做事费力）和 `fatigue_going`（提不起劲），也认 M10、L5、费力等写法；`skill.json` 列出全部名称和合理范围。M10 和 L5 用同一种活动量，单位列留空；L5 比 M10 大时不计算。疲劳题答「是」或「否」，也可以写 1 或 0。数值出了合理范围、单位不认识或不是数时不计算：报告写明原因，脚本退出码是 3。`out/result.json` 给出 `relative_amplitude` 和 `fatigue_score`。

引用 `out/report.md`，包括 `边界:` 那一行。

