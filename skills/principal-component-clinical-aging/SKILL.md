---
name: principal-component-clinical-aging
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes LinAge, the linear clinical aging clock of Fong et al., Nature Aging
  2024, from routine blood tests, blood pressure, BMI and a short health questionnaire, with the
  sex-specific medians, MADs and weights of all 61 parameters released in Supplementary Table 7, and
  reproduces the authors' worked example and their per-subject LinAge values to 1e-9 years. Use when
  the user mentions LinAge, PCAge, the NHANES principal-component clinical clock, or asks for a
  clinical biological age from ordinary checkup labs. Missing items count as zero, as the paper does,
  and are listed. Medicines are not read. The report does not say what to start or stop.
---

# LinAge 临床衰老年龄

用户交常规化验（血常规、生化、血脂、铁代谢、叶酸、维生素 B12、C 反应蛋白、纤维蛋白原、糖化血红蛋白、NT-proBNP、尿白蛋白肌酐比）、血压、脉搏、BMI、可替宁（有就给）、22 项既往病史、两题自评健康和过去一年看医生的次数，再加年龄和性别。不要向用户要 NHANES、补充表或 PDF：61 个参数的中位数、MAD 和权重已经在 `scripts/presets.py`。

公式照论文补充材料：年龄差 = C1 + β0 × 实足年龄（月）+ Σ βi × (xi − 中位数i) / MADi，LinAge = 实足年龄 + 年龄差；男女各一套参数。C 反应蛋白和 NT-proBNP 取自然对数，可替宁按 10、100、200 ng/mL 分成 0–3 档，低密度脂蛋白按作者代码用 TC − TG/5 − HDL（mmol/L）。只在 40–84 岁算。

缺的化验项按论文的办法记为 0（标准化后），报告列出缺项和它们权重的绝对值之和；没回答的病史和问卷按「没有」计，和作者代码一样。一项化验都没有、缺年龄或性别、年龄不在 40–84 岁、单位不能换算、数值不在合理范围、病史写了 0 和 1 以外的数时，不算，脚本退出码 3，`out/problems.json` 写明原因。

单项权重是死亡风险模型里的统计贡献，有的方向和常识相反，不能当成改善目标；报告不给目标值。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" \
  --measurements measurements.csv \
  --age 60 \
  --sex 女 \
  --medications meds.txt \
  --labs checkup.csv \
  --out out
```

`measurements.csv` 用 `item,value,unit` 三列。名字可以用化验单上的中英文叫法（如 `总胆固醇`、`HDL-C`、`超敏C反应蛋白`、`ALT`），`skill.json` 列出全部名字、单位、换算和合理范围；病史一行一项，有写 1、没有写 0；看医生次数写在 `healthcare_visits_past_year`，或直接写 NHANES 的 `huq050` 编码。`out/result.json` 写出 `linage_years`、`linage_delta_years`、`missing_count`、`missing_weight_years` 和几个中间指数。

引用 `out/report.md`，包括 `边界:` 那一行。方法和复现见 [references/contract.md](references/contract.md)。
