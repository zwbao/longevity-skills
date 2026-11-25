# 材料核查记录

核查日期：2026-11-25。用户说明本机没有浙大缓存目录，未复制任何缓存或原文文件到仓库。
下载文件、全文转文本、作者代码克隆与公开API响应均只放在临时目录作核查。

## 全文和出版记录

- [Nature Medicine文章页](https://www.nature.com/articles/s41591-022-01970-5)：静态HTML取得全文，包括Methods、Table 1、扩展图1–4、Data/Code availability、作者声明及全部补充链接。浏览工具遇到身份重定向，curl可读。
- [PMC全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC9556321/)：成功打开，与期刊的DOI、年份、结果、定义一致。
- [Europe PMC出版记录](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:36216936&format=json&resultType=core)：核查Journal Article/research-article及2022卷期年。

计算使用的逐字短引文（Results → Minimum risk level of vegetable intake）：

> We estimated a TMREL of 306–372 g per day, corresponding to approximately 4–5 servings per day.

Table 1 给出从零摄入至同一范围的风险比较；没有印出个人摄入差距算例。
只冻下这两个端点，不抄整篇原文。论文为CC BY 4.0，引用归属Stanaway等。

## 全部独立补充文件

1. [Supplementary Information / MOESM1](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-022-01970-5/MediaObjects/41591_2022_1970_MOESM1_ESM.pdf)：下载并提取全部文本，核查表与图。
2. [Reporting Summary / MOESM2](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-022-01970-5/MediaObjects/41591_2022_1970_MOESM2_ESM.pdf)：下载，两页为图像，已逐页渲染阅读；确认样本、无原始数据采集、无随机化和代码数据链接。

| Supplementary Information位置（PDF自身目录页码） | 核查的内容或列名 |
|---|---|
| Section 1，p3–6 | 五结局检索式、纳入排除规则、检索结束日期 |
| Table 1，p7–8 | PRISMA Topic、Item、Checklist item、Location |
| Table 2，p9 | PRISMA abstract checklist及所在段落 |
| Table 3，p10–21 | Author、Year、Study name、Population、Location、Study design、Sex、Follow-up、Age start/end、Exposure assessment、Endpoint、Disease ascertainment、Events、Sample size、Outcomes |
| Table 4，p22 | GATHER报告要求和正文对应位置 |
| Table 5，p23–27 | Category、Variable、Definition；含nid、暴露上下界、参考组上下界、效应值、偏倚变量的定义模板，没有逐人数据 |
| Table 6，p28–29 | Author、Year、Outcome、Exposure Measurement Score、Exposure Assessment Score、Outcome Assessment、Confounders Score、Quality Score |
| Table 7，p30–36 | Outcome、Alternative group exposure、Reference group exposure、Log effect size、Log effect size standard error、Study |
| Figures 1–5，p37–39 | 五结局不剔除异常点的log RR、RR曲线及漏斗图 |
| Figure 6，p40 | 热量调整与未调整的敏感性比较 |

这两份文件就是期刊该文章页列出的独立补充文件，没有另列Excel、Zenodo或OSF附件。
没有把未打开的附件当作没有内容。

## 公开代码

[ihmeuw-msca/burden-of-proof](https://github.com/ihmeuw-msca/burden-of-proof)，
克隆核查commit `c8ad876a579cfd136850c13549aa706cd0fa2437`。
打开主README和`risks/vegetables/`全部4个文件：README.md、config.R、
Prep bias covariates for diet MR_BRT.r、veg_TMREL.R。
后者按nid、b_0、b_1去重，构造b_midpoint，再取0.85分位并生成uniform draws；
输入及输出路径均为FILEPATH。没有个人摄入差距计算示例。没有执行训练代码。
通用`first_process`、`second_process`、`mrtool`与`limetr`是元回归相关代码，
不作为本技能计算依赖。

## 论文链接的公开数据

[IHME VizHub Burden of Proof](https://vizhub.healthdata.org/burden-of-proof/)已打开。
从页面脚本中确认其只读API，取得风险和结局元数据后，下载并检查全部五结局的
`study_data`、`output_data`、`study_citations`响应。请求格式：
`https://vizhub.healthdata.org/burden-of-proof/api/v1/{endpoint}?risk=112&cause={cause_id}`。

| 本文结局 | cause_id | study_data行数 | output_data行数 | study_citations行数 |
|---|---:|---:|---:|---:|
| 食管癌 | 411 | 24 | 100 | 6 |
| 缺血性心脏病 | 493 | 92 | 100 | 17 |
| 缺血性卒中 | 495 | 55 | 100 | 12 |
| 出血性卒中对应数据系列 | 496 | 30 | 100 | 9 |
| 2型糖尿病 | 976 | 68 | 100 | 16 |

study_data包含ref_risk_lower/ref_risk_upper、risk_lower/risk_upper、study_id、
log_observed_relative_risk、log_observed_relative_risk_standard_error及人群属性。
output_data包含risk、linear_cause及其上下界、log_cause及其上下界，
sex_name、age_group_name、location_name与category_id。
study_citations含study_id、field_citation_value。
因此确实存在公开风险曲线数据，不能宣称全套风险数值从未公开。
但当前IHD响应有92行，与正文78项观察不同；未确认发表时的冻结数据版本。
本技能不插值这些曲线、不重估TMREL，不用当前接口数值作为2022论文复现证据。

## 可行性结论

个人差距合同只需要正文已经印出的306与372两个端点，所需常数没有缺失，允许创建A类技能。
独立个人差距算例未印出，验证保持draft。无需创建因缺少计算常数而停止的PIPELINE_NOTE.md。
