---
name: phenotypic-age
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Calculates clinical Phenotypic Age from chronological age and nine blood biomarkers
  using the published correction to Liu et al. (PLoS Medicine, 2018). Use for 表型年龄、PhenoAge、九项血检年龄 or
  a user-supplied laboratory target scenario. Reports the simple age difference, not PhenoAgeAccel.
---

# 表型年龄

接收 20–84 岁成年人的实足年龄及同一次空腹至少 8 小时采血的九项血检。
论文：Liu 等，PLoS Medicine，2018，doi:10.1371/journal.pmed.1002718；
计算使用 2019 年正式更正 doi:10.1371/journal.pmed.1002760。

用户命令：

> 用我的年龄和九项血检算表型年龄；如果我提供目标值，也比较达到目标后的模型变化。

将化验整理为 CSV 或 TSV，表头 `marker,value,unit`，再运行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 40 --out out
```

可选 `--targets targets.csv`，同样表头，只列用户自己提供的血检目标。
`--sex` 可接受上下文，不进入公式。不要替用户设目标，不允许以年龄作为改善目标。

九项是白蛋白、肌酐、空腹血糖、CRP、淋巴细胞百分比、平均红细胞体积、
RDW-CV、碱性磷酸酶和白细胞计数。别名、单位、换算和宽范围检查见 `skill.json`。
CRP 交原始浓度，脚本只取一次自然对数；不能交 log(CRP)，也不能用 log(1+CRP)。
CRP 为零、低于检出限等不等式结果不能代入或自行替换。
RDW-SD（fL）不能代替 RDW-CV（%），淋巴细胞绝对计数不能代替百分比。
所有按中文或英文别名输入的血检均须注明单位；带单位的规范键可省单位列的值。

输出 `out/report.md`、`out/result.json`、`out/levers.json`。
缺项、单位错误、超范围、无法读数或目标错误时退出码为 3，写 `out/problems.json`，
数值输出为 null，不产生 levers；告诉用户具体缺哪项，不能以均值或零补齐。
不支持直接解析 PDF、图片；由助手先提取表格并核对单位。

报告先放论文卡片，再放个人结果与本次输入。始终标注“仍在验证”：没有找到
论文印出的完整个人算例，测试通过不代表已经复现论文示例。
年龄差只表示相减；PhenoAgeAccel 是相对参考人群年龄回归的残差，不能混称。
不提供死亡风险分层、五分位、疾病判断、寿命预测或用药建议。
模型敏感度和目标变化不是因果效应，不能把降低任一血检数值等同于健康获益。

不要向用户索要 NHANES 数据、回归系数、补充表或代码仓库。常数已在
`scripts/presets.py` 中冻结；来源、单位冲突及验证缺口见
`references/contract.md`、`references/claims.md` 和 `references/sources.md`。

每份报告必须原样保留：

> 边界: 这是观察性人群模型的表型年龄估计，不能诊断疾病、预测个人寿命或证明干预能逆转衰老，不能据此开始或停止用药。
