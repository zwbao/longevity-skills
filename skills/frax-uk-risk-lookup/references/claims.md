# 论文证据核查

来源：Kanis 等，FRAX and the assessment of fracture probability in men and women from the UK，Osteoporosis International，2008，19(4):385–397。[出版社全文](https://link.springer.com/article/10.1007/s00198-007-0543-5)，[PMC全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC2267485/)，[PubMed记录](https://pubmed.ncbi.nlm.nih.gov/18292978/)。

研究设计：风险预测方法开发及英国流行病学校准，利用既往前瞻性人群队列和危险因素荟萃分析。不是干预随机试验，也不把出版社栏目“Special Position Paper”当作试验设计。清单evidence为method。

全部样本组：方法段列9个推导队列——Rotterdam、EVOS/EPOS、CaMos、Rochester、Sheffield、Dubbo、Hiroshima和Gothenburg的两个队列。正文没有逐队列人数及推导合计，不能补造；相关详情引用既往文献。讨论引用先前研究在11个独立前瞻性队列、超过一百万人年中验证；本文没有逐队列名称/人数清单，不能把人年当人数。本技能只用表2校准输出，不读取这些队列的个体数据，没有病例对照组或新试验组。

物种：人（human）；本文无动物或细胞实验。

利益冲突：作者声明“None.”。同时Acknowledgements列出Alliance for Better Bone Health、Amgen、Hologic、IGEA、Lilly、Lunar、Novartis、Pfizer、Roche、Wyeth及EU支持；International Osteoporosis Foundation、International Society for Clinical Densitometry、National Osteoporosis Foundation提供不受限制的支持。无冲突声明不等于无产业资助。

| 论文声称什么 | 正文/补充材料实际有什么 | 本技能实际算什么 | 同名的另一个项目 |
|---|---|---|---|
| 整合危险因素和可选股骨颈BMD估计十年骨折概率 | 表1–3和图1–7；内嵌Appendix给一般表达式，未印完整数值参数；无独立补充文件 | 表2离散点直接匹配，无连续风险模型 | 当前官方FRAX可能含其他国家及更新参数，不能等同本技能 |
| 年龄、性别、单一危险因素对应不同概率 | 表2两性、四年龄、七分类、两结局，共112格 | 使用真实输入选择唯一一格/结局，不取整或外推 | 其他国家FRAX校准及FRAXplus不在实现内 |
| 多因素进一步增加概率 | 正文有特定年龄组合范围及图示，无任意组合完整查表 | 多危险因素退出3，不能将单项风险相加或相乘 | 未调用在线FRAX，也未拟合其输出 |
| 骨密度加入后影响不同 | 表1右侧与表3有特定T-score值 | 不纳入本次无BMD范围 | 不把腰椎BMD换成股骨颈BMD |
| 高酒精摄入为二元风险因素 | 方法段每日3个及以上单位，表2行名>2 units daily；未给克数换算 | 仅接受已确认分类，不根据杯数推断 | 未借用后续工具的定义或剂量调整 |

表2主要结局包括临床脊柱、髋部、肱骨和前臂骨折；髋部是其中一部分。概率不等于诊断，表内没有个人置信区间。所有参数来自表2；合同记录其完整列结构、排除条件、可行性核查及复现测试。原文模型描述的缺失参数不影响有限查表，但阻止声称实现完整FRAX。
