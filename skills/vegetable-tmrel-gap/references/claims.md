# 论文与实现核对

研究设计：系统检索后重新进行 Bayesian meta-regression 的原创研究；Europe PMC
（PMID 36216936）出版类型为 research-article、Journal Article 及研究资助条目，
没有将其标为 Review。实际证据为观察性研究的汇总：49项前瞻性队列、1项 case–cohort，
没有相关随机试验。清单 evidence 使用 cohort 表示主结论来自观察队列；不是随机干预效果。

样本组：正文 Overview 报告50项研究、247项相对风险估计、4,609,296名参与者、34个国家/地区。
缺血性卒中12项前瞻性队列，829,610人；IHD 17项前瞻性队列，1,952,226人、41,494个事件、
78项观察；出血性卒中9项前瞻性队列，646,338人、30项观察；食管癌6项前瞻性队列，818,059人；
糖尿病15项前瞻性队列及1项case–cohort，1,025,899人。结局间存在同一队列，不相加为独立总样本。
各研究自身的高、低暴露组作比较，无个人模型独立验证队列、随机治疗组或安慰剂组。
完整研究名称、地区、人口、性别、随访、年龄、事件和样本量见 Supplementary Table 3。

物种：人（human）；这是人群观察文献的荟萃分析，没有本文动物或细胞实验。

利益冲突：Competing interests 声明作者无利益冲突。资助包括 Bill & Melinda Gates Foundation、
Bloomberg Philanthropies、University of Melbourne、澳大利亚与英国公共卫生机构、
Norwegian Institute of Public Health、St. Jude、Cardiovascular Medical Research and Education Fund、
NIH National Institute on Aging 与 National Institute of Mental Health，见全文 Acknowledgements。

| 论文声称什么 | 补充材料实际有什么 | 代码仓库实际算什么 | 同名或相近项目是什么 |
|---|---|---|---|
| 蔬菜TMREL为306–372克/日 | 表3是研究特征；表7是输入研究的暴露区间、log效应和SE | `risks/vegetables/veg_TMREL.R` 对暴露下界与中点取0.85分位，输入路径为FILEPATH | 本技能是已发表范围的个人差距读出，不是重新估计GBD的TMREL |
| 非线性关联与不同证据星级 | 图1–5为未trim敏感性曲线，图6比较能量调整 | `config.R` 配置递减样条、trim与偏倚校正，预处理脚本整理偏倚协变量 | 通用Burden of Proof方法论文DOI 10.1038/s41591-022-01973-2不是本蔬菜论文 |
| 高摄入关联的证据在结局间不同 | 表6列研究质量评分；表7列研究效应，并非个人预测表 | 通用MR工具及两阶段处理支持风险曲线与证据分数 | 其他风险因素（红肉、吸烟）代码不能借作蔬菜参数 |
| 暴露不含豆类、腌菜、淀粉类蔬菜等 | 补充检索和纳入规则；表5为提取变量定义模板 | 饮食预处理从外部CSV读取暴露上下界 | WHO蔬果合计目标及其他包含土豆、豆类的指南口径不等同 |

风险效应不转成个人结果：摘要和Table 1把从零到TMREL描述为风险下降，部分Results段落反过来
以相同百分比描述零摄入相对TMREL的风险更高。这两个百分比一般不能互换，因此本技能
不借其中一个方向推算个人RR。食管癌摘要的星级与TMREL比较的UI亦不可混作同一个检验。
正文Methods对随访偏倚分界使用months，而仓库预处理代码使用数值10；本技能不使用该协变量。

表号差异：Reporting Summary第2页将研究特征称Table S5、提取表称Table S4，
实际Supplementary Information分别是Table 3与Table 5；资料目录遵循实际PDF编号。
正文Data availability的引用范围和Results Overview的纳入文献编号也不同；样本说明遵循Results及表3。

论文的306–372范围是人群参考范围，不是临床达标线。超出上端点不推断危害，
不输出“还应该吃多少”，只输出已记录克数与参考端点的差。

