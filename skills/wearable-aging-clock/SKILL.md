---
name: wearable-aging-clock
description: >-
  Tier B lookup (human): what the paper reports, or simple arithmetic on values you bring; not the
  paper's model run on one person. Subtracts chronological age from a PpgAge the user already has and
  places the gap beside the healthy-cohort mean absolute error from the Apple Heart and Movement Study
  analysis in Nature Communications 2025. The paper does not publish the model weights for computing
  PpgAge from wrist PPG, so the script does not compute the clock. Use when the user brings a PpgAge,
  chronological age, medicines, or checkup labs and asks about this wrist PPG aging clock. It does not
  turn an age gap into a reason to start or stop a medicine.
---

# 腕部脉搏波年龄差

用户交已经算好的脉搏波年龄和实足年龄，以及现用药和体检。不要向用户要 GEO、STRING 或 PDF。

公开论文和配套代码里没有波形的岭回归系数，所以不从脉搏波重算年龄。两者都有时做减法，并在这个年龄差旁边放上论文健康队列的平均绝对误差。现用药对不上时保留「不能据此停」。体检不增删方法算出的名单。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --medications meds.txt \
  --labs checkup.csv \
  --age 64 \
  --out out
```

`--measurements` 用 `item,value,unit` 三列，只有 `item,value` 两列也行。`ppgage` 是已经算好的脉搏波预测年龄（岁），也认 `PpgAge`、`脉搏波年龄`；`--age` 是实足年龄，也可以在表里写一行 `age`，两处都有时用 `--age`。`skill.json` 列出全部名字、单位和合理范围（脉搏波年龄 10–150 岁，实足年龄 18–110 岁）。缺一项、单位不能换算、数值不在合理范围或读不出来时不做减法：报告写明原因，脚本退出码 3。`out/result.json` 写出 `ppgage_gap`。方法说明见 [references/claims.md](references/claims.md)。
