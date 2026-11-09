---
name: bia-acc-osteosarcopenic-adiposity
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Reads the bone T-score, skeletal-muscle S-score and body-fat percentage from one
  person's BIA-ACC bioimpedance report and applies the operational cut-offs printed by Ilich et al.
  (GeroScience 2026): T < -1.0 reduced bone mass (T <= -2.5 marked), S <= -1.0 reduced muscle mass,
  fat >= 25% (men) or >= 32% (women) adiposity, and all three together as the BIA-ACC osteosarcopenic
  adiposity (OSA) phenotype. Use for 骨肌减少性肥胖, 骨质疏松性肌少性肥胖, osteosarcopenic obesity, BIA-ACC 体成分报告,
  骨量肌量体脂一起看. Does not recompute the proprietary device scores and does not accept DXA T-scores.
---

# 骨-肌-脂综合表型（BIA-ACC 骨肌减少性肥胖）

用户交自己 BIA-ACC（BioTekna）体成分报告上的三个数和性别，年龄可选。不要向用户要论文、DXA 报告或原始阻抗数据；切点已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements bia.csv --sex female --age 52 --out out
```

`bia.csv` 的列是 `item,value,unit`：

- BIA-ACC 骨量 T 值（必填，无单位）
- BIA-ACC 肌量 S 值（必填，无单位）
- 体脂率（必填，%，写 28.5 而不是 0.285）

名称也认 `BIA-ACC T-score`、`S-score`、`FM%`、`脂肪率` 等，`skill.json` 列出全部。普通「骨密度 T 值」不会被认作 BIA-ACC T 值：DXA 的 T 值和 BIA-ACC 的不可互换。

缺项、单位不对、超出范围、缺性别时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `bone_category`、`reduced_bone_mass`、`reduced_muscle_mass`、`adiposity`、`components_met` 和 `osa_phenotype`。

## 报告里必须保留的话

- 这是按论文切点对 BIA-ACC 报告的操作性分档，不是骨质疏松、肌少症或肥胖的临床诊断。
- T、S 值由厂商专有算法算出，本技能不重算；其他设备或 DXA 的读数不能代替。
- 研究对象是 20–90 岁意大利白人成人，横断面研究；年龄拐点是人群曲线，不是对个人的预测。

引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
