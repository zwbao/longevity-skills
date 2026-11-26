# 来源与可行性审计

核查日期：2026-11-26。机器没有用户所述浙江大学缓存目录；未复制缓存全文到仓库。全文与附件只下载到 /tmp，仓库仅保存方法、引用和查表常数。

## 已打开并阅读

- [期刊文章页](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2802963)：全文、表 1–4、图、两份补充文件链接和更正链接。
- [Europe PMC 完整 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10066463/fullTextXML)：全文与表格及脚注；直接 PMC 网页返回浏览器验证，因此用这份官方全文交叉核对。
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/37000449/) 和 Europe PMC DOI 检索：出版类型、作者、卷期年。
- [更正通知](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2804662)：Errors in Figure and Supplement，2023-05-09，图和附件的 95% CI 更正。
- Supplement 1：期刊页面文件名 `zoi230209supp1_prod_1683218447.99118.pdf`，21 页。读取所有文本页并渲染 eFigures 2–4（p16–18）及空白 p20。eFigure 1 p14 流程图文字可提取。
- Supplement 2：`zoi230209supp2_prod_1683218448.00616.pdf`，1 页，数据共享声明。

期刊附件地址（下载时须使用文章页提供的完整签名链接，静态裸链接可能 403）：

- https://cdn.jamanetwork.com/ama/content_public/journal/jamanetworkopen/939092/zoi230209supp1_prod_1683218447.99118.pdf
- https://cdn.jamanetwork.com/ama/content_public/journal/jamanetworkopen/939092/zoi230209supp2_prod_1683218448.00616.pdf

PMC 对应文件名为 jamanetwopen-e236185-s001.pdf / s002.pdf。manifest 保留稳定 PMC 地址，实际阅读副本来自期刊签名链接。裸 CDN 和 PMC 附件地址访问失败，Europe PMC supplementaryFiles 下载超时，随后完整签名 CDN 链接成功；没有把访问失败当作附件为空。

## 表格列及使用范围

| 定位 | 列名/内容 | 使用 |
|---|---|---|
| 正文表 1 | Covariates；Studies, No. (%)；No. of RRs (%)；Mean RR (95% CI)；P value | 研究背景，非个人模型 |
| 正文表 2 | Drinking categories；Studies, No./risk estimates, No.；Unadjusted/Partially adjusted/Fully adjusted 各自的 RR (95% CI)、P value | 仅 lifetime nondrinker 参照的 Fully adjusted RR/CI |
| 正文表 3 | Drinking categories by median age at enrollment；Studies/risk estimates；三套调整模型 RR/CI/P | 核对但不按个人年龄选用 |
| 正文表 4 | 男/女分组的 Drinking categories；Studies/risk estimates；三套调整模型 RR/CI/P | 仅 Fully adjusted RR/CI；表头残留 by median age，按实际 Men/Women 分组解释 |
| Supplement 1 eTable 1，p15 | Year、Author、Sex、Country、No. of deaths、No. of subjects、Age range、Follow-up year、Covariates assessed | 新增研究背景 |
| eTable 2，p19 | Drinking categories、N/n、Egger Coefficient/ttest P、P (Q statistic)、I² (%,95% CI) | 偏倚及异质性；同时核对分档边界 |
| eTable 3，p21 | Drinking categories、N/n、Unadjusted/Partially-adjusted/Fully-adjusted 的 RR、95% CI、ttest P | 年龄设计敏感性分析，不作为个人模型 |
| Supplement 2，p1 | Data；Data available: No | 明示原始数据不开放 |

## 访问未成功的预注册

[OSF tnhd3](https://osf.io/tnhd3/) 在正文及 eReferences 2 被称为 protocol。页面、api.osf.io/v2/nodes/tnhd3/、registrations 端点及 OSF v1 project 端点均返回 403；Jina 页面副本为空，API 副本返回 500；CDP 依赖检查检测到 Chrome 但连接授权超时。因此**没有读到 OSF 协议或文件清单**，也不能声称 OSF 不含其他文件。本文和已打开附件没有点名其他 GitHub、Zenodo 或结果代码/数据发布地址；Supplement 2 直接说明数据不开放。

这不影响本技能有限的查表可行性：它不依赖 OSF 或重拟合所需权重，所有使用的区间、RR、CI 都已在完整正文印出。若后续要重现元分析拟合或扩展个体风险模型，必须另行取得原始数据/代码，当前未完成此类复现。
