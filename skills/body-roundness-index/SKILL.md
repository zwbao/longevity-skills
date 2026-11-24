---
name: body-roundness-index
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. 根据成人身高和腰围计算身体圆度指数 BRI
  与腰围椭圆偏心率，在用户询问身体圆度、腰围相对身高或腰围变化时使用。支持使用者自填腰围目标的数学情景比较，不提供体脂率、内脏脂肪或健康范围。
---

# 身体圆度指数 BRI

依据 Thomas 等，Obesity (Silver Spring, Md.)，2013，DOI：10.1002/oby.20408。

用户提供自己的身高与腰围 CSV，表头 `marker,value,unit`。两项均需齐全；支持 cm、m、mm、in，中文或英文名称由 skill.json 识别。不要索要论文、补充表、队列资料或公开计算器的输出。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

`--age` 和 `--sex` 可作为兼容的背景参数传入，几何公式不使用它们。研究来自成人；不要据此解读儿童、妊娠期体形。重复比较时保持腰围部位一致；论文中 NHANES 和 St. Luke’s 在髂嵴上缘测量，Kiel 使用下肋与髂嵴之间的方法。

只有用户自己提供腰围情景时才加 `--targets targets.csv`。目标表同样使用 `marker,value,unit`，只含腰围；身高保持固定。没有目标时仍生成当前腰围附近的数学敏感度，不主动生成减腰围目标。

输出：`out/report.md`、`out/result.json`、`out/levers.json`。单位、范围或缺项不合要求时退出 3，写 `out/problems.json` 与含论文卡片的中文报告，结果置空。告知用户要补测或纠正哪一项，不猜单位、不补零。

BRI 与偏心率无单位。BRI 较高表示相对身高更圆，不等于疾病或脂肪量。图 3 的 BRI 及图 S2 的偏心率已复现；未实现补充表 S1–S2 的脂肪回归及健康范围，原因见 references/contract.md。不得套用其他论文的 BRI 分档，也不得将原论文 BMI 分组内的 BRI 分布当作个人健康阈值。

每份报告保留论文卡片和以下原句：

> 边界: BRI 是身高与腰围构成的体形指标，不是体脂率、内脏脂肪量、疾病风险或寿命预测；不能据此判断健康与否、制定减重目标或开始、停止药物。
