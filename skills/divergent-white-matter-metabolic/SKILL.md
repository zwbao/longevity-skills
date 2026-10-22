---
name: divergent-white-matter-metabolic
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. Use when the user mentions divergent white-matter metabolism, EWM,
  AWM, or this FDG signature of cognitive decline. Current medicines and checkup labs are context. The
  report does not say what to start or stop.
---

# 白质葡萄糖代谢的差值

你交预期白质和非典型白质的 SUVR。两个都有时，报告用前者减去后者。缺一个时，报告说明没有算出差值。差值不是认知诊断。这两个值要用论文自建的体素掩模从 FDG-PET 提取，论文没有给个人切点，所以这只是两数相减。

不要向用户要影像或 PDF。不要另造回归权重。现用药对不上时写「不能据此停」。体检不增删这两个区域。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --out out
```

方法说明见 [references/claims.md](references/claims.md) 和 [references/contract.md](references/contract.md)。

