---
name: elastin-fragments-innate-aging
description: >-
  Tier B lookup (human, mouse): what the paper reports, or simple arithmetic on values you bring; not
  the paper's model run on one person. In Yi et al., Nature Aging 2025 the 1,500 pg/ml and 250–680
  pg/ml limits only pick two comparison groups out of a cohort (values between or below them belong to
  neither), and the main evidence is in mice; the paper defines no personal score, and the assay is a
  research ELISA. The script only says whether one supplied serum elastin-fragment concentration falls
  in the paper's high or normal comparison range, and checks a peptide against the published
  sequences. Use when the user mentions elastin fragments, the E-motif, or innate immune activation by
  matrix fragments. Medicines and checkup labs stay context. The report does not say what to start or
  stop.
---

# 弹性蛋白片段

论文的两个浓度区间只是队列里用来比较的两组人，中间和更低的人不属于任何一组；这不是个人风险分档，检测也是研究用的 ELISA。

你交血清弹性蛋白片段浓度（pg/ml），以及可选的肽序列、其他基质碎片、现用药、体检、年龄。不要向用户要 GEO、STRING、PDF 或补充表。

报告开头是论文卡片。浓度按正文的高组和正常组界值归类。透明质酸、纤连蛋白和胶原碎片没有界值列。年龄回归缺斜率和截距，不算。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --age 50 \
  --out out
```

`--measurements` 用 `name,value`。弹性蛋白片段用 `弹性蛋白片段` 或 `ELN`，单位 pg/ml。`--medications` 一行一个名字。`--labs` 是 `项目,结果,单位`。

方法说明见 [references/claims.md](references/claims.md) 和 [references/contract.md](references/contract.md)。
