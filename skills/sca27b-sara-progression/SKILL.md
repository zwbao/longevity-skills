---
name: sca27b-sara-progression
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Adds up one person's eight SARA ataxia item scores (rated by a neurologist) and
  places them against the printed results of Traschütz et al. (eBioMedicine 2026; 219 patients with
  SCA27B, the FGF14 GAA repeat-expansion late-onset ataxia, and 390 healthy controls): age-decade
  patient medians and healthy 90th percentiles, the cohort progression rate (overall or ambulatory),
  and, from Supplementary Tables S4-S5, the model difference in yearly progression for the person's
  shorter-allele GAA repeat count versus the cohort median of 16. Use for SCA27B, GAA-FGF14, FGF14,
  SARA 评分, 共济失调进展, 小脑共济失调, 较短等位重复数. States that these are cohort averages and contrasts, not a
  personal disease forecast.
---

# SCA27B：SARA 评分与队列进展对照

用户交医生按标准查体打的 SARA 八项分数，可选基因报告上 FGF14 两个等位的 GAA 重复数，以及评分时年龄。不要向用户要论文、补充表或 PDF，用到的数已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements sara.csv --age 66 --out out
```

`sara.csv` 的列是 `item,value,unit`：

- 八项必填（单位可空）：步态 0–8、站姿 0–6、坐姿 0–4、言语 0–6、手指追踪 0–4、指鼻试验 0–4、快速轮替动作 0–4、跟膝胫试验 0–4。英文名 gait、stance、sitting、speech、finger chase、nose-finger、diadochokinesia、heel-shin 也认。
- 可选：较长等位、较短等位的 GAA 重复个数（不是碱基对数）。给了较短等位才算重复数那一节。
- `--age` 可选：给了才做同年龄段对照；健康对照第 90 百分位只印到 50–80 岁。

报告给出 SARA 总分、是否属于步态 ≤3 的独立行走亚组和该组的队列平均进展（0.40 或全队列 0.54 分/年）、同年龄段患者中位数和健康对照第 90 百分位，以及较短等位重复数相对 16 个重复的模型进展差（总分和八项各自）。论文按 >180、≥250 切点另建的模型照原样列出，不和连续模型相加。

任何一项缺失、超出该项满分、单位不对或年龄不合理时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `sara_total_score`、`ambulatory_subgroup`、`cohort_progression_points_per_year`、`control_p90_for_age_decade`、`margin_over_control_p90`、`short_allele_group`、`short_allele_progression_difference`。

## 不能算的

- 个人绝对进展速度：补充表 S4 的协变量中心化常数没有印出，只能给相对 16 个重复的差值。
- 起病年龄：较长等位与起病年龄的回归没有印出截距。
- 50 岁以下、80 岁以上的健康对照第 90 百分位：正文没有印出。

## 报告里必须保留的话

- 这些是 SCA27B 患者队列的平均进展和模型差值，不是个人病程预测，也不是诊断。
- SARA 必须由受过训练的医生评分；其他疾病、跌倒或手术后状态也会抬高分数。
- 不给任何药物或剂量建议；治疗的开始、调整或停止交给神经科医生。

引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
