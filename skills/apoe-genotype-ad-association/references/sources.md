# 材料核查（2026-11-26）

没有配置浙大订阅缓存路径；未复制缓存全文到仓库。

| 材料 | 已打开的内容 | 数字与用途 |
| --- | --- | --- |
| [期刊全文页](https://jamanetwork.com/journals/jamaneurology/fullarticle/2811630) | 论文、正文表、两份补充文件目录 | 确认发表年份、作者、原始研究与主表 |
| [PMC 全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC10628838/) | 完整 Methods、Results、Discussion、Table、利益冲突、图注 | 主表提取为结构化行；主要解释依据 |
| [Supplement 1](https://pmc.ncbi.nlm.nih.gov/articles/instance/10628838/bin/jamaneurol-e233599-s001.pdf) | 50页 PDF；eMethods、eAppendix、eFigures 1–6、eTables 1–16、eReferences | 页码与列名见下 |
| [Supplement 2](https://pmc.ncbi.nlm.nih.gov/articles/instance/10628838/bin/jamaneurol-e233599-s002.pdf) | Data Sharing Statement，1页 | 作者不再分发个体数据，需向原仓库申请 |
| [PubMed PMID 37930705](https://pubmed.ncbi.nlm.nih.gov/37930705/) | 期刊卷期 80(12):1284–1294、2023 Dec 1 | 原创 Journal Article，非综述 |

PMC 补充文件直链访问遇到人机验证；成功通过期刊 CDN 的签名链接取得 Supplement 1，
并通过 [Europe PMC supplementaryFiles](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10628838/supplementaryFiles)
取得含两份补充 PDF 和正文两图的压缩包。期刊与 Europe PMC 的 Supplement 1 字节一致，
SHA256 `649131c38a9e37a2a35b3f6cdb89ec5d6697abd92f4a20774a5d07d94c8dec44`。
下载文件只在临时目录；仓库仅保存本技能用到的提取数字。

## 已打开的补充内容和列名

| PDF 页 | 内容 | 列名／核查结果 |
| --- | --- | --- |
| 3–11 | eMethods | 诊断、去重、APOE质控、祖源、年龄规则、logistic/Cox模型；未链接本研究成品代码 |
| 12–23 | eAppendix | 队列贡献、资助与数据源；不是模型系数文件 |
| 24–29 | eFigures 1–6 | 入组流程、祖源构成、OR/HR图；p.27 eFigure 4 已视觉检查，无逐点数值标注 |
| 30–31 | eTable 1 | Cohort/Study, Genotyping Platform, Cohort-Platform ID, Sample count, Data Repository |
| 32 | eTable 2 | Study, Accession Number, Related Datasets（NIAGADS NG00067 ADSP子项目） |
| 33 | eTable 3 | Group & APOE stratum, Diagnosis, Pathology, Sex, Age, Global Ancestry（EUR/AFR/AMR） |
| 34 | eTable 4 | Cohort-Platform ID；NHW/NHB/HISP各CN和AD人数 |
| 35 | eTable 5 | Cohort, Ascertainment design；NHW/NHB/HISP各CN和AD人数 |
| 36 | eTable 6 | Group/Model；EAS/NHW/NHB/HISP各No. carriers、OR (95% CI)、P-value；无年龄窗口列 |
| 37 | eTable 7 | Group/Model；Hispanic Whites/Blacks各No. carriers、OR (95% CI)、P-value |
| 38–39 | eTables 8–9 | 临床诊断限定／病理确认调整；各人群No. carriers、OR (95% CI)、P-value及组间P值 |
| 40–42 | eTables 10–12 | 招募设计限定／调整及剔除推断种族；相同OR列；敏感性分析不替换主表 |
| 43 | eTable 13 | Group/Model（剂量、基因型、性别及交互）；No. carriers、HR (95% CI)、P-value及组间P值 |
| 44–45 | eTables 14–15 | HISP或NHB内，EUR/AFR/AMR的<25、>25、>50、>75（部分>90）重叠阈值列；OR、CI及P值 |
| 46 | eTable 16 | Global Population Ancestry Proportion >75%；EUR/AFR/AMR各No. carriers、OR (95% CI)、P-value |
| 47–50 | eReferences | 方法和既往研究引用，不含额外结果附件 |

## 代码和原始数据

全文、两份补充文件、eMethods、eReferences 与期刊附件目录未列本研究的 GitHub、Zenodo、OSF
成品代码或可直接下载的模型结果文件，故无本研究仓库可克隆。引用 R、PLINK、SNPweights 等
是分析软件，不等于作者发布了回归模型。Supplement 2 写“Data available: No”，解释原数据
可向各仓库申请；eTables 1–2 列出 NIAGADS/DSS、dbGaP、NACC、Synapse、LONI ADNI、RADC、TARCC。
这些是受申请约束的个体数据来源，不是已发布的年龄风险查询表；本任务未申请、下载或再分析原始个体数据。
没有未下载而被误判为空的期刊补充文件。

## 提取方法

主表使用 PMC HTML 的表格行／列提取，跳过剂量、交互行；补表由 `pdftotext -layout`
提取对应页中的基因型行。保留每个输出单元格的原印文本，置信区间为有限数字时直接读取。
不从图像坐标重建值、不用人数估计风险、不纠正原数字的舍入。可查表数据在
`data/associations.json`，文件校验和登记于 `skill.json`。
