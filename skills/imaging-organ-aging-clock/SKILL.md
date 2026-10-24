---
name: imaging-organ-aging-clock
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. The organ ages of the npj Digital Medicine 2026 imaging clock come
  from LASSO models on 1,777 UK Biobank imaging-derived phenotypes across seven organs, which a person
  cannot obtain, so the script cannot compute them. It only subtracts chronological age from organ
  predicted ages the user already has, and lists the plasma proteins named in the main text. Use when
  the user mentions imaging organ age, MRI organ clocks, or this UK Biobank imaging study. Current
  medicines and checkup labs do not edit the protein list or the gaps.
---

# 影像器官年龄差

器官预测年龄要用英国生物银行的 1777 项影像指标和论文的 LASSO 模型算，这里不算它；脚本只把你已经拿到的预测年龄减去实足年龄。

用户提供实足年龄、各器官已经算好的预测年龄、用药和体检。不要向用户要 UK Biobank、影像表型、GEO、STRING 或 PDF。

七个器官没齐就不报平均年龄差。蛋白名单不随体检改变。药名对不上时保留「不能据此停」。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" \
  --medications meds.txt \
  --labs checkup.csv \
  --age 60 \
  --measurements organs.tsv \
  --out out
```

`organs.tsv` 每行是 `brain 70` 这种器官和预测年龄。可用 brain、heart、body、kidney、liver、pancreas、eye，以及 brain_gm、brain_wm。引用 `out/report.md`，包括 `边界:` 那一行。
