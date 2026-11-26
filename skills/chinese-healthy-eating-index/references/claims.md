# 原文与技能逐项核查

- 研究设计：基于DGC-2016开发方法，并对CHNS-2011进行横断面应用与社会人口因素关联分析。虽数据来自前瞻开放队列，本论文个人读出及主要关联分析没有随访疾病结局。Europe PMC记录出版类型research-article; journal article，非综述。
- 全部样本组：CHNS-2011共14,584人，年龄≥2岁，饮食数据及协变量完整；连续三日24小时回顾及同周期家庭油盐库存称重资料。没有独立病例、对照、外部验证队列或随机干预组。Table 4低、中、高三分位人数分别4861、4862、4861，为同一批人的分层，不是验证样本；年龄组2–17、18–59、≥60岁。原文不报告完整个人记录。
- 物种：人（human），无动物或细胞实验。
- 利益冲突：作者声明无利益冲突。资助包括National Key Research and Development Program of China（2016YFD0400602）和National Natural Science Foundation of China（30972474、81202208）；CHNS数据收集另有正文Acknowledgments列出的机构资助。不额外推断商业关系。

| 论文声称什么 | 补充表里实际有什么 | 代码仓库实际算什么 | 同名的另一个项目是什么 |
| --- | --- | --- | --- |
| 17项连续得分衡量与DGC-2016符合程度，最高100分 | S1列10大食物组每SP的能量、碳水、蛋白、脂肪和代表食物量；S2列各能量水平推荐克数及SP | 论文没有发布代码仓库；本实现以Table 3及正文公式计算个人SP记录 | 不是美国HEI、Chinese Dietary Balance Index或Chinese Food Pagoda Score，也不使用后续指南版本 |
| 对1289种单食物作SP换算 | 没有逐项1289食物的转换表；只有示例及营养范围 | 不实现任意食物自动分类/克数转SP，不取范围中点 | 不能把其他项目或记忆中的份量冒充本文换算 |
| 酒精因人群而异 | 补充表没有另一份酒精公式 | 按§3.1.3的明确文字；记录Table 3倒置问题 | 不将酒精满分解读为安全摄入量 |
| 与社会人口特征有关 | S1图是2002/2012营养现状与推荐范围，非个人验证集 | 不使用Table 6系数修改个人分数；正文把5.13、6.83描述为fold，但表内是线性系数，不能当倍数风险 | 不等于疾病预测模型或因果干预效果 |

已逐项打开的材料及列：

- Table 1：Components、Weighting、Key Recommendations、Comments、Key Evidence。
- Table 2：Food Group；各Calorie Level下的Standard Portion per 1000 kcal；Cooking Oils另用g/1000 kcal。
- Table 3：Component及Score 0、5、10；为主要运行常数来源。
- Table 4：Characteristics、总样本及三个CHEI分层、p for Trend。
- Table 5：CHEI Score分组、Mean、1st至99th百分位。
- Table 6：Variables、CHEI Score Mean(SD)、Univariate和Final Multivariate的Coefficient(95%CI)、p-Value。
- Figure 1：各性别/年龄组17项得分分段比例；没有个人输入。
- Figure S1a/b：Recommended Intake Ranges 2016、Average Intake 2002、Average Intake 2012，纵轴grams；没有个人示例。
- Table S1：Food categories、Energy per SP(kcal)、Carbohydrate per SP(g)、Protein per SP(g)、Fat per SP(g)、Examples of one SP。
- Table S2a/b：Food Group(g或SP)、Calorie level(kcal)，11个水平1000–3000；部分食品列留空并说明appropriate amounts，未擅补。

全文与补充包均已读取；唯一补充PDF中的全部材料均已打开。没有发现GitHub、Zenodo、OSF、eMethods或单独Appendix链接。所有选择与不能计算的部分见[contract.md](contract.md)。
