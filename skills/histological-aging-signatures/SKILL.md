---
name: histological-aging-signatures
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. Subtracts chronological age from a tissue predicted age the user
  already has and prints the paper's per-tissue mean absolute errors beside it, for the histological
  tissue clocks of Nature Medicine 2026. The slide models are not run, so no age is computed from a
  slide and the difference is not the paper's clock. Use when the user brings a tissue predicted age
  and asks about these tissue clocks. Does not turn an age gap into advice to start or stop a
  medicine.
---

# 组织切片年龄差

用户交组织名称、已经算好的预测年龄和实足年龄，以及现用药和体检。不要向用户要 GEO、STRING 或 PDF。

配套源码里没有拟合好的切片权重，所以不从切片重算年龄。报告做预测年龄减实足年龄，并在这个差旁边放上全部组织的平均绝对误差。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

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

组织表用列 `tissue,predicted,age`。
