# 产品合同

用户提供所选食物组（水果与蔬菜合计、水果、蔬菜）的长期平均日摄入克数，可选结局、分析类型，以及自己设定的目标摄入量。技能自带从 Aune 等 2017 年 IJE 论文补充表8–18提取的 651 行数值和45列表头/参照量，正常运行无需联网或用户寻找论文附件。报告只返回对应的观察性人群 RR、印出的95% CI及参照量，或相邻两行；不输出个人绝对风险、疾病诊断、寿命或饮食处方。

流水线已授权直接实施此合同。

## 可行性核查

已打开 PubMed 的出版类型（Meta-Analysis / Systematic Review）、PMC完整正文及 Europe PMC fullTextXML，已下载并打开全部两个补充文件：367页 Supplementary Materials PDF，以及 Supplementary Webappendix DOCX（MOOSE清单）。White Rose Research Online 的出版版补充PDF与Europe PMC补充PDF经 pdftotext -layout 提取后的文本逐字相同。文件级来源、校验和与查看内容见 sources.md。

查表需要的摄入点、RR、95% CI及参照摄入量均印在补充表8–18（PDF第158–168页）。不需要重拟合样条。论文描述了三个分位点的样条结点，但没有提供足以重建任意摄入量预测与其CI的全部回归系数和协方差；本合同只读已发表表格，所以不以推断、拟合或插值补足这些量。表13的合计摄入列没有任何RR，明确返回 not_published，不生成系数。

## 输入和输出

`intake_g_d`：g/d，常见别名见 skill.json；仅接受 g/d，精确因子1。份量并不通用，因此不接受份/天、杯/天或 kg 代替日摄入量。原文将一份按80 g处理用于荟萃分析，不把这个研究约定自动应用于用户的实际份量。0–3000 g/d 是本实现的宽松录入校验范围，不是论文切点，也不意味着该范围内均能查表。LOINC不适用于此处的自报摄入量，未填。

每次读取一个食物组和一个结局列，默认合计摄入/全因死亡。通过选项可分别读取全部45列，发病、死亡、合并分析不相互替代；水果或蔬菜的单独估计不相乘。

- exact：输入精确等于印出摄入点，原样返回RR和CI；参照行只印1.00，无CI，CI为null。
- bracket：在表范围内但无对应行，仅返回相邻两个摄入点及各自RR/CI。两点不是个人风险上下界，当前RR为null。
- outside_table：输入合理但超出所选列的范围，返回该列范围，RR为null，不截断、不外推。
- not_published：表13合计列为空，RR及参照量均为null。纸面上35.6后的横线不视为RR=1。

原表其他空白或横线不进入数值CSV，也不以别的列或疾病替代。`result.json` 所有数值、状态和上下邻行均在清单声明。

## 目标和敏感度

`--targets` 与当前测量使用同一食物组、结局和参照量。双方都 exact 时，输出目标行RR减当前行RR；它只是两个印出点的数值差，不是风险百分点或干预效果。任一方无精确值时差为null。未提供预测协方差，因此不计算差的CI。

每次写 `levers.json`（longevity-levers/1）。敏感度是两条印出行的 `(RR高-RR低)/(摄入高-摄入低)`：非精确点使用其相邻两行；精确点使用前后行，表端使用单侧邻行。它描述已舍入表格的割线斜率，**不是原样条曲线的导数，也不是插值预测**。超范围、原表空白时无敏感度。文件保留差分所用两行便于核对。

## 复现

先写 tests/test_manifest.py 的测试，再提取数据和编写实现。表18合计列：500 g/d对应0.73 (0.70–0.77)，800 g/d对应0.69 (0.66–0.73)，参照为0 g/d。表8合计摄入在500 g/d的三种结局分别为0.84 (0.81–0.86)、0.84 (0.81–0.87)、0.80 (0.75–0.85)，参照为35.6 g/d。期望值直接抄纸面；直接查表用精确匹配，不派生常数。另以表9–17各一行检查列映射，以各列不同下限、空白和尾行验证不会跨列填补。

