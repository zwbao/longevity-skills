# SKILLCOURT 跌倒史切点：合同、数值来源与核对

## 产品合同

1. 用户提供自己在 SKILLCOURT 上测得的随机星形跑完成时间、简单踏步反应时间、选择踏步反应时间中的至少一项（秒），年龄可选。
2. 技能自带论文正文印出的三个探索性切点和对应的 AUC、灵敏度、特异度，不向用户要论文、PDF 或补充表。
3. 报告只说每项成绩落在切点哪一侧，并给出该切点在论文人群里的判别表现。不能算：调整年龄和中心后的个人预测概率（正文没有印出截距、系数和 z 标准化用的均值和标准差；表 5–7 的单元格本次只拿到登录跳转、没有读到，不能断定表里没有）；将来跌倒的概率（研究是横断面、跌倒史是回顾性的）。

## 来源

| 代号 | 出处 | 用到什么 |
| --- | --- | --- |
| [P] | Giesche F 等. Reactive agility and motor-cognitive assessments for distinguishing community-dwelling older adults with and without a history of falls: a dual-centre cross-sectional study. GeroScience 2026. doi:10.1007/s11357-026-02477-4 | 正文 Methods（SKILLCOURT 流程、入选年龄 ≥60 岁）、Results “Discrimination analyses”（切点、AUC、灵敏度、特异度、比值比） |
| ESM 1 | 11357_2026_2477_MOESM1_ESM.docx | 表 S1–S5 只用于核对分中心成绩范围，用于设定输入合理范围 |

## 切点（照原文）

- “For clinical interpretability, an exploratory cutoff of 28.6 s was derived from the unadjusted Random Star Run analysis (Table 4), which yielded an AUC value of 0.66, with 55% sensitivity and 76% specificity.”
- “For comparison, the unadjusted ROC analyses based on the original SKILLCOURT reaction times yielded AUC values of 0.63 and 0.61 for the simple and choice reaction tasks, respectively, with exploratory cutoff values of 0.62 and 0.88 s.”
- 方向：“longer completion times were associated with higher odds of having a history of falls”；反应任务同样是慢者比值比高（OR 1.58、1.42）。

## 操作定义（论文没写死的地方）

- 等于切点算哪一侧：论文没写。本技能把等于切点的值归入“达到或超过切点”一侧，报告里用同一说法。
- 输入范围：随机星形跑 10–150 秒（ESM 1 表 S4 两中心均值约 31–33 秒、标准差约 7–8 秒，范围留宽）；踏步反应 0.2–3 秒（表 S4 均值 0.64–0.87 秒）。把毫秒当秒写（如 620）会超出范围被拦下。
- 三个切点分别对照、分别报告，不合成一个总判断；`tests_at_or_above_cutoff` 只是计数，不是论文的评分。

## 核对

论文没有印出某个人成绩对应结果的算例，所以没有可复现的个人示例；`validation` 保持 `draft`。测试核对：切点和 AUC/灵敏度/特异度与正文印出的一致；切点边界（等于切点归入达到或超过一侧）；毫秒换算；毫秒当秒、单位错、一项都没有时退出码 3。
