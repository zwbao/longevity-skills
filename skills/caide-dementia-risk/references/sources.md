# 来源与可行性检查（2026-11-26）

- 机器未提供浙大缓存根目录，未读取或复制缓存文件。
- [DOI](https://doi.org/10.1016/s1474-4422(06)70537-3)及[ScienceDirect文章页](https://www.sciencedirect.com/science/article/pii/S1474442206705373)：检索索引可见摘要与引言；实时文章页及其pdfft下载被403拦截。检索结果混有相关文献摘要（包括FINGER），不把它们当作本文全文。
- [Lancet全文入口](https://www.thelancet.com/journals/laneur/article/PIIS1474-4422(06)70537-3/fulltext)：403。web-access CDP前置检查发现Chrome端口但代理连接超时，未获得浏览器会话；继续使用公开网页读取。
- [Academia公开全文副本](https://www.academia.edu/13561461/Risk_score_for_the_prediction_of_dementia_risk_in_20_years_among_middle_aged_people_a_longitudinal_population_based_study)：网页读取工具成功返回原刊第735–741页全文，作者、DOI、页眉、表1–4、ROC图说明、利益冲突及44篇参考文献齐全。直接curl遇到验证页，数值依据是网页读取成功的全文文本，不是验证页。全文与参数已人工逐项读取；未将完整文章存入技能目录。
- [PubMed PMID 16914401](https://pubmed.ncbi.nlm.nih.gov/16914401/)：核对作者、题名、期刊卷期年及DOI。
- [Europe PMC核心记录](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:16914401&format=json&resultType=core)：实际读取JSON；isOpenAccess=N、hasSuppl=N，无PMCID；全文链接只有需订阅的DOI。网页版访问失败，REST记录成功。
- [Julkari机构库](https://www.julkari.fi/items/10c45127-fe84-43ae-bcb7-f61d39788d39/full)及[Helsinki研究门户](https://researchportal.helsinki.fi/en/publications/risk-score-for-the-prediction-of-dementia-risk-in-20-years-among-/)：书目元数据；未据此获得附件或系数。
- OpenAlex DOI查询尝试由网页工具返回不可访问；未从该途径取得副本。

表1（736页）列为未痴呆/痴呆/p，描述样本；表2（737页）两模型均有β coefficient、p、OR (95% CI)、Score；表3（737页）两模型均有Score、All/demented (n)、Risk (95% CI)；表4（738页）低/中/高风险类别各含Model 1和Model 2、输入类别、总分与Risk of dementia。计算所需值全部在正文。

已读全文未点名Supplementary Table、Appendix、eMethods、代码库或数据存储库，Europe PMC亦无补充材料记录，因此没有可列出的待下载附件；出版社附件列表因403未直接核验，不将这点写成“已证明没有附件”。没有用后续论文、在线计算器或记忆补常数。
