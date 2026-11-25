# 材料核对记录

访问日期：2026-11-25。当前机器没有用户所述的浙大缓存目录；以下均从公开一手来源取得，原文件只留在临时目录。

- 期刊文章页与全文：[Springer Nature](https://link.springer.com/article/10.1007/s10654-018-0380-1)。卷期为2018年33卷9期811–829页；2018年3月28日在线发表。
- [Europe PMC元数据](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1007/s10654-018-0380-1&format=json)：PMID 29589226、PMCID PMC6133005；pubType包含meta-analysis、systematic review、review-article、journal article。故`evidence=review`，基础研究为人群前瞻性队列。
- [Europe PMC全文XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6133005/fullTextXML)：核对正文、表1、表2、许可、利益冲突、补充文件清单及外部链接。
- 期刊仅列一个补充文件：[10654_2018_380_MOESM1_ESM.docx](https://static-content.springer.com/esm/art%3A10.1007%2Fs10654-018-0380-1/MediaObjects/10654_2018_380_MOESM1_ESM.docx)。网页文本抓取器不能解析DOCX，直接从期刊链接下载成功；已读取OOXML正文及所有表。文件SHA256：`d0d83b497a97d183bd5cbfd3d968a7fc16baa5d09c7645a20f0866fbb216aaa1`。

|材料|已核对的内容和列|用于计算|
|---|---|---|
|正文表1|Authors、Country/cohort、Exposures investigated (events)、n at baseline/average follow-up、Average age/proportion male、covariates|否，描述队列|
|正文表2|Outcome (cases/n baseline)、exposure/studies、PA调整前后summary RR (95%CI)、p、I²、non-linearity p|否，核对设计及摘要差异|
|附表1|数据库与Google Scholar的Search terms|否|
|附表2|Exposure、Categories used by study authors、Dose applied to exposure category，总久坐研究赋值|否，不重做剂量赋值|
|附表3|Exposure、Categories、Dose applied，电视研究赋值|否|
|附表4|Authors、Inclusion criteria、Health related exclusion criteria/adjustments、Representativeness、Outcome measure、Exposure measure、Physical activity measurement|否，适用性和测量限制|
|附表5|Outcome、Exposure、Below Threshold、Above Threshold；两行分别给小时范围与RR (95%CI)|是，四个独立分段|
|附表6|RR、95%CI、Number of studies、I²、p-value，亚组/敏感性分析|否，不提供亚组选择器|
|附表7|四个结局，各有dose h/day、RR、LCI、UCI|是，总久坐72条印刷行|
|附表8|四个结局，各有dose h/day、RR、LCI、UCI|是，电视66条印刷行|
|附图1–2|调整前后每增加1小时线性RR森林图，DOCX内EMF|未数字化；不用图形拟合系数|
|附图3–4|调整前后非线性关系图，DOCX内EMF|未数字化；数值以附表7–8为准|
|附图5|漏斗图与Egger检验，DOCX内EMF|不用于个人输出|

附图的图题及嵌入对象已检查；本实现不依赖从图像读取数值。没有其它单独附表文件或未下载的补充链接。未发现本文发布的代码仓库或Zenodo/OSF数据链接；不是“找不到系数所以假定不存在”，而是选择明确公开的查表输出作为方法合同。

`printed-tables.tsv`保留附表5、7–8的转写，表格跨列用制表符表达；`data/*.csv`将四个横向结局块展开为长表，数字原样转写。出处：Patterson et al. (2018)，DOI 10.1007/s10654-018-0380-1，文章及补充材料按[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)使用；更改仅为格式转写、中文说明与查表接口。
