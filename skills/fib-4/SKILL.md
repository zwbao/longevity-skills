---
name: fib-4
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the original FIB-4 liver fibrosis index from age, AST, ALT and
  platelet count, and locates the result against the HIV/HCV-coinfection study's published cutoffs.
  Use for FIB-4、肝纤维化指数、肝酶和血小板联合解读。 Keeps the original population limits and distinguishes the two
  histological endpoints without predicting individual disease probabilities or lifespan.
---

# FIB-4 肝纤维化指数

从本技能目录运行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 45 --out out
```

读取 `item,value,unit` 三列表格中的 AST、ALT、血小板计数，以及采血时年龄。
使用同次采血的结果。性别不进入原公式，不需要提供。接受 CSV 或 TSV；化验单为图片或 PDF 时先确认项目、数值和单位，再整理为表格，不能猜数或补零。

标准单位、中文和英文别名、准确换算系数及录入范围见 `skill.json`。常见单位转换由 `skillkit` 处理；酶活性和血小板以别名提交时必须注明单位。使用带单位的规范键名且不填单位时按键名单位读取。录入范围不是临床正常范围。

原研究为 Sterling 等，Hepatology，2006，APRICOT 试验资料的回顾性二次分析，主要为基线横断面分期。对象为大于 18 岁的 HIV/HCV 共感染、ALT 升高且肝病代偿者。未确认这些条件时，只能描述“原研究切点位置”；不能把它当作一般体检人群的已验证诊断规则。

输出 `out/report.md` 和 `out/result.json`：FIB-4 指数、表 5A 进展期纤维化切点位置，以及分开列出的表 5B 中度或进展期纤维化切点位置。报告先放论文卡片；人群诊断性能不写成个人患病概率。切点等号按表格，差异和两个原文算例见 [合同](references/contract.md)。

缺项、读不出数、错单位、超录入范围或文件无法读取时，退出码为 3，生成 `out/problems.json` 和中文问题报告，移除旧 `result.json`。助手按问题清单请用户补齐或核实自己的指标。不能要求用户查找全文、补充表、原始队列、GitHub 文件；全部运行参数已包含在技能内，运行时无需联网。

这是现患纤维化的辅助指数，不是可据以设定健康干预目标的风险方程；不提供 `--targets` 或 `levers.json`。ALT 在分母中，单独升高 ALT 也会让指数下降，不能解读为健康改善。没有三分类概率模型的完整参数，不拟合图线，不给出任意个人的 Ishak 分期概率。

每份报告必须原样保留：

> 边界: 本报告只按 Sterling 等（2006）的 FIB-4 公式计算指数并对照原研究切点；原研究对象为 HIV/HCV 共感染、ALT 升高且肝病代偿的成人，不能直接外推到一般体检人群。结果不是纤维化确诊、个人患病概率、生物年龄或寿命预测，不能据此自行决定是否需要肝活检，也不能据此开始或停止药物。

材料核查、样本及利益冲突见 [claims.md](references/claims.md)。
