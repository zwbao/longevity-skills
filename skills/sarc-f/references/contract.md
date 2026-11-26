# 产品合同与可行性审计

1. 用户提供自己的四项日常功能困难回答（按题意编码0、1、2），以及过去一年实际跌倒次数；年龄和性别可选，不参与计分。
2. 技能维护者从原始论文正文和表1核对并冻结规则；个人运行无需下载公开数据，不向用户索要论文、补充材料或队列。
3. 报告只给五个单项分、总分及是否达到筛查界值；不确诊、不估计患病概率、肌肉量或寿命，也不推算改变回答后的治疗获益。

## 重新判断原先拒收原因

此前登记仅因文章类型为社论而拒收，并非已发现计算常数缺失。按修订标准，本篇在表1完整提出可用个人回答计算的问卷方法，因此定为A。PubMed明确标为Editorial；manifest用method描述其可计算的方法贡献，不将其冒充完整队列验证。

## 获取记录（2026-11-26）

- 用户说明本机没有浙大全文缓存目录，故未假定存在缓存，也未将全文文件加入仓库。
- [DOI](https://doi.org/10.1016/j.jamda.2013.05.018)、[JAMDA文章页](https://www.jamda.com/article/S1525-8610(13)00303-4/fulltext)和[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1525861013003034)：网页访问返回403；浏览器CDP依赖检查连接超时，未获取网页的附件列表。
- [Crossref元数据](https://api.crossref.org/works/10.1016/j.jamda.2013.05.018)可读，确认作者、题名、PII和DOI，没有关联补充材料条目。[Elsevier XML接口](https://api.elsevier.com/content/article/PII:S1525861013003034?httpAccept=text/xml)返回200但只有元数据，没有正文或附件列表，未将其当作全文。
- [PubMed PMID 23810110](https://pubmed.ncbi.nlm.nih.gov/23810110/)可读，核对出版类型、2013年14卷8期531–532页和作者。Europe PMC REST请求超时，未取得额外材料。
- [作者ResearchGate文章页](https://www.researchgate.net/publication/243966215_SARC-F_A_Simple_Questionnaire_to_Rapidly_Diagnose_Sarcopenia)可读全文。[公开PDF副本](https://fitgreystrong.com/wp-content/uploads/2019/12/Malmstrom-Edit-SARC-F-questionnaireJAMDAAug2013.pdf)含ResearchGate封面，标明由John E Morley于2016-07-27上传；已读全部三页（封面加正文531–532页），并查看531页表格图像核对等号和区间。
- 全文只有表1，列名为Component、Question、Scoring；未点名Supplementary Tables、Appendix、eMethods、代码仓库或数据下载。以DOI加supplement/code/data/GitHub/Zenodo/OSF检索未发现该文新增配套文件。没有已发现但未下载的附件；出版社附件列表仍未独立核实，不能据此断言出版社绝无附件。实现所需全部常数已在已读原始全文中，不依赖任何未打开材料。

## 常数的出处

| 量 | 原文位置 | 本实现 |
| --- | --- | --- |
| 四项困难回答各0/1/2 | p.531表1前四行 | 保留各行题意；步行使用辅助器具归2；起身很困难或无法独立完成归2 |
| 提物重量10磅，上楼10级 | p.531表1题干 | 保留原题；10磅约4.54千克仅为说明（精确国际磅换算为0.45359237 kg/lb），不是新增测量输入 |
| 跌倒0次、1–3次、≥4次对应0/1/2 | p.531表1最后一行 | `falls_points`，输入过去一年实际次数 |
| 总分0–10，五项各0–2 | p.531正文第三段 | 相加，不加年龄、性别权重 |
| 总分≥4界值 | p.531正文第三段 | `classify`，等号归达到界值 |

跌倒次数0–1000、成人年龄18–120为应用层输入检查范围，不作为研究人群或临床阈值。计数与得分不做单位互换；没有其他可换算的量纲，也未猜测LOINC。中文题意为说明性翻译，未做独立语言学验证。

## 复现与限制

在实现计分脚本之前先写 `tests/test_manifest.py::test_table1_falls_per_term_scores`，逐项断言表1明确印出的0、1、2分及对应跌倒条件，整数要求完全相等，无拟合或反推。`validation.quote`抄表格的Scoring单元格，以换行连接；视觉核对原PDF中的“1–3”和“=”（自动文本提取曾将它们误读）。

集成测试另核对正文印出的总分端点0和10、界值4及其以下分层；这些是规则边界测试，不声称论文有这样的完整患者病例。原文没有印出完整个人算例，也没有初步研究样本量、系数、风险概率、敏感度或特异度；本技能的reproduced只指单项计分复现，不代表临床效能得到复现。

这是对回答进行汇总的筛查问卷，不是可设干预目标的风险方程或时钟，故不提供targets/levers。改善编码不等同于已证明降低患病概率。
