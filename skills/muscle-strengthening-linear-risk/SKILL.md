---
name: muscle-strengthening-linear-risk
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Converts weekly muscle-strengthening exercise duration into the population
  relative-risk associations of the published linear dose-response model. Use for a person's weekly
  strength-training minutes or a user-specified duration comparison. Reports all-cause mortality, CVD,
  total cancer and diabetes with model confidence intervals, while retaining the limitations of the
  paper's nonlinear findings.
---

# 每周力量训练时长的线性关联换算

用户提供自己的每周力量/抗阻/自重训练总时长和实足年龄。技能按 Momma 等，British Journal of Sports Medicine，2022 的表 1 线性列换算群体关联。不要把它用作运动处方或个人疾病风险预测。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 50 --out out
```

CSV 表头为 `marker,value,unit`；项目可用 `每周力量训练总时长` 或 `strength_minutes_per_week`。单位用 `min`（一周总分钟数）或 `h`（一周总小时数，精确乘 60）。不是单次训练分钟数、训练频次或有氧运动总时长；不把重体力家务算作本文训练暴露。

可选 `--targets targets.csv` 使用相同表头，填用户自己指定的目标周时长。它仅生成情景比较，不自动选择、排序或推荐训练目标。`--sex` 为可选上下文，不改变模型。年龄仅用于成年人适用范围检查。

缺项、非数值、单位不支持或超范围时退出 3，读取 `out/problems.json` 告诉用户缺少或填错的项目；不要用零替代缺失。不要让用户找论文、补充表、队列数据或代码：需要的表 1 常数已在 `scripts/presets.py` 中。

成功时读取 `out/report.md`、`out/result.json`、`out/levers.json`。论文卡片在报告开头；输出键中的 `linear` 必须保留。报告与任何图示均须标注“线性模型群体关联”，同时保留 J 形/L 形非线性结果的限制。不得用线性下降走势推断增加训练一定更好，不得将本结果当作图 4 非线性曲线或据此寻找最佳时长。

边界：这是观察性队列荟萃分析的线性关联换算，不是个人患病或死亡概率、寿命预测或改变训练时长后的因果收益；不能据此开始或停止药物，也不提供用药剂量或训练处方。

材料清单、公式和验证范围见 [references/contract.md](references/contract.md)，研究设计与样本见 [references/claims.md](references/claims.md)。
