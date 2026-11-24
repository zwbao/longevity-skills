# 证据与材料核查

## 研究设计和人群

这是 GBD 2021 的原创比较风险评估与综合建模研究（PubMed PMID 38762324；不是个人预测方程的独立验证队列），清单用 `method` 表达研究设计。研究期 1990–2021，涵盖 204 个国家和地区、811 个次国家地点、88 项风险和 631 个风险–结局组合，使用 54,561 个不同资料源。相对风险资料源 3,359 个、暴露资料源 51,337 个，存在重复，不能相加当作人数。研究包含男女和不同年龄组，并无统一的病例、对照、推导及验证人数；不要把全球人口或资料源数说成样本人数。

收缩压子分析：附录 1 印刷页 268 表 1（列 `Countries with data | New sources | Total sources`）为暴露资料 166 个国家、9 个新资料源、1,116 个总资料源；页 270 表 3（同列名）为相对风险资料 67 个新资料源、70 个总资料源，国家数 NA。它综合队列与随机试验，不是本技能开展的临床试验。

物种：人（human；Homo sapiens）。没有以动物或细胞实验作为此个人读出的参数来源。

资助：正文列 Bill & Melinda Gates Foundation；资助方未参与设计、数据收集分析解释、撰稿或投稿决定。

利益冲突：已读正文 Declaration of interests，存在多位作者披露，不能写“无利益冲突”。例如 A E Schutte 披露 Abbott、Medtronic、Servier、Skylabs 咨询，以及包括 Aktiia、Omron 等公司的讲课等报酬和相关学术团体职务；A Rane 披露作为 Agios 全职员工持有股票或期权；其他作者还有专利、药企资助及咨询关系，多标为研究之外。其余作者声明无利益冲突。详见原文完整披露，本技能不推销任何设备或治疗。

## 结论对照

| 论文声称什么 | 补充表实际有什么 | 代码仓库实际算什么 | 同名的另一个项目是什么 |
|---|---|---|---|
| TMREL 是群体风险归因的反事实暴露参照，并对不确定性建模 | 附录 1 表 S9 页 513，列 Risk Name、2019 TMREL range、2021 TMREL range；收缩压 2021 列为 105–115 mmHg | 论文原代码入口现重定向，未取得可克隆仓库；本地脚本只比较两个端点 | GBD 2019 的 110–115 mmHg 不是本技能采用的 2021 区间 |
| 收缩压 TMREL 以均匀分布表示，归因负担计算时抽样 | 附录 1 页 278–279 给出选取百分位的规则和两个端点 | 未声称复现 RR、SEV、PAF 或 DALY | Burden of Proof 的风险曲线和星级不是个人风险概率，也不是这个固定区间比较 |
| 全球危险因素负担随时间与人口变化 | 附录 2 提供结果图及表 S1–S6 的说明，详细表另托管于 GHDx | 没有把人群负担乘到个人测量上 | 其他年份 GBD 更新不能替换本文参数 |

## 原始来源与访问记录（2026-11-25）

- [出版社全文页](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(24)00933-4/fulltext)：已尝试，403；DOI 跳转同样受限。PMC 网页遇浏览器验证。
- [Europe PMC 全文 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11120204/fullTextXML)：已下载并读正文、方法、讨论、披露及所有 supplementary-material 链接；列出 mmc1.pdf、mmc2.pdf、mmc3.pdf。
- [White Rose 大学存档的出版版 PDF](https://eprints.whiterose.ac.uk/216064/1/1-s2.0-S0140673624009334-main.pdf)：已下载并提取文本，与该 DOI 一致。
- [附录 1 mmc1.pdf](https://ars.els-cdn.com/content/image/1-s2.0-S0140673624009334-mmc1.pdf)：已下载、提取全文，查阅目录和 TMREL、收缩压章节及表 S9，并查看表 S9 页图。其表 S1–S9 均在该 PDF 内；包括风险层级、比较风险评估定义、GATHER 清单、地域层级、SDI、介导矩阵、风险–结局变化及 TMREL。未将 500 多页全部当作个人算法参数。
- [附录 2 mmc2.pdf](https://ars.els-cdn.com/content/image/1-s2.0-S0140673624009334-mmc2.pdf)：已下载并查阅；含结果图 S1–S4，表 S1–S6 指向 GHDx。S1/S2 是归因死亡、DALY 和 PAF；S3 是 SEV；S4 是联合 PAF；S5 是选定结局的 RR；S6 是风险–结局评分与 DALY。它们不构成个人 SBP 差值示例。
- [附录 3 mmc3.pdf](https://ars.els-cdn.com/content/image/1-s2.0-S0140673624009334-mmc3.pdf)：已下载并查阅；为作者、单位及贡献。
- [GHDx 数据发布页](https://ghdx.healthdata.org/record/ihme-data/gbd-2021-burden-by-risk-1990-2021)：直接请求可读。公开文件列 Data Release Information Sheet、Supplementary Results Appendix、Table Index [CSV]（实际文件名 IHME_GBD_2021_RISK_1990_2021_TABLE_INDEX_Y2024M05D14.XLSX）；链接均指向 download-access/login。未下载信息表及表索引，也未取得其额外表格；结果附录已从出版社取得。不可将需要登录的文件写成“没有数据”。
- [代码旧入口](http://ghdx.healthdata.org/gbd-2021/code)及 [Methods Web Portal](https://www.healthdata.org/gbd/methods-appendices-2021)：当前均重定向到 IHME data-access 说明页，没有得到可克隆仓库地址，未声称审计作者代码。
- [Burden of Proof](https://vizhub.healthdata.org/burden-of-proof/)：已打开应用入口，未取得可用于独立个人示例的静态表；没有拟合其输出。
- [2024 更正全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC11457227/)（DOI 10.1016/S0140-6736(24)01458-2）：已读取，修正的是图 7 风险类别图例颜色，在线版于 2024-07-18 更新；更正未涉及表 S9 的收缩压端点。PubMed 页面及 Europe PMC XML 初次访问未返回正文，最终通过 PMC 网页核实。

所有全文与附件保存在仓库外的临时目录，未复制入技能。唯一计算常数为表 S9 的两个端点，材料已足够完成该算术比较；对于打不开的额外表格与代码，访问限制均保留，不推断其内容。
