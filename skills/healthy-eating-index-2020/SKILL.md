---
name: healthy-eating-index-2020
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes Healthy Eating Index-2020 total and component scores from a person's
  prepared dietary densities, fatty-acid ratio, and energy percentages. Use for HEI-2020, 健康饮食指数,
  饮食质量评分, or comparisons of recorded diets and user-supplied targets in people aged at least two
  years.
---

# HEI-2020 饮食质量评分

适用于至少2周岁、已有膳食分析数据的人。按 Shams-White 等（2023）图3计算13项分数及总分；评分标准与HEI-2015相同。不是HEI-Toddlers-2020、AHEI或中国健康膳食指数。

用户命令：

```bash
python3 scripts/personal_report.py --measurements diet.csv --age 40 --out out
```

`diet.csv` 用 `item,value,unit` 三列；模板见 [references/input-format.md](references/input-format.md)。用户应提供自己的膳食分析记录，不能用示例值代替缺失值。若只有照片、菜名或未分类的克重，先说明需要依据食物成分和当量资料整理，不能猜算。

食物密度输入采用相对于明确参考密度的无量纲比值（单位`1`），例如总水果密度除以`1 cup equivalent / 1000 kcal`。数值仍是原分析中每1000千卡的杯当量数；钠以`1 g / 1000 kcal`为参考。必须保留各项目的参考密度，不可把全天份数直接作为密度。脂肪酸输入是质量比；两项供能输入用`%`，也接受单位`1`的供能分数并乘100。不得把食物当量换成普通杯容量或重量盎司。

`--age`必填；低于2岁停止。`--sex`只接受为可选背景，不改变分数。脂肪酸比值分母为零不在本工具输入范围；停止并请核对原始记录。

用户已提供目标时加`--targets targets.csv`，使用同样列，可只填拟改变的项目。工具验证联合情景，并输出每个单项情景；单项情景若违反食物包含关系或供能约束则保持未计算。不得自行替用户设置目标。

输出 `out/report.md`、`out/result.json`、`out/levers.json`。后者包含当前值的分段斜率及目标分差，只描述数学变化，不代表真实食物替代或健康效益。缺项、单位错误、非数值、超范围或数据矛盾时退出3并写 `out/problems.json`，不输出评分。

运行无需联网。禁止向用户索要论文全文、图表、NHANES队列、SAS软件或NCI代码包。计算常数已经固定在 `scripts/presets.py`；来源核对见 [references/contract.md](references/contract.md) 和 [references/claims.md](references/claims.md)。

报告使用中文，开头包含论文卡片。保留这句边界，不开具饮食或用药处方：

> 边界: 本评分只描述所提供饮食记录与《美国居民膳食指南2020—2025》的符合程度，不代表营养是否充足、疾病风险或寿命；单次记录不能代表长期习惯，不适用于2岁以下儿童，也不能据此开始或停止用药。
