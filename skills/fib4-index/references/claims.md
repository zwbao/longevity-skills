# 证据核对

研究设计：成人 NAFLD 的横断面诊断性能比较，使用 NASH CRN 自然史数据库和 PIVENS 试验的基线数据；不是随机干预效果分析。Europe PMC 的出版类型含 Comparative Study、Evaluation Study、Journal Article，非综述。

全部样本组：总计 541 名成人；NASH 317 人（stage 0–2 为 216，stage 3–4 为 101），非 NASH 224 人（分别 200、24），合计低分期 416、进展期 125。正文没有分别列出自然史数据库与 PIVENS 的来源人数，不能自行分配。纤维化 stage 0/1/2/3/4 分别 140/159/117/85/40。儿童 TONIC 被排除；无另招募健康对照或独立外部验证队列。留一法及 50:50、80:20 随机拆分均在同一数据集内。研究排除了其他并存肝病。

物种：人（human / Homo sapiens）。本文自己的分析无动物或细胞实验；正文明确为 adults，并非从参考文献中的物种推定。

利益冲突：已核查 PMC XML 的 front、正文及 back，未见专门 Disclosures / Competing interests 声明；不能记作“无”。出版社排版全文未能打开，最终版声明未核对。论文明确来源于 NIH NASH CRN，Europe PMC 标注 NIH extramural research support；不能据此推断无其他资助或利益关系。

| 论文声称什么 | 补充表里实际有什么 | 代码仓库实际算什么 | 同名的另一个项目是什么 |
| --- | --- | --- | --- |
| 表 1 用年龄、AST、ALT 与血小板定义 FIB4；表 5 使用两个切点 | PMC XML 无 supplementary-material、app、media 或外部代码数据链接；Europe PMC hasSuppl=N。公式在正文表 1 | 论文未提供代码链接；本技能为表 1 的独立实现 | 2006 年 HIV/HCV 原始开发与其他肝病验证是不同研究；不借用其阈值 |
| 表 2、3 是临床特征汇总；表 4 是各指标的分期汇总 | 无额外个人样例表可读取 | 不从组均值或中位数构造个人验证 | NAFLD fibrosis score、APRI、BARD 等是比较方法，本技能不输出它们 |
| 表 5、6 报告诊断性能受患病率影响 | 无可获得的个体队列链接 | 不将队列 PPV/NPV 输出为个人概率 | 不是后续临床指南或最新年龄校正方案 |
| Discussion 未验证 FIB4 变化是否对应纤维化变化 | 未列纵向验证补充文件 | targets 仅替换公式输入，报告明确限制 | 不是治疗获益模型或治疗推荐系统 |

## 原文差异与不扩大的结论

- 接收稿题名为 USE OF THE FIB4 INDEX FOR NON-INVASIVE EVALUATION OF FIBROSIS IN NONALCOHOLIC FATTY LIVER DISEASE；DOI、PMID、作者、卷期页码一致，最终题名按 PubMed / Europe PMC 的出版记录登记，不把接收稿误判为另一研究或预印本。
- 摘要起初称比较六项指标，方法、结果和表格实际有七项对照指标。结果中 FIB4 对 NAFLD fibrosis score 的 AUROC 差异未达通常显著性水平，不能复述成显著优于全部比较方法。
- 摘要把 AUROC 0.802 称为 jackknife-validated；正文 Validation 写全样本 0.802、留一法 0.797、拆分 0.795 与 0.794。个人报告不使用这些作为个人精度。
- 正文将 FIB4 汇总指向表 3、原始指标指向表 4，实际两者相反，以表格内容为准。
- 正文称 378 人占 72%，但表 5 总样本为 541；不把该百分比放入个人结果。正文 Caucasian 400 与表 3 的 402 也不同，不用于计算。
- 摘要切点等号与表 5 严格不等号不同，采用表 5，详见合同。

## 材料访问记录（2026-11-26）

- 无用户提供的本机缓存目录；未将缓存或完整论文复制到仓库。
- [PubMed 出版记录](https://pubmed.ncbi.nlm.nih.gov/19523535/) 与 [Europe PMC 核心元数据接口](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:19523535&format=json&resultType=core)：已读取，确认 DOI、年、作者、出版类型及 hasSuppl=N。
- [ScienceDirect 文章页](https://www.sciencedirect.com/science/article/pii/S1542356509005333)、[期刊全文页](https://www.cghjournal.org/article/S1542-3565%2809%2900533-3/fulltext)、[期刊 PDF](https://www.cghjournal.org/article/S1542356509005333/pdf)：403 或验证页，未读到最终排版版及其附件列表；不能声称已核查出版社独有附件。
- [PMC 全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC3079239/)：直接访问为验证页，通过文本代理取得完整接收稿正文和六张表；随后从 [NCBI 公共存储原始 XML](https://pmc-oa-opendata.s3.amazonaws.com/PMC3079239.1/PMC3079239.1.xml) 直接读取并核对表 1、表 5、所有表格及元数据。原始 XML 明确标记无补充材料、不是预印本；没有点名的 GitHub、Zenodo、OSF 或数据文件需要另行打开。
- [Europe PMC 全文](https://europepmc.org/articles/PMC3079239)、PDF render：验证页；fullTextXML 接口返回服务端错误。PMC PDF、表格独立页未能获取；BioC 接口限流。
- [OpenAlex 开放位置](https://api.openalex.org/works/doi:10.1016/j.cgh.2009.05.033) 已读取，仅列出版社、PubMed、PMC/Europe PMC，接收稿身份确认；[NASH CRN 论文目录](https://jhuccs1.us/nash/open/NASH_publications.pdf) 同样列该接收稿题名与卷期页码。
- 原始 XML 含 Figure 1 六个 ROC 图像引用及 Figure 2 图像引用，但没有文本图注；公共存储的文章目录只有 JSON、TXT、XML，不含图像或 PDF。未取得图像内容；验证缺口保留，不声称图中没有个人算例。

全文公式与分档参数均完整可读；无法打开的出版社页面和图像不用于声称复现或补充未见的参数。
