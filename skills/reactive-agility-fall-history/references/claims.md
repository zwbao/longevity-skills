# 论文、补充材料、代码、同名的另一个东西

- 研究设计：双中心横断面观察研究（跌倒史回顾性自报，过去 12 个月）；PubMed 出版类型 Journal Article（PMID 42678611）。注册号 DRKS00034524（2024 年 7 月 8 日，回顾性注册）。
- 全部样本组：招募 258 人（中心 1 德国法兰克福 Goethe 大学 80 人，中心 2 卢森堡 LUNEX 178 人），纳入 231 人（中心 1 67 人，其中 23 人有跌倒史；中心 2 164 人，其中 80 人有跌倒史），合计 103 人有、128 人没有跌倒史，平均 71.9 ± 7.5 岁。随机星形跑和简单反应的判别分析样本 172 人（80 有、92 无）；选择反应 171 人（80 有、91 无）。没有独立验证队列，只做了 1000 次 bootstrap 内部验证。
- 物种：人（Homo sapiens）。
- 利益冲突：论文 Competing interest 写明 “TH provides scientific consulting services to SKILLCOURT GmbH. The company had no influence on the study design, data analysis, interpretation of the results, or the decision to submit the manuscript for publication.” 资助：卢森堡中心由 Oeuvre Nationale de Secours Grande-Duchesse Charlotte（2022AID220）资助，德国中心无外部资助。

| | 内容 |
| --- | --- |
| 论文声称 | 年龄和中心调整后，SKILLCOURT 随机星形跑（反应式变向）和简单踏步反应在有/无跌倒史两组间有差异（Holm 校正后显著），TUG、坐站、步速（单任务和双任务）和电脑认知测试没有。随机星形跑每慢 1 SD 比值比 1.82，调整模型 AUC 0.73（灵敏度 70%、特异度 71%），显著高于 TUG（0.63）；简单反应比值比 1.58、AUC 0.72，但不优于电脑简单反应（0.63）。选择反应比值比 1.42、AUC 0.70。未调整 ROC 给出探索性切点：随机星形跑 28.6 秒（AUC 0.66，灵敏度 55%，特异度 76%），简单/选择反应 0.62 和 0.88 秒（AUC 0.63 和 0.61）。 |
| 补充材料实际有什么 | ESM 1（DOCX）已打开：表 S1–S4 是分中心的人群特征、运动、电脑认知和 SKILLCOURT 成绩描述统计（例如随机星形跑中心 1 32.90 ± 7.40 秒、中心 2 31.40 ± 8.41 秒），表 S5 是分中心组效应（β / η²p / p）。没有切点、截距或个人算例。正文表 1–7 的网页（/tables/N）和 PDF 在本次抓取中只返回登录跳转，表内单元格没读到；简单和选择反应切点的灵敏度、特异度应在表 6、表 7，技能不填。 |
| 代码实际算什么 | 论文没有公开代码；数据“可向通讯作者合理索取”。分析用 Jamovi 2.7.4 和 R rms 包 validate.lrm。本技能只做切点对照，不拟合、不重建 logistic 模型。 |
| 同名的另一个东西 | 起立行走测试 13.5 秒、五次坐站 12 秒、步速 1 m/s 等常用跌倒风险界值（论文讨论部分引用）是别的测试和别的人群，本技能不用。坐着按键的电脑简单/选择反应时与 SKILLCOURT 站立踏步反应时不是同一个量。 |

摘要与正文一致：摘要的 “η2p = 0.04” 是正文 Table 4 的 0.039 四舍五入。正文说 28.6 秒切点“derived from the unadjusted Random Star Run analysis (Table 4)”，但判别分析在表 5，这里照原文记录。
