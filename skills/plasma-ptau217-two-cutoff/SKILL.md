---
name: plasma-ptau217-two-cutoff
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Classifies one plasma pTau217 result measured with the Simoa ALZpath assay as
  negative, indeterminate (grey zone) or positive using the single and two-cut-off thresholds printed
  by Martino-Adami et al. (Nat Commun 2026) for South American memory-clinic cohorts (default:
  Cog-Aging-Study-Brazil, posterior threshold 0.85, <=0.50 / >=0.79 pg/mL), and the pTau217/Abeta42
  ratio when a Simoa plasma Abeta42 is given. Use for 阿尔茨海默病血液检测, 血浆 pTau217, p-tau217, 磷酸化tau217,
  pTau217/Aβ42, 淀粉样蛋白血检, 灰区. Not a diagnosis; refuses other assays (Lumipulse, Elecsys, mass
  spectrometry).
---

# 血浆 pTau217 阳性 / 灰区 / 阴性

用户交一次血浆 pTau217 化验（Simoa 平台 ALZpath 试剂），可选同一次的血浆 Aβ42（Simoa Neurology 4-plex E）。不要向用户要论文、补充表或 PDF，切点已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements labs.csv --assay simoa-alzpath --out out
```

`labs.csv` 的列是 `item,value,unit`：

- 血浆pTau217（必填）：pg/mL（ng/L 相同）。也认 pTau217、p-tau217、磷酸化tau217。
- 血浆Aβ42（可选）：pg/mL。有它时再算 pTau217/Aβ42 比值并分档。

参数：

- `--assay`（必填）：只能是 `simoa-alzpath`（也认 `simoa`、`alzpath`）。化验单上看不出检测方法时，先问用户或检测机构，不要猜。别的方法（Lumipulse、Elecsys、质谱）数值尺度不同，脚本会拒绝。
- `--cohort`：`brazil`（默认，唯一有脑脊液验证的队列）或 `argentina`。
- `--probability`：`0.80`、`0.85`（默认，论文里表现最好）或 `0.90`。灰区越宽，两端分档越可靠，落在灰区的人越多。

单位不对、超出范围、缺 pTau217 或检测方法不对时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `ptau217_two_cutoff_category`、`ptau217_single_cutoff_status`、`ptau217_abnormal_class_probability`、`ptau217_abeta42_ratio`、`ratio_two_cutoff_category`、`ratio_single_cutoff_status`、`ashton_two_cutoff_category` 和 `cutoff_set`。

## 报告会说什么

- 两切点分档（主读法）、单切点分档，以及论文表 2 引用的 Ashton 等（2024）切点作对照。
- 阴性：直接说是好消息，但不排除以后变化或其他原因。阳性：请到神经内科或记忆门诊，由医生结合认知评估判断。灰区：由医生决定是否做脑脊液、PET 或复查。
- 离切点不到 0.02 pg/mL 时提醒复查可能落到另一侧。
- 混合模型的后验概率不是患病概率，报告这样写明。
- 论文队列的阳性/阴性预测值只放在“说明”里，标明是队列数字。

## 不做的事

- 不诊断阿尔茨海默病，不算患病概率，不看趋势。
- 不套用到其他检测方法或脑脊液结果。
- 不给药量，不说开始或停止任何药。

引用 `out/report.md`，包括 `边界:` 那一行。切点来源和复现见 [references/contract.md](references/contract.md)。
