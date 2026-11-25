# 证据与材料核查

论文：Morley JE、Malmstrom TK、Miller DK，The journal of nutrition, health & aging，
16(7):601–608，2012，doi:10.1007/s12603-012-0084-2。
使用卷期年2012；Springer网页另列2013年上线时间，不改变引用年份。

研究设计：社区纵向观察队列，有基线横断面分析。Europe PMC / PubMed出版类型为
Validation Study、Journal Article、Research Support, N.I.H., Extramural；不是综述或随机试验。

全部样本组：AAH原始队列998名美国圣路易斯社区非裔成年人，来自内城和近西北郊两个
社会经济条件不同的地区，并非两个独立验证队列；基线年龄49–65岁，MMSE至少16分。
九年后复评582人，期间死亡163人。基线排除ADL困难的分析样本703人
（健壮421、衰弱前期263、衰弱19）；排除ADL依赖的样本883人
（健壮444、衰弱前期373、衰弱66）。两组互相重叠，不能相加。
功能随访样本分别最多423人（263、153、7）和528人（276、225、27），
各结局有进一步缺测。实验室血样总共349人；按上述排除口径进入实验室分析的分别
239人（136、95、8）与317人（147、142、28）。没有训练/留出测试的分割。

物种：人（human；原文为African Americans）。研究没有动物或细胞实验。

利益冲突：Acknowledgments后作者声明与本文无冲突。
资助：美国National Institute on Aging给D. K. Miller的R01 AG-010436；未发现本文工具的商业专利或受雇声明。

## 打开过的材料

核查日期：2026-11-25。用户注明本机无浙大缓存，未假定存在缓存附件。

- [Springer文章页](https://link.springer.com/article/10.1007/s12603-012-0084-2)：摘要、元数据、参考文献；正文为订阅内容，未列独立补充附件。
- [PMC作者接收稿](https://pmc.ncbi.nlm.nih.gov/articles/PMC4515112/)：页面直连遇到验证码；通过web-access允许的Jina读取正文与内嵌附录，HTML未完整呈现表1–7。
- [NCBI BioC全文接口](https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC4515112/unicode)：成功打开全文结构，补齐导言及表1–7的全部表格单元、列头和脚注；附录表在接口中标T8。
- [Europe PMC元数据](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1007/s12603-012-0084-2&format=json&resultType=core)：成功；核对作者、卷期年、出版类型、PMCID及hasSuppl=N、hasData=N。
- Europe PMC HTML/PDF、fullTextXML及PMC PDF直接访问未成功；全文已由上述作者接收稿和官方BioC接口读到，不把失败的入口当作无材料。

全文未点名发布代码仓库、GitHub、Zenodo或OSF数据包。论文提及总样本维生素D分析数据可向作者索取，
这不是公开数据附件，也不参与FRAIL评分。不把网页页脚NCBI GitHub链接当作论文代码。
下载的原文仅在临时目录用于核对，没有复制进技能。

## 表格列与用途

| 材料 | 实际列/内容 | 是否用于个人计算 |
| --- | --- | --- |
| Appendix 1（BioC T8） | 五行题干、回答编码、计分规则、基线患有率 | 只用题干和计分，患有率不当个人概率 |
| Table 1 | 按两种ADL排除口径列Healthy、Prefrail、Frail及P-Value；基线特征 | 只核对队列构成 |
| Table 2 | 两种口径的Baseline和9-Year Follow-Up，三分层的结局均值/SD或百分比及逐项n | 描述性人群结果，无个人完整输入记录 |
| Table 3 | Cross-sectional / Longitudinal Outcomes；两种口径；Models 1a/2a/1b/2b；B(SE)、P-Value、Odds Ratio(95% CI) | 不当作个人绝对风险模型 |
| Table 4 | 单项与横断面结局；两种口径；B(SE)、P-Value、OR(95% CI) | 不改变五项等权规则 |
| Table 5 | 单项与纵向结局；两种口径及两种调整模型；B(SE)、P-Value、OR(95% CI) | 不改变五项等权规则 |
| Table 6 | 两种口径、三个分层的实验室指标原值及log10值、P-Value | 不要求用户提供血液指标 |
| Table 7 | 两种口径；实验室log10指标与Prefrail/Frail的B(SE)、P-Value | 不要求用户提供血液指标 |

## 主张、材料和实现的区别

| 论文声称什么 | 附录/表格实际有什么 | 本技能代码实际算什么 | 同名或相近方法是什么 |
| --- | --- | --- | --- |
| 问卷分层与九年功能下降及死亡有关 | 群体关联，且随结局、排除口径和调整模型不同 | 单次问卷分数与分层 | 不是预期寿命或死亡概率计算器 |
| 五项各计一分 | Methods有等权规则及总分分档，Appendix 1有逐项编码 | 五项加总，输出每项便于核对 | 不是Fried表型、Rockwood缺陷累积指数或FRAIL-NH |
| 疾病项按指定类别计数 | Appendix 1明确11类、5类为阳性起点 | 输入指定疾病种数，并按原文重编码 | 不用任意“慢病总数”，不改成超过5类 |
| 体重下降使用一年窗口 | 正文至少5%，附录大于5%/小于5%，缺等号 | 恰好5%按正文计1，始终提示差异 | 不采用其他问卷的半年、一个街区等改写 |

摘要与表格另有差异：摘要声称调整基线后的frail在两个口径都预测IADL困难，
但Table 3无ADL困难组Model 2a的IADL frail为B=0.40、P=.508；
无ADL依赖组Model 2b为B=0.99、P=.006。按表格限定关联，不复述摘要的普遍显著说法。
死亡属于二元logistic关联，不能把OR当风险比或个人风险。

原文复现证据限定于Appendix 1印出的逐项分值；skill.json中保留短引文，
测试直接枚举原文疾病区间。无公开个体数据，不声称重新验证九年预测表现。
