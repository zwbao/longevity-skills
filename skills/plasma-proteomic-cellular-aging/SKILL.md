---
name: plasma-proteomic-cellular-aging
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. Applies the SomaScan cell-type clock coefficients that Ding and
  colleagues released with their Nature Medicine 2026 paper (cellage repository) to protein values the
  user supplies. The clocks expect protein levels z-scored against a whole cohort; neither the paper
  nor the repository gives reference means and standard deviations, so one person's own SomaScan file
  cannot be turned into valid inputs, and the paper prints no per-person example. Without
  cohort-standardized values the number is not the paper's cell-type age. Use when the user brings
  SomaScan protein z-scores, sex, medicines, or checkup labs and asks about these cellular aging
  clocks. It does not turn a predicted cell age into advice to start or stop a medicine.
---

# 细胞类型蛋白年龄

用户交 SomaScan 蛋白 z 分数、性别、现用药和体检。这些 z 分数必须是在一个队列里按每个蛋白标准化后的值；论文和代码都没给参考均值和标准差，一个人自己的原始数值做不出来，直接套用得到的不是论文的细胞类型年龄。不要向用户要 GEO、STRING 或 PDF。

报告列出对上足够实测蛋白的细胞类型和预测年龄。一个人的文件算不出年龄差。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --out out
```

`--measurements` 用两列 `item,value`。性别用 `sex`，女为 1，男为 0。蛋白列名用系数表里的 aptamer 编号。
