---
name: sleep-chart-biological-ageing
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. The Nature 2026 sleep chart relates self-reported sleep duration to
  biological age gaps from imaging, plasma proteomics and metabolomics models built in UK Biobank;
  those gaps cannot be computed for an individual here. The script only places supplied sleep hours in
  the paper's short (<6 h), normal (6–8 h) or long (>8 h) groups, which restates the input against the
  paper's exposure categories, not a score. Use when the user gives sleep hours and asks where they
  sit in this chart. The skill does not ask for the PDF or a cohort. It does not turn a short or long
  group into advice to start or stop a medicine.
---

# 睡眠时长分组

论文的结论建立在影像、蛋白组和代谢组算出的生物年龄差上，这里不算它们；脚本只把你的睡眠小时数放进论文的三组，不是评分。

用户交自己的睡眠小时数、现用药和体检。不要向用户要 GEO、STRING 或 PDF。

报告只把小时数放进短、正常或长。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --out out
```

`--measurements` 用 `item,value,unit` 三列；单位列空着时按小时读，只有 `item,value` 两列也行。睡眠小时数的名字是 `sleep_hours`，也认 `sleep`、`睡眠时长`、`睡眠小时数`、`总睡眠时长` 等，`skill.json` 列出全部名字、单位和范围。按分钟记的在单位列写 `min` 或 `分钟`，会换成小时。换成小时后不在 2–16 之间、单位不能换算或结果不是数时不分组：报告写明原因，脚本退出码 3。`out/result.json` 写出 `sleep_duration_bin`（短、正常或长；没有小时数时为空）。
