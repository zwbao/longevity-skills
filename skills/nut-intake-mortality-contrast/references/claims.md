# 来源、研究对象与实现边界

研究设计：系统综述及剂量反应荟萃分析。Europe PMC 的 PMID 27916000 记录含 `meta-analysis; systematic review`，因此 evidence=review。
实际纳入的是人体前瞻性研究；部分来源队列来自试验，但本分析汇总摄入的观察关联，不能标为 nut 随机试验。
物种：人（human；Homo sapiens）。人体来源为原文明示，学名仅为标准物种标签；讨论中引用的机制研究不是本研究新增实验。
利益冲突：作者声明无 competing interests。资助来自 Olav og Gerd Meidel Raagholt’s Stiftelse for Medisinsk forskning、挪威区域卫生机构与 NTNU 联络委员会、Imperial College NIHR BRC；资助方不参与研究及发表决定。

全部样本结构：20 项前瞻性研究、29 篇论文；9 项美国、6 项欧洲、4 项亚洲、1 项澳大利亚；3 项仅男性、5 项仅女性、12 项两性。主要为成人，其中一项范围为 16–79 岁。没有个人风险方程的训练/验证队列，也没有本技能单独的对照招募。
正文各结局剂量反应样本：冠心病 12,331 例/315,397 人；卒中 9,272 例/396,768 人；心血管疾病 18,655 例/376,228 人；癌症 18,490 例/304,285 人；全因死亡 85,870 例/819,448 人。
这些分析重叠，不能相加成独立样本总量。全文的纳入研究数和各结局实际进入剂量反应分析的研究数不同。
全因死亡正文注明 15 项研究、15 篇论文、16 个风险估计。
表 S7 列出 Adventist（两组）、Oxford Vegetarian、Iowa Women’s Health、EPIC、Nurses’ Health、Health Professionals Follow-up、PREDIMED、SUN、Physicians’ Health、Southern Community、Shanghai Men’s Health、Shanghai Women’s Health、Netherlands Cohort、Blue Mountains Eye、Moli-sani、Linxian 和 Golestan 的来源记录；多篇/亚组不按独立队列机械相加。
所有研究来源表的标题、页码和列结构见 sources.md；不会把某一研究的样本量作为汇总总量。

| 论文声称什么 | 补充表实际有什么 | 代码仓库实际算什么 | 同名的另一个项目是什么 |
|---|---|---|---|
| 总坚果每个印出单位增量与全因死亡的线性关联 | S17 给同一分析的亚组；S7 为来源研究暴露档、RR、校正变量 | 论文没有发布代码链接；本地脚本只换算 Table 1 已汇总斜率 | 不使用其它年份的坚果综述替代本文参数 |
| 全因死亡存在非线性，曲线趋平 | S15 有离散 RR，但标题是 peanuts；与正文引用口径有差异 | 未提供可直接调用的完整样条模型；本技能不重建 | 不把树坚果、花生或花生酱的独立斜率当总坚果 |
| 假定因果关系时可估计地区归因死亡 | S23 有 Region、Country、各结局百分比和 N | 未发布该计算代码；本技能不计算地区或个人归因死亡 | 不移植 GBD 其它版本的数据 |

## 原文内部差异

S14/S15 标题写 peanuts，但正文在总坚果段落引用它们；保留原样并排除在计算之外。
癌症 Results 的非线性检验 P=0.11，Discussion 泛称包括癌症有非线性；不据此扩大技能。
感染死亡异质性摘要与正文/Table 1 不一致；本文部分正文把研究数和死亡数连写。技能不使用这些结局。
全因死亡的高低组 RR 0.81 与线性增量 RR 0.78 是不同对比，不能替换。
表 S7 原始研究可能含 nuts and seeds、nuts and peanut butter 等暴露，定义并不完全一致；本技能继承汇总结果的限制，不能推断单一坚果制品的效应。

边界: 这只是人群观察性研究的线性关联换算，不是你的绝对死亡风险、寿命预测或改变摄入后的因果收益；不能据此决定摄入量，也不能据此开始或停用药物。

## 全因死亡来源记录的样本核对（S7，pp.26–31）

以下是补充表的来源记录，不是互斥的汇总分母，也不全以独立记录进入汇总；不相加替代正文 819,448 人。

| 来源记录 | 表中人数/抽样框 | 死亡数 | 说明 |
|---|---:|---:|---|
| Fraser 1997，Adventist，黑人组 | 1,668 | 416 | 男女，≥25 岁 |
| Fraser 1997，Adventist，白人高龄组 | 基线 603，另有随访中进入高龄组人数未给出 | 1,387 | 不能用 603 当全部死亡的完整分母 |
| Mann 1997，Oxford Vegetarian | 10,802 | 392 | 男女，16–79 岁 |
| Blomhoff 2006，Iowa Women’s Health | 31,778 | 5,451 | 女性 |
| Leenders 2013，EPIC | 451,151 | 25,682 | 男女 |
| Bao 2013，Nurses’ Health | 76,464 | 16,200 | 女性 |
| Bao 2013，Health Professionals Follow-up | 42,498 | 11,229 | 男性；与上一行人数合计 118,962 |
| Guasch-Ferre 2013，PREDIMED | 7,216 | 323 | 男女；按摄入的观察分析 |
| Fernandez-Montero 2014，SUN | 17,184 | 119 | 男女 |
| Hshieh 2015，Physicians’ Health | 20,742 | 2,732 | 男性 |
| Luu 2015，Southern Community | 71,764 | 6,256 | 男女 |
| Luu 2015，Shanghai Men’s Health | 61,123 | 3,387 | 男性 |
| Luu 2015，Shanghai Women’s Health | 73,142 | 4,757 | 女性；与上一行人数合计 134,265 |
| van den Brandt 2015，Netherlands Cohort | 3,202 subcohort members | 8,823 | 病例队列抽样，子队列人数不是全部死亡的分母 |
| Gopinath 2015，Blue Mountains Eye | 2,893 | 1,044 | 男女 |
| Bonaccio 2015，Moli-sani | 19,386 | 334 | 男女 |
| Wang 2016，Linxian | 2,445 | 1,501 | 男女 |
| Eslamparast 2016，Golestan | 50,045 | 3,981 | 男女 |
