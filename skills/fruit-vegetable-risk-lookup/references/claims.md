# 论文与实现的对应关系

研究设计：PubMed PMID 28338764 的出版类型为 Meta-Analysis 和 Systematic Review，属于人体前瞻性队列的系统综述与剂量反应荟萃分析，清单 evidence=review；不是随机分配摄入量的试验。Aune 等，International Journal of Epidemiology 46(3):1029–1056，卷期年2017，DOI 10.1093/ije/dyw319。

全部样本组：正文 Results 报告95个独立队列、142篇出版物；欧洲44、美国26、亚洲20、澳大利亚5个研究。各分析的研究、参与者与病例/死亡数不同，不可直接求和，亦无独立的个人模型推导/验证队列。Supplementary Tables 3–7列出全部队列、年龄、性别、随访期、饮食测量、病例、调整变量；Table 1各分析的计数汇总在本文末尾，保留原文的大于号。

物种：人（human）；没有本研究新增的动物或细胞实验，讨论中引用动物或机制论文不算本论文实验物种。

利益冲突：正文“Conflict of interest: All the authors declare no conflict of interest.”。资助为 Olav og Gerd Meidel Raagholt’s Stiftelse for Medisinsk Forskning、Central Norway RHA与NTNU联络委员会、Imperial College NIHR BRC；作者称资助方未参与设计、研究实施、资料收集/分析、解释、写作/审核或发表决定。未声明与本文干预相关的专利或商业受雇关系。

| 论文声称什么 | 补充材料实际有什么 | 作者代码实际算什么 | 同名或相近项目 |
|---|---|---|---|
| 果蔬摄入量与冠心病、卒中、心血管疾病、总癌症及全因死亡相关，低摄入范围关联变化更陡 | 表8–18分别列出合计、水果、蔬菜的摄入g/d及非线性RR/95% CI，不同列参照和尾端不同 | 全文和两份补充材料未链接代码仓库；正文称使用Stata 13.0。此技能是表格读取器 | 不是个人ASCVD风险方程，也不是饮食质量评分 |
| 疾病的主分析合并发病与死亡，另做亚组 | 表8–11、14–17分别给mixed/incidence/mortality；表12–13为卒中亚型；表18为全因死亡 | 无作者程序可供核对；不以线性每200g RR替代非线性表 | 不与其他年份的果蔬荟萃分析交换数值 |
| 部分食物亚类有关联 | 表19–27为亚类曲线，正文表2–6与图32–242为相关结果 | 本技能不实现亚类输入，明确限定总果蔬、水果、蔬菜 | 不把亚类摄入量冒充总量 |
| 全球可归因死亡数依赖因果与可推广性假设 | Supplementary Methods、表33有人群分布/归因量 | 不计算个人可避免死亡数或寿命 | 人群归因负担不是个人概率 |

正文 Discussion 和Table 7使用低于500 g/d对应约5.4 million的全因归因死亡数，而摘要写5.6 million；此差异不影响所读非线性RR表，本实现完全不输出该归因量。Supplementary Table 13合计果蔬列为横线/空白，并非可用的出血性卒中曲线，始终标记未印出。

## Table 1 的全部分析计数

这些是研究级背景，不写成用户的结果；高低比较与线性剂量反应计数不自动当作每个非线性子列的计数。

| 食物组/结局 | 比较 | 研究数n | 病例或死亡数 | 参与者数 |
|---|---|---|---|---|
| Coronary heart disease | | | | |
| Fruit and vegetables | High vs low | 16 | 18516 | 792197 |
|  | Per 200 g/d | 15 | 17742 | 775132 |
| Fruit | High vs low | 25 | 40229 | 1568460 |
|  | Per 200 g/d | 24 | 43336 | 1555553 |
| Vegetables | High vs low | 22 | 34754 | 2123415 |
|  | Per 200 g/d | 20 | 20853 | 1047071 |
| Stroke | | | | |
| Fruit and vegetables | High vs low | 8 | 10560 | 226910 |
|  | Per 200 g/d | 10 | 11644 | 303338 |
| Fruit | High vs low | 17 | 46951 | 960337 |
|  | Per 200 g/d | 16 | 46203 | 964142 |
| Vegetables | High vs low | 13 | 14519 | 427124 |
|  | Per 200 g/d | 13 | 14973 | 441670 |
| Cardiovascular disease | | | | |
| Fruit and vegetables | High vs low | 16 | 27842 | 963240 |
|  | Per 200 g/d | 13 | 20329 | 877925 |
| Fruit | High vs low | 21 | 81807 | 1605227 |
|  | Per 200 g/d | 17 | 72648 | 1492617 |
| Vegetables | High vs low | 18 | 32049 | 1112174 |
|  | Per 200 g/d | 14 | 23857 | 1009038 |
| Total cancer | | | | |
| Fruit and vegetables | High vs low | 13 | 54123 | 904300 |
|  | Per 200 g/d | 12 | 52872 | 902065 |
| Fruit | High vs low | 21 | 105401 | 1569168 |
|  | Per 200 g/d | 20 | 112370 | 1648240 |
| Vegetables | High vs low | 17 | 101118 | 1505948 |
|  | Per 200 g/d | 17 | 108855 | 1597722 |
| All-cause mortality | | | | |
| Fruit and vegetables | High vs low | 22 | 87574 | 1035556 |
|  | Per 200 g/d | 15 | 71160 | 959083 |
| Fruit | High vs low | 30 | 93473 | >1144194 |
|  | Per 200 g/d | 27 | 94235 | >1104255 |
| Vegetables | High vs low | 24 | 82904 | 1082960 |
|  | Per 200 g/d | 22 | 86264 | 1050795 |
