# 可行性与来源审计

核查日期：2026-11-25。流水线未提供本机缓存根目录。
通过 web-access 的静态网页/公开下载路径读取材料；浏览器 CDP 前置检查连接超时，
未使用登录态。公开全文和文件下载成功，没有把连接超时写成“论文未发表数据”。

## 出版物与全文

- [文章页](https://www.nature.com/articles/s44360-026-00139-5)：完整 Main、Results、Discussion、Methods、Data availability、Code availability、Competing interests 和附件链接。
- [正文 PDF](https://www.nature.com/articles/s44360-026-00139-5.pdf)：33 页（含正文、扩展材料和报告清单）；表 3 位于 p. 984。SHA-256：`6a70d48aed0772b5317f46da6827477b5c1405b0d0643492f9c2836ae1946948`。
- [表 2](https://www.nature.com/articles/s44360-026-00139-5/tables/2)：Health outcome、85th percentile risk level、RR (95% UI)、Exposure-averaged BPRF、Conservative interpretation、ROS、Star rating、Publication bias、No. of studies、Selected bias covariates。
- [表 3](https://www.nature.com/articles/s44360-026-00139-5/tables/3)：Health outcome；Number of standard drinks 的 1–10 列。每格是 mean RR (UI lower, UI upper)，脚注明确比较 current alcohol use 与 no alcohol use，并计入 between-study heterogeneity。HTML 与 PDF 的全部 600 个数字一致。
- 正文扩展表 1 是结局定义（Outcome、GBD Definition、ICD-10 codes），扩展表 2 是最低风险暴露水平与不饮酒等效点（Health outcome、TMREL (g/day)、NDE level (g/day)、Relative Risk at TMREL (95% CI)）。两张表的独立网页为图像，已渲染并读取 PDF 第 29、30 页。这些表不作为个人目标或建议；扩展表 2 在部分零 TMREL 结局印出 1.00 (1.00, 1.00)，本技能保持表 3 的来源范围，零参照不混入这些区间。
- [PubMed 42688145](https://pubmed.ncbi.nlm.nih.gov/42688145/) 确认 Nature Health 1(9):979–999，2026；开放全文另链接到 [PMC13533843](https://pmc.ncbi.nlm.nih.gov/articles/PMC13533843/)。Europe PMC DOI API 超时，未将其视为无文献记录。

## 两份补充文件均已下载并打开

[Supplementary Information](https://static-content.springer.com/esm/art%3A10.1038%2Fs44360-026-00139-5/MediaObjects/44360_2026_139_MOESM1_ESM.pdf)，
252 页，包含 Supplementary Methods、Tables 1–18、Figs. 1.01–1.16、2.01–2.20、3.01–3.20。
SHA-256：`234a897184327a34495d6aa0f30cab23d80628904c7c554aaf7ac9adc26bb280`。
下面页码按 PDF 文件从 1 开始，包含封面；文档自身页码可能少 1。

| 位置 | 实际内容与列 | 本实现用途 |
| --- | --- | --- |
| 表 S1，PDF p. 6 | 结局；Inclusion criteria；Exclusion criteria | 研究适用范围，不是个人诊断切点 |
| 表 S2，p. 7–8 | 数据库和基础检索式 | 检索方法核查 |
| 表 S3，p. 9–11 | 结局与 PubMed 检索式 | 同上 |
| 表 S4，p. 12–15 | 结局与 CINAHL 检索式 | 同上 |
| 表 S5，p. 16–18 | 结局与 EMBASE 检索式 | 同上 |
| 表 S6，p. 19–23 | 结局与 Web of Science 检索式 | 同上 |
| 表 S7，p. 24–27 | Outcome；Most recent high-quality systematic review；Start date of review；# underlying sources | 综述起点与搜索时间 |
| 图 1.01–1.16，p. 28–43 | PRISMA 筛选流程 | 研究级计数，不进入个人读出 |
| 表 S8，p. 45–51 | Category；Variable；Definition，包括 source、population、exposure、outcome、effect measure | 数据提取定义 |
| VII，p. 52 | 暴露单位处理、酒精度假设、密度、standard drink 与月转日 | 只核查定义；技能不做饮料体积换算 |
| VIII，p. 53–55 | BoP 六步法、样条、偏倚、异质性、BPRF | 明确平均 RR 与 BPRF 的区别 |
| 表 S9，p. 56–127 | Author；Year；Health outcome；Location；Study design；Sex；Age Start/End；Exposure/Outcome Assessment；Outcome type；Sample Size；Reference；Exposed group；Cases；Controls；Control Pool；Alcohol Type | 人群、病例与对照结构；不是一个去重后的总人数 |
| 表 S10，p. 128–180 | Author；Year；Health outcome；Sex；Reference；Exposed group；Natural Log of Effect；Standard Error of Natural Log of Effect；Covariates Adjusted for in Source | 原研究效应量，未用于重新拟合 |
| 表 S11，p. 181–204 | Author；Year；Study design；Health outcome；按研究列出的偏倚协变量（如 age、sex、incidence、hypertension、smoking 等） | 偏倚定义核查 |
| 表 S12，p. 205–206 | Health outcome；Spline degree, number of interior knots；Priors & constraints | 样条配置；本技能无需完整拟合系数 |
| 表 S13，p. 207 | Health outcome；Selected bias covariates；Gamma solution (mean and standard deviation) | 已选偏倚项与异质性参数；不作为个人系数 |
| 表 S14，p. 208–209 | Bias Covariate Name；Details | 协变量编码定义 |
| 图 2.01–2.20、3.01–3.20，p. 210–236 | 模型约束选择、无 trimming 的敏感性分析 | 不从曲线图读数或拟合新常数 |
| 表 S15，p. 237–239 | Health outcome；Number of standard drinks 1–10；RR 与 conventional 95% UI | 已读；区间不同于正文表 3，不能混用 |
| 表 S16，p. 240–242 | PRISMA Abstract：Section/Topic；Item #；Checklist item；Reported | 核实系统综述身份 |
| 表 S17，p. 243–249 | PRISMA manuscript：Section/Topic；Item #；Checklist item；Location | 同上 |
| 表 S18，p. 250–252 | GATHER：Item #；Checklist item；Reported on page # | 报告完整性清单 |

[Reporting Summary](https://static-content.springer.com/esm/art%3A10.1038%2Fs44360-026-00139-5/MediaObjects/44360_2026_139_MOESM2_ESM.pdf)，
3 页，是图像型 PDF；已渲染第 1 页并读取第 2–3 页 OCR。
说明没有新收集原始数据、研究数由文献筛选决定、随机化和盲法不适用。
SHA-256：`8ddbb1288fcf67a26e787116f61ab646bc25ca0078733a99a3b743bc4ab98389`。
其中另指向 `http://ghdx.healthdata.org/gbd/2023/data-sources`；访问 HTTPS 对应路径返回 404。
这是失效的目录路径，不意味着补充表或风险曲线数据缺失。
文章页没有列出另一份未下载的 xlsx、Zenodo 或 OSF 文件。

## 作者代码

已克隆 [ihmeuw-msca/burden-of-proof](https://github.com/ihmeuw-msca/burden-of-proof)，
审阅版本 `c8ad876a579cfd136850c13549aa706cd0fa2437`。
打开 README、`first_process` 结构、`risks/alcohol_ihd/tables.R` 等。
仓库包括 `limetr`、`mrtool`、通用拟合与后处理以及风险专用代码；
表格脚本从外部拟合结果目录读取 `summary.yaml`、`inner_quantiles.csv`、`outer_quantiles.csv`、原研究数据。
示例路径包含 `filepath`，没有执行作者完整训练流程，也没有宣称原样复现整篇荟萃分析。
本文印出的表 3 已足够实现查表，不需要用原研究数据重新估计参数。

## 作者释放的数据

已打开 [Burden of Proof visualization](https://vizhub.healthdata.org/burden-of-proof/) 的公开页面，
根据页面实际加载的 `dist/main-50cbea30eff511a849f9.js` 中公开请求定位其数据端点。
`metadata/risk` 中 High alcohol use 的 rei_id 为 102；`metadata/risk_cause` 列出 20 个结局。
已分别下载、解析这 20 个结局的 `output_data` 和 `study_citations`，共 40 个 JSON 响应：

- 结局 ID：297、322、444、450、411、414、441、417、456、423、429、438、493、495、496、500、521、535、543、976。
- 曲线端点：[output_data?risk=102&cause=493](https://vizhub.healthdata.org/burden-of-proof/api/v1/output_data?risk=102&cause=493)，其他结局替换 cause。
- 引用端点：[study_citations?risk=102&cause=493](https://vizhub.healthdata.org/burden-of-proof/api/v1/study_citations?risk=102&cause=493)，其他结局替换 cause。
- 每个曲线数据集有 151 个暴露行，risk 为 0–150；字段包括 risk、sex_name、age_group_name、location_name、log_cause 及上下限、linear_cause 及上下限、category_id。
- 引用数据包含 study_id、field_citation_value。文献引用数量不能等同正文研究数，可能存在分层或去重差别。
- 举例：缺血性心脏病 risk=10 行的 linear_cause 为 0.921741019993816，下限 0.806926978899007，上限 1.05289143894837，取两位小数与表 3 对应。这是来源核查，未成为实现常数。

数据端点先用 Python 默认网络路径访问时报 403；使用同一公开 URL 的 curl 下载成功。
因此没有把初次失败报告为不可获得。运行技能只使用固定表 3，不依赖动态平台或将平台上更密的点混入“印出查表值”。

## 冻结数据的许可与可行性结论

论文为 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，
`data/table3.csv` 是对 Dai 等 2026 表 3 的格式转换，增加机器键及克/日列，原数值未变；
来源与作者在本文件、manifest、报告卡片中保留。未复制整份下载材料入仓库。
本方法需要的全部平均 RR、UI 与摄入量节点已明确印出；没有必须猜测的系数、权重或切点。
可实现 Tier A，验证范围是复现印出表格，不是重跑 MR-BRT 或临床验证个人风险。
