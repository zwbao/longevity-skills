# 材料清单及参数出处

核对日期：2026-11-25。机器上无用户所述图书馆缓存；从公开出版社下载。原始全文、PDF、临时OCR和代码克隆仅放在/tmp，未复制入仓库。

## 已打开的材料

1. [出版社文章页及全文](https://www.nature.com/articles/s41591-022-01978-x)：直接HTTP成功取得完整正文、Methods、数据/代码声明、扩展数据、利益冲突。检索工具的Nature打开曾因idp重定向失败，未将其误判为无全文。
2. [PMC全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC9556318/)：首次地址出现浏览器校验，后通过`/articles/9556318/`入口取得全文，用于交叉确认题录和开放许可。
3. [Table 1](https://www.nature.com/articles/s41591-022-01978-x/tables/1)：Background / Main findings and limitations / Policy implications；其分级计数与结果正文不一致，见claims.md。
4. [Table 2](https://www.nature.com/articles/s41591-022-01978-x/tables/2)：全36行和脚注已打开，计算使用它的印出数值，原始单元格与解析数据一同存入data/table2.json。
5. [Supplementary Information，MOESM1](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-022-01978-x/MediaObjects/41591_2022_1978_MOESM1_ESM.pdf)：302页PDF，已下载并提取文本，目录包含9节。所有补充表均在这一文件内，没有另列xlsx。
6. [Reporting summary，MOESM2](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-022-01978-x/MediaObjects/41591_2022_1978_MOESM2_ESM.pdf)：3页，文本提取为空，逐页渲染后OCR读取研究设计、软件、性别及资料可用性声明。
7. [作者代码](https://github.com/ihmeuw-msca/burden-of-proof)：已克隆，检查README、risks/smoking/config.R、连续风险抽样和年龄调整代码；快照提交`c8ad876a579cfd136850c13549aa706cd0fa2437`。脚本读取外部模型和抽样输出；本技能没有运行作者完整拟合流程，也不需要这些文件来查表2。
8. [VizHub](https://vizhub.healthdata.org/burden-of-proof/)：已打开主页面及其公开数据接口，风险字典中Smoking为99，肺癌结局为426。[肺癌输出数据](https://vizhub.healthdata.org/burden-of-proof/api/v1/output_data?risk=99&cause=426)有100个曲线点，[引用数据](https://vizhub.healthdata.org/burden-of-proof/api/v1/study_citations?risk=99&cause=426)有78项。公开数据并非不存在，但本技能只使用出版时表2冻结值，未复制该实时曲线为2022年预测。
9. [Europe PMC题录](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41591-022-01978-x&format=json&resultType=core)：确认卷28期10、2022年及出版类型。没有调用第三方计算器或使用预印本替代出版版。

出版社页面所列两份补充文件均已成功取得；没有已列出但未下载的补充材料。CDP连接检查超时，未操作用户浏览器；公开HTTP途径已足够读取全部所需材料。

## 表格字段核对

页码均为MOESM1 PDF物理页（含封面），不是正文页码。

| 材料/定位 | 打开的字段 | 本技能用途 |
|---|---|---|
| 正文Table 2 | Risk–outcome pair; Risk unit; Mean risk at different exposure levels: 5, 10, 20, 40; 85th percentile risk level; Mean risk at 85th percentile risk level; ROSs; Average BPRF; Average increased risk (%); Star rating; Pub. bias; No. of studies | 冻结RR、UI、暴露点、年龄标签、星级和偏倚标记；ROS及平均BPRF保留在原始单元格，不当作个人结果 |
| 补充表1，PDF6页起 | Cause Name; Definition | 36个终点定义 |
| 补充表2，PDF8页起 | Extracted variable (column name); Extraction guidance provided；包括risk、outcome、location、exposure和效应字段 | 数据提取模板，不是模型系数 |
| 补充表3，PDF46页起 | Cause; NID; Underlying NID; Author; Year; Study name; Population; Location; Study design; Sex; Follow-up; Age start/end; Exposure assessment; Endpoint; Disease ascertainment; Person-years; Events; Sample size; Outcomes; Cases; Controls; Control pool; Exposed | 研究级病例、对照和样本组信息，不相加成独立队列人数 |
| 补充表4，PDF174页起 | NID; Cause; Author; Year; Study design; Location; cv_adj_L0/L1/L2; cv_exposure_study; cv_older; cv_subpopulation | 研究偏倚编码，不把它们当个人测量 |
| 补充表5，PDF205页 | Total unique sources; Total sources; Total observations；Dose-response risk及Age pattern of risk for CVD outcomes | 研究/观察计数，和正文总研究数不混用 |
| 补充表6，PDF206页起 | Risk-outcome; Type of risk; Spline degree, # interior knots; Priors & constraints | 建模规格，不是全部拟合样条权重 |
| 补充表7，PDF208页起 | Risk-outcome; Unit of risk; Selected bias covariates; Mean gamma solution | 风险单位和异质性参数，不作个人偏倚校正 |
| 补充表8，PDF234页起 | Cause; NID; Outlier flag; Reference exposure; Alternative exposure; Log relative risk; Log standard error | 原始研究级观察，不能当作重估后的个人查表值 |
| 补充表9–11，PDF297页起 | PRISMA Manuscript Checklist、PRISMA Abstract Checklist、GATHER Checklist：Item、Checklist item及Location等列 | 报告规范定位，无个人预测参数 |
| 补充第4节，PDF195页起 | 各结局dose-response曲线及95%UI | 核对单位及整体关系，不从图形采样重建数值 |
| 补充第5节，PDF204页起 | 方法；5.2.2年龄风险、衰减因子及年龄分层图 | 年龄调整是逐抽样进行，不拿图估算年龄因子 |
| 补充第6–7节，PDF213、232页起 | 裁剪/单调性敏感性图；骨折funnel和forest图 | 区分敏感性结果与表2最终值 |

## 冻结与再分发

表格数值由出版社HTML单元格提取，使用列顺序和每行14单元格的检查防止错位；中文名及稳定键是本技能新增的映射。两个重复的第85百分位点与已有暴露点比对一致后去重，其余数值保留原样。数据文件SHA-256在skill.json登记。

原文授权为[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。归属：Dai等，Health effects associated with smoking: a Burden of Proof study，Nature Medicine 28:2045–2055（2022），DOI10.1038/s41591-022-01978-x。冻结文件是表2的结构化改写，包含新增中文标签；未改动印出的RR/UI。