## 边界

这是前瞻性人群研究的观察性关联查表，不是个人患病或死亡概率，也不能证明改变摄入量会带来相同变化；不能据此开始或停止用药。

研究以成人队列为主，混杂、摄入测量误差、地区差异和异质性限制解释。没有个人基线风险或统一预测时间，不能把RR当作未来若干年的概率。年龄、性别、疾病和现用药不改变查表值；技能不读临床信息来修正原表。

## 各列支持范围

以下范围是存在印出RR的首末摄入点（g/d），不是连续预测区间；中间仅支持相邻行展示。

| 补充表 | 食物组 | 结局 | 分析类型 | 首末印出摄入点 |
|---|---|---|---|---|
| 8 | combined | coronary_heart_disease | mixed | 35.6–900 |
| 8 | combined | coronary_heart_disease | incidence | 35.6–900 |
| 8 | combined | coronary_heart_disease | mortality | 35.6–850 |
| 9 | fruit | coronary_heart_disease | mixed | 0–800 |
| 9 | fruit | coronary_heart_disease | incidence | 0–700 |
| 9 | fruit | coronary_heart_disease | mortality | 5.7–800 |
| 9 | vegetables | coronary_heart_disease | mixed | 0–600 |
| 9 | vegetables | coronary_heart_disease | incidence | 0–550 |
| 9 | vegetables | coronary_heart_disease | mortality | 11.4–600 |
| 10 | combined | stroke | mixed | 34.3–900 |
| 10 | combined | stroke | incidence | 34.3–900 |
| 10 | combined | stroke | mortality | 35.6–850 |
| 11 | fruit | stroke | mixed | 0–800 |
| 11 | fruit | stroke | incidence | 0–700 |
| 11 | fruit | stroke | mortality | 5.7–800 |
| 11 | vegetables | stroke | mixed | 5.1–500 |
| 11 | vegetables | stroke | incidence | 5.1–500 |
| 11 | vegetables | stroke | mortality | 11.4–500 |
| 12 | combined | ischemic_stroke | mixed | 35.6–700 |
| 12 | fruit | ischemic_stroke | mixed | 5.1–400 |
| 12 | vegetables | ischemic_stroke | mixed | 5.1–500 |
| 13 | combined | hemorrhagic_stroke | mixed | 未印出 |
| 13 | fruit | hemorrhagic_stroke | mixed | 5.1–250 |
| 13 | vegetables | hemorrhagic_stroke | mixed | 5.1–400 |
| 14 | combined | cardiovascular_disease | mixed | 35.6–900 |
| 14 | combined | cardiovascular_disease | incidence | 86.8–900 |
| 14 | combined | cardiovascular_disease | mortality | 35.6–850 |
| 15 | fruit | cardiovascular_disease | mixed | 0–800 |
| 15 | fruit | cardiovascular_disease | incidence | 32.8–600 |
| 15 | fruit | cardiovascular_disease | mortality | 0–800 |
| 15 | vegetables | cardiovascular_disease | mixed | 13.7–600 |
| 15 | vegetables | cardiovascular_disease | incidence | 51.6–500 |
| 15 | vegetables | cardiovascular_disease | mortality | 13.7–600 |
| 16 | combined | total_cancer | mixed | 40–900 |
| 16 | combined | total_cancer | incidence | 50–900 |
| 16 | combined | total_cancer | mortality | 40–900 |
| 17 | fruit | total_cancer | mixed | 5.7–650 |
| 17 | fruit | total_cancer | incidence | 24.5–650 |
| 17 | fruit | total_cancer | mortality | 5.7–600 |
| 17 | vegetables | total_cancer | mixed | 20–650 |
| 17 | vegetables | total_cancer | incidence | 27.8–650 |
| 17 | vegetables | total_cancer | mortality | 20–600 |
| 18 | combined | all_cause_mortality | mortality | 0–830 |
| 18 | fruit | all_cause_mortality | mortality | 0–600 |
| 18 | vegetables | all_cause_mortality | mortality | 0–600 |
