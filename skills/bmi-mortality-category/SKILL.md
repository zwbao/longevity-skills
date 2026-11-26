---
name: bmi-mortality-category
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes BMI from a person's height and weight and returns the published
  nine-category all-cause mortality association for never-smokers without relevant pre-existing
  chronic disease. Use when an adult asks how their BMI relates to mortality or wants to compare a
  specified target weight with the published category table. Reports pooled hazard ratios and floating
  confidence intervals, not individual death probabilities or life expectancy.
---

# BMI 分档与全因死亡关联

读取身高体重，按 Global BMI Mortality Collaboration（Lancet，2016）正文表 2 查九档 HR。不混用表 1 的六档结果，不把中国肥胖诊断阈值代入论文。

用户命令：

> 用我的身高体重查看 BMI 对应的死亡关联，并比较我指定的目标体重。

## 需要的个人信息

- 同次测量的身高、体重及单位；CSV 表头为 `marker,value,unit`。
- 测量时年龄：`--age`，仅 20 至未满 90 岁。
- 吸烟史：`--smoking never|former|current|unknown`，必须明确为 never；戒烟不等于从不吸烟。
- 相关既往慢病：`--chronic-disease no|yes|unknown`，必须明确为 no。按附录分析计划，包括心血管病（心梗、卒中、冠脉搭桥或成形术、外周动脉病、心衰等）、癌症（非黑色素瘤皮肤癌除外）、慢性呼吸系统病（如 COPD）、神经退行性病（帕金森病、阿尔茨海默病等）。研究各队列记录并不完整，本工具采用保守的统一筛查；不把单独糖尿病或高血压自动当成以上排除项。
- `--sex` 可选，只作上下文；该实现查询男女合并结果，不据性别重新计算。

不默认用户满足人群条件。不向用户索取全文、补充表、队列数据或代码；查表数字已冻结在 `scripts/presets.py`，运行不联网。

## 执行

`python3 scripts/personal_report.py --measurements measurements.csv --age 50 --smoking never --chronic-disease no --out out`

需要比较用户自定目标体重时追加 `--targets targets.csv`，列同测量表，只接受体重；身高固定。未指定目标时仍输出当前值下敏感度。BMI 档内 HR 为常数、切点处导数不存在，不能把这一特性解释为减重无效或突然有效。

输出 `out/report.md`、`out/result.json` 和 `out/levers.json`。缺项、错误单位、超范围、未知项目或不满足人群条件时退出 3，写 `out/problems.json` 和带论文卡片的错误报告；结果数值为空，不生成情景结果。

## 报告含义与边界

先展示论文卡片，再展示个人 BMI、对应区间、该档人群 HR 和 95% 浮动方差置信区间。参照为 BMI 22.5–<25.0 kg/m²，使用未舍入 BMI 判档。有效范围为 15≤BMI<60，拒绝外推。

这只复现表 2 查表，不复现原始 Cox 回归或荟萃分析。原研究排除随访最初 5 年，不能把这一条件说成已确认用户未来存活。HR 不是概率；区间不是个人预测区间；目标表值之差不是干预获益。不给药物剂量或启停药建议。

每份报告必须保留：

> 边界: 本报告只按 BMI 查询论文特定人群的死亡危险比（HR），不是个人死亡概率、预期寿命或体重改变的因果效果；不能据此开始、停用或调整药物。

核对范围、输入工程限制及原文差异见 [contract.md](references/contract.md)，来源与研究设计见 [claims.md](references/claims.md)。
