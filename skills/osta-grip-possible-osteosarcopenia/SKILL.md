---
name: osta-grip-possible-osteosarcopenia
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Classifies one person as possible osteoporosis, possible sarcopenia and possible
  osteosarcopenia from body weight, age, sex and handgrip strength, using the OSTA index (0.2 x
  [weight - age], at or below -1) and the AWGS 2019 grip cut points (men under 28 kg, women under 18
  kg) as printed by Koh et al. (J Gerontol A 2026, TARGET cohort, Singapore, adults aged 60 and over).
  Adds the paper's cohort associations with intrinsic capacity and 6-month mini-MoCA as population
  context. Use for 骨肌减少症, 骨质疏松自评, OSTA, 握力, 肌少症筛查, 骨密度风险, 老人认知. States that this is a screening class,
  not a diagnosis, and does not predict the person's cognition.
---

# 可能骨肌减少症筛查（OSTA 加握力）

用户交体重、握力（优势手两次平均），以及年龄和性别。不要向用户要论文、PDF 或补充材料，公式和切点已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements body.csv --age 78 --sex 女 --out out
```

`body.csv` 的列是 `item,value,unit`：

- 体重（必填）：kg，也接受 lb、g。按名称（体重、weight）给时必须写单位，因为磅数也落在合理范围里；用“斤”记的先除以 2。
- 握力（必填）：kg，也接受 lb。论文做法是每只手量两次，取优势手两次的平均。按名称给时必须写单位。
- 行名用键名 `weight_kg`、`grip_strength_kg` 时单位可以空着，按 kg 读。

`--age` 和 `--sex` 都必填：年龄进 OSTA 公式，性别决定握力切点。

报告给出 OSTA 指数和分档（高 < −4、中 −4 到 −1、低 > −1），可能骨质疏松（OSTA ≤ −1）、可能肌少症、可能骨肌减少症（两项都符合）各是或否；再列出论文人群里可能骨肌减少症与内在能力、6 个月简版 MoCA 的关联和筛查表现，明确写成人群结果。

缺体重、握力、年龄或性别，单位缺失或不认识，数值超出范围（体重 25–250 kg、握力 1–100 kg）时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `osta_index`、`osta_risk_category`、`possible_osteoporosis`、`possible_sarcopenia` 和 `possible_osteosarcopenia`。

## 报告里必须保留的话

- 这是筛查分类，不是诊断；论文里筛查阳性的人约一半被 DXA 确认。
- 论文的认知关联是新加坡 60 岁及以上老人的人群平均差异，不是这个人的认知预测；只符合一项的人，论文没有发现关联。
- 不给药物或剂量建议；要确认请医生做骨密度（DXA）和肌少症评估。

验证状态是草稿：论文没有印出个人算例，测试只核对公式和切点。引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
