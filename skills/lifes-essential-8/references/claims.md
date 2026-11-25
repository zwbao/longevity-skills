# 来源核查

研究设计：Lloyd-Jones 等的 AHA Presidential Advisory，Circulation 2022;146(5):e18–e43。本文由专家组整合人体证据，以修改Delphi法更新评分构造；不把其当作新队列预测模型或随机试验。PubMed编号35766027；Europe PMC核心记录的pubTypeList为research-article、Review、Journal Article，已核对其包含Review类型。因此不称其为新的原创队列研究；manifest使用consensus以准确表达已读取全文中的AHA专家咨询及评分更新属性。

全部样本组：本咨询文件没有新招募的病例、对照、推导或验证队列及其样本量。正文借助近期NHANES分布制定分档，引用多个既有研究；这些并非本技能的训练样本。附录是示例人物，不是真实验证队列。

物种：人（human / Homo sapiens）；本文讨论人类全生命历程健康构造，没有本论文新做的动物或细胞实验。

利益冲突：已读全文Writing Group Disclosures和Reviewer Disclosures。Anderson披露WW及McCormick Science Foundation顾问关系；Allen披露NIH/AHA研究资助；Brewer披露AHA、NIH、CDC、ACC支持及专业组织/期刊职务；Foraker披露NIH/NCI资助；Lavretsky披露NIH、PCORI、NCCIH资助；Perak披露NHLBI和Northwestern资助。其余写作组成员表中其他经济关系栏为None；全组ownership interest及expert witness均为None。审稿人Johnson、Palaniappan、Van Horn披露NIH/NHLBI或NIH资助；其他审稿人相应栏为None。不能归纳为全体无利益冲突。

| 论文声称什么 | 原文/补充表实际有什么 | 发布代码实际算什么 | 同名或相近项目的区别 |
|---|---|---|---|
| 更新人体心血管健康构造 | Table 1成人/儿童八项分档，实施注释及总体均值定义 | 本文没有链接专用算法代码仓库或数据发行版 | Life’s Simple 7是旧构造，不等同LE8 |
| 饮食评估可面向个人或人群 | Appendix 1 Table A：Domain、CVH Metric、Method of Measurement、成人/儿童Quantification；Table B：Component、Foods、Scoring Criteria、Note；Table C：Screener Item、Question、Scoring Criteria、Score | 本技能只转换已计分成人MEPA总分 | 不把MEDAS、DASH原始分或饮食分位数当MEPA |
| 可扩展至儿童与婴幼儿 | Appendix 2含饮食、活动、体重的年龄分组建议及测量限制 | 本技能成人限定，不执行儿童评分 | 其他研究自定义NHANES代理变量不混入本实现 |
| 八项可汇总并追踪 | Appendix 3 Examples 1–4提供输入、Metric/Points与Sum、总分 | 本实现复现成人Examples 1、3、4；未复现儿童Example 2 | 后续LE8风险关联研究并非此评分的个人风险公式 |

## 可行性与访问记录（2026-11-25）

未提供本机订阅缓存路径。先访问AHA文章页及补充页，遭403/访问限制；PMC普通页遇验证码，但[PMC作者接受稿全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC10503546/?report=classic)经HTTP读取成功，核对正文、Tables 1–3、图注、披露与附录链接。PMC仅列一份附件NIHMS1913084-supplement-Supplemental_File.pdf；其下载地址遇验证码，不能称为已下载成功。Europe PMC文章、全文XML和附件接口未成功；OpenAlex返回PMC及UNC DOI 10.17615/wpxv-6b42，UNC访问超时。AHA/ADA Know Diabetes by Heart全文副本未下载成功。浏览器代理连接不可用。

最终通过[出版商LWW托管的原始Supplementary Materials镜像](https://cdn-links.lww.com/permalink/jcn/a/jcn_00_00_2022_08_26_hayman_jcn-d-22-00197_sdc1.pdf)在网页阅读工具中打开完整18页PDF，题名、作者页眉和AHA 2022版权均与目标论文一致；已核对Appendix 1（Tables A–C）、Appendix 2（年龄分组建议）、Appendix 3（Examples 1–4）及参考文献。该地址属于Journal of Cardiovascular Nursing的附件路径，托管的是目标论文原始附件，不将其误认作Circulation原始下载URL。另一2024 LWW附件路径访问失败。检索曾出现Scribd转存，未将其作为评分或验证的证据来源。没有把抓取全文或原PDF复制入仓库，只记录必要方法事实与短验证引文。

全文和附件没有点名GitHub、Zenodo或OSF的本研究代码/数据发布；引用的NHANES是人群饮食分位数分支的数据源，本技能不用该分支。本实现需要的成人分档、扣分、加权方式和验证例均已在上述正文及附件找到，未从记忆或第三方输出推断模型常数。
