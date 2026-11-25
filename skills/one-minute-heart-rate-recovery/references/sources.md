# 材料与可行性审计

核查日期：2026-11-25。DOI：10.1056/nejm199910283411804。本次任务明确表示本机无图书馆缓存，未复制缓存或全文进仓库。

| 来源 | 实际访问结果 |
|---|---|
| [NEJM文章页](https://www.nejm.org/doi/full/10.1056/NEJM199910283411804)；同DOI短路径、带articleTools参数的页面 | 已尝试打开；403或无法访问，不能检查当前网页附件区 |
| [NEJM正式PDF](https://www.nejm.org/doi/pdf/10.1056/NEJM199910283411804?articleTools=true) | 搜索引擎可索引正文，直接打开及下载受403限制 |
| [The Heart Center公开的正式PDF副本](https://thcabq.com/wp-content/uploads/2019/11/HEART-RATE-RECOVERY-IMMEDIATELY-AFTER-EXERCISE-AS-A-PREDICTOR-1.pdf) | 成功下载并阅读全文7页（1351–1357），包括Table 1–3、Figure 1–2及参考文献；PDF保留NEJM原始版式及版权信息。仅保存在临时目录，不再分发 |
| [PubMed](https://pubmed.ncbi.nlm.nih.gov/10536127/) 与 [Europe PMC](https://europepmc.org/article/MED/10536127) | 常规网页读取受限；Europe PMC REST core记录可读，出版类型为Journal Article、inPMC=N，没有PMC全文编号 |
| [OpenAlex DOI记录](https://api.openalex.org/works/https://doi.org/10.1056/nejm199910283411804) | 成功读取；列出NEJM正式PDF、PubMed及历史CiteSeerX条目，没有列出开放仓储正式全文 |
| web-access浏览器后备路径 | Node与Chrome端口检查通过，但CDP连接超时；没有通过浏览器读取出版社页，未改变用户标签页 |

**补充材料、代码、数据**：逐页检查正式全文，未点名Supplementary Table、Appendix、eMethods或外置材料；“supplementary multivariable Cox regression analyses”是正文描述的附加统计分析，不是一个被链接的文件。全文仅注明SAS版本，没有GitHub、Zenodo、OSF或其他公开代码/数据发布链接。另按DOI查找supplement、appendix、GitHub，未发现本文的可确认附件或仓库。出版社附件区未能核查，故不声称其当前确实为空；没有已发现但未下载的具体附件链接。`paper.supplements=[]`仅表示没有实际使用的附件，不代表证明不存在附件。

**可行性结论（编码前）**：只计算主切点下的个人HRR差值与分档；需要的全部数学定义和阈值已印在完整正文，均能定位，无需未公开系数。没有可复现的个人数值示例，按流水线规则继续创建Tier A暂定技能。完整多变量绝对风险模型不在合同内。
