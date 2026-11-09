---
name: handgrip-low-strength-mortality
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Checks one person's own handgrip strength (dominant hand, best of two trials) against
  the EWGSOP2 (men < 27 kg, women < 16 kg) and FNIH (men < 26 kg, women < 16 kg) low-strength cut-offs
  and reports the all-cause mortality hazard ratio printed for that group versus people at or above
  the cut-off in Pérez-Sousa et al. (GeroScience 2026, Mexican Health and Aging Study, adults 50 and
  over, Supplementary Table S3); with height it also gives allometric grip (kg/m²). Use for 握力, 握力低,
  握力计, 肌少症筛查, 肌力, 死亡风险, handgrip strength. States that the hazard ratios are population associations,
  not a personal death probability, and does not diagnose sarcopenia.
---

# 握力切点与全因死亡风险比（墨西哥 MHAS 队列）

用户交自己测的握力和性别，身高和年龄可选。不要向用户要论文或 PDF，切点和风险比已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements grip.csv --sex male --age 68 --out out
```

`grip.csv` 的列是 `item,value,unit`：

- 握力（必填）：优势手两次中的最大值，kg，也接受 lb。必须写单位（磅数也常落在合理范围内）。
- 身高（可选）：cm，也接受 m、mm、in。只用来算身高校正握力。
- 名称也认 grip、handgrip strength、HGS、手握力 等，`skill.json` 列出全部。

报告给出按 EWGSOP2 和 FNIH 切点的分档，低于切点时给出论文补充表 S3 该性别低握力组相对达到切点者的全因死亡风险比（模型 2 完全调整为主，同时列模型 1），以及身高校正握力（握力 ÷ 身高²）。

缺握力或性别、握力没写单位、单位不认识、数值超出范围时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `ewgsop2_category`、`ewgsop2_mortality_hr`、`fnih_category`、`fnih_mortality_hr` 和 `allometric_hgs_kg_m2`。

## 报告里必须保留的话

- 风险比是论文人群（墨西哥 50 岁及以上成人，随访中位约 9 年）里低握力组相对达到切点者的关联，不是个人死亡概率或预期寿命，也不能说明因果。
- 女性低于 16 kg 在完全调整后置信区间跨过 1，论文认为女性结论不确定。
- 这些切点是肌少症共识里“肌力低”的定义，不是在这个队列里推导出的死亡阈值；不写诊断。握力偏低时建议请医生评估。

验证状态是草稿：论文没有印出个人算例，测试只核对分档查表。正文表 1–3 的四分位界值没能打开，所以不按四分位分组。引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
