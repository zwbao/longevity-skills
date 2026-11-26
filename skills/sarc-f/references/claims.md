# 原文核查

论文：Malmstrom 等，Journal of Cachexia, Sarcopenia and Muscle，2016，7(1):28–36。
DOI：10.1002/jcsm.12048。2015年在线发表，按卷期年登记2016。

研究设计：原创人群观察验证研究；AAH和BLSA包含横断面与纵向结局，NHANES为横断面。
出版社标注Original Article，PubMed记录并非综述；主结论按cohort登记。
全部样本：AAH初始998人（2000–01年49–65岁），本研究分析Wave 4的853人，
六年后Wave 10访谈582人；853人中筛查阳性157、阴性696。
BLSA分析1053名≥60岁参与者，阳性66、阴性987，功能随访27.07±11.7个月，
死亡状态追踪最长9.75年。NHANES 1999–2002原始21004人，本研究有效分析3288名60–85岁参与者，
阳性505、阴性2783。三个人群用于验证，非随机试验，未划分机器学习训练/测试集。
AAH最初入组年龄不是Wave 4年龄；Discussion将AAH与BLSA概括为随后六年，
本技能按Methods逐队列记录随访，不统一写成六年。
物种：人（human），没有动物或体外实验。
利益冲突：作者声明无。资助：美国国家老龄研究所R01 AG010436及其院内研究计划。

| 论文声称什么 | 补充表里实际有什么 | 代码仓库实际算什么 | 同名或相近项目是什么 |
| --- | --- | --- | --- |
| 五项症状和跌倒自述可按固定规则筛查功能风险 | 无独立补充表；规则逐项印在正文Methods | 未列配套研究代码；本技能实现原文计分，不声称是作者代码 | 采用AAH/BLSA版本；NHANES为替代措辞版本 |
| 阳性分档与不良功能、住院及死亡有关 | 正文表2–5给群体比较、OR及B系数，不是个体预测表 | 本技能不输出OR、绝对概率或干预效应 | FRAIL是另一套衰弱问卷；SARC-CalF及其他扩展不在本实现 |

## 材料访问记录

核查日期：2026-11-26。用户说明本机无订阅缓存。

- [出版社文章页](https://onlinelibrary.wiley.com/doi/10.1002/jcsm.12048)：全文、表1–5、利益冲突、参考文献和页尾均已核对，无Supporting Information文件列表。
- [PMC全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC4799853/)：已阅读正文、方法计分、讨论、所有表格与文末；未列附录或独立补充文件。
- [Europe PMC全文XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4799853/fullTextXML)：已读取，supplementary-material、media、app节点均为0；仅在临时目录检查，未复制入库。
- [PubMed记录](https://pubmed.ncbi.nlm.nih.gov/27066316/)：核对题名、作者、卷期年及全文入口。
- 页面及全文未指向本研究的GitHub、Zenodo、OSF或其他代码/数据发布包。没有未下载的已列补充文件。

## 正文表格检查

| 表 | 栏或分组 | 用途 |
| --- | --- | --- |
| 1 | AAH/BLSA/NHANES；SARC-F≥4的Yes/No、人数、P-value；年龄、性别、教育、收入等 | 样本描述，不是评分系数 |
| 2 | 各队列；SARC-F≥4的Yes/No；IADL、起坐、握力、SPPB、步行、膝伸肌力；OR(95% CI)、P-value | 横断面分组结局 |
| 3 | 各队列及各单项；Unstandardized coefficients B(SE)、OR(95% CI)、P-value | 横断面单项关联，不是问卷加权 |
| 4 | AAH/BLSA；SARC-F≥4；B(SE)、OR(95% CI)、P-value | 纵向分组结局 |
| 5 | AAH/BLSA及各单项；B(SE)、OR(95% CI)、P-value | 纵向单项关联，不是问卷加权 |

各表无给定完整个人五项输入的结局预测示例。可复现的印出示例是Methods中的逐项计分，
validation明确限定于跌倒单项。论文也指出需在其他人群及标准肌少症定义下进一步验证；
筛查阴性不表述为确认健康。
