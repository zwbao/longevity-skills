---
name: cd38-recent-thymic-emigrants
description: >-
  Tier B lookup (human): what the paper reports about named entities, not a validated personal score.
  Bohacova et al., Immunity 2024 is a single-cell and spectral cytometry study; its gates work on
  transformed fluorescence intensities from the authors' own panel and instrument, which a person
  cannot get from a clinical lab, and no personal score is defined. The script only gates supplied
  transformed CXCR3, CD38 and CD25 values of naive CD4 and CD8 T cells with the thresholds in the
  method repository, and places a supplied age in the paper's age groups. Use when the user mentions
  CD38 recent thymic emigrants, naive T-cell aging, or this Immunity paper. Medicines and checkup labs
  do not change the gate list. The report does not say what to start or stop.
---

# 初始细胞分档

这是研究数据的门控，不是个人化验评分：阈值是原实验仪器和数据转换下的数，换一家实验室的流式结果不能直接套用。

用户交现用药、体检、年龄，以及转换后的标志物表达。不要向用户要 GEO、STRING 或 PDF。

有标志物时按门控分档。没有标志物也没有年龄时名单是空的。药名对不上时保留「不能据此停」。体检不增删方法算出的名单。

## Command

```bash
python "$SKILL/scripts/personal_report.py" \
  --medications meds.txt \
  --labs checkup.csv \
  --markers markers.csv \
  --age 70 \
  --out out/
```

`markers.csv` 列：`lineage,cxcr3,cd38,cd25`。`lineage` 为 CD4 或 CD8。

把 `out/report.md` 整段交给用户，包括最后一行 `边界:`。
