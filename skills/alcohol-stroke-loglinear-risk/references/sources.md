# 来源和可行性审计（2026-11-26）

本次机器没有用户所指的图书馆缓存目录。没有将全文、PDF 或缓存复制进仓库。

| 材料/访问入口 | 结果及用途 |
| --- | --- |
| [DOI](https://doi.org/10.1016/S0140-6736(18)31772-0) 和 [Lancet 全文页](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(18)31772-0/fulltext) | 尝试打开，返回 403 |
| [PMC 文章页](https://pmc.ncbi.nlm.nih.gov/articles/PMC6497989/) | 公开全文索引可发现；当前直接页面触发验证码 |
| [Europe PMC 文章页](https://europepmc.org/articles/PMC6497989) | 页面访问失败，改用官方 API |
| [Europe PMC fullTextXML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6497989/fullTextXML) | 成功取得并阅读完整正文、表格、图注、利益冲突和补充材料清单；对应正式发表版本 |
| [Europe PMC supplementaryFiles](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6497989/supplementaryFiles) | 成功下载 ZIP，打开唯一补充 PDF mmc1.pdf，共 45 页；另含正文 Figure 1–5 的 jpg/gif 两种格式，不是额外补充数据表 |
| [PMC 附录原链接](https://pmc.ncbi.nlm.nih.gov/articles/instance/6497989/bin/mmc1.pdf) | 直接链接返回 HTML 而非 PDF，真正阅读的 PDF 来自上述官方 supplementaryFiles API |
| [Oxford ORA](https://ora.ox.ac.uk/objects/uuid:6c82d6de-fa90-42d6-ace8-aa0d7c3568ce) | 作者机构副本被检索发现，直接页面返回 403；未依赖它抽取系数 |
| [PubMed](https://pubmed.ncbi.nlm.nih.gov/30955975/) | 核对书目信息：2019 May 4，393(10183):1831–1842；PMID 30955975 |

Europe PMC core 元数据接口（query `EXT_ID:30955975 AND SRC:MED`）返回出版类型
`research-article`、`Journal Article`，`isOpenAccess=Y`，与原创研究一致。
实际阅读文件的 SHA-256：

- fullTextXML：`9f4e8323895beea173d9bb48385792f8152f1c6a6cec7232dce37c3326673c5f`
- mmc1.pdf：`fe028b78c7182ad8b7a446e60a2fc7cbb72f52dbebc18fff8a0dcb6f3fb1aa26`

全文 XML 将同一 mmc1.pdf 在两处列出，并非两份不同附录。
核查 Methods、附录方法和文末，没有作者指定的 GitHub、Zenodo、OSF 或其他公开代码/数据下载链接。
附录 p 6 列 SAS 9.3、R 3.2.1、CKB Data Release 14；未发布可直接重跑的个人记录。
本技能不需要个体训练数据，也不声称下载过它。

# 附录逐项定位

| 位置 | 材料与列/标注 | 与计算的关系 |
| --- | --- | --- |
| pp 4–6 | Supplementary Methods：饮酒频率、酒种及体积分数；疾病定义；样本筛选；每 100/280 g/周 log RR 缩放 | 方法和适用范围；缺密度，所以不做体积转克数 |
| p 7 | Text-Table 1：ALDH2/ADH1B、酶、功能、SNP、碱基及氨基酸改变、代谢和饮酒量方向 | 背景，无个人基因权重 |
| p 8 | Webfigure 1：全部、随机基因样本、额外病例、生化子样本男女计数 | 样本审计 |
| p 9 | Webtable 1：基线饮酒组、N、%、基线均量；两次重测 N、均量及平均 usual intake | 群体复测校正，不作个人查表 |
| p 10 | Webtable 2：男女饮酒组、N、地区、年龄、教育收入、吸烟、健康史 | 队列背景 |
| p 11 | Webtable 3：主要酒种、男女饮酒比例、平均 g/周 | 不作为用户酒精度或杯大小 |
| p 12 | Webtable 4：地区、N、各饮酒状态%、当前饮酒者及全体平均 g/周 | 暴露背景 |
| p 13 | Webtable 5：地区、分型人数、两个位点 A 等位基因频率 | 不作个人评分 |
| p 14 | Webtable 6：总体/基因子集、各位点 AA/AG/GG、饮酒指标及每等位基因趋势 P | 不作个人评分 |
| p 15 | Webtable 7：九种联合基因型 × 地区、男女平均 g/周及 C1–C6 | 解释分组依赖地区，不按个人基因分配摄入量 |
| pp 16、18 | Text-Figures 1–2：地区/基因型摄入量、分组切点、饮酒比例和均量 | 研究图示 |
| p 17 | Webtable 8：C1–C6 及 C1–C3、人数、饮酒状态、均量 | 群体分组 |
| p 19 | Webtable 9：全体/基因子集和 C1–C6 基线特征、趋势 P | 混杂核查 |
| pp 20–21 | Text-Figure 3、Webtable 10：传统/遗传 N，生理指标 slope (95% CI) per 280 g/week、P | 不输出个人血压或生化变化 |
| p 22 | Text-Figure 4：传统/遗传卒中图，RR、CI、事件数、每 280 g/周注释 | 与正文 Figure 4 一致 |
| pp 23–24 | Webtable 11：男女、多个传统模型、饮酒组；三类卒中 N events、RR (95% CI) | 不采用传统 U 形分组进行目标选择 |
| p 25 | Webtable 12：Men Model 1/2、Women Model 1；C1–C6；三类卒中 N events、RR (95% CI)；每 280 g/周总结行 | 唯一数值系数来源：Men Model 1 |
| p 26 | Webtable 13：C1–C3 与 C4–C5 的事件数、平均摄入量、率比 | 分类比较，不当作拟合直线的预测值 |
| pp 27–29 | Webfigures 2–4：分地区 SBP、总卒中，分年龄饮酒比例及均量 | 稳健性和背景 |
| p 30 | Webtable 14：年龄组；传统/遗传 N、slope 或 RR (95% CI)、P | 不据此拼接个人年龄系数 |
| pp 31–33 | Text-Figure 5、Webtable 15：冠心病传统模型，急性心梗和总冠心病 N、RR (95% CI) | 不输出心脏保护判断 |
| p 34 | Webtable 16：男女遗传模型、C1–C6、心梗/冠心病 N、RR (95% CI) | 未进入个人计算 |
| p 35 | Text-Table 2：男女生理指标均值及疾病 RR，按男性均量缩放的效应和 CI | 与正文 Table 2 对照；不把女性行作饮酒量斜率 |
| pp 36–37 | Webtable 17、Webfigure 5：单个位点、生理指标 GG vs AG 差、SE、每 G 等位基因趋势、P | 单位点敏感性分析 |
| pp 38–40 | Webtable 18、Webfigures 6–7：男女位点基因型、疾病事件数、RR (95% CI) | 非本技能模型 |
| pp 41–45 | Webfigures 8–12：观察结果、假定适量饮酒保护/不保护下的预期遗传结果 | 假设检验，不用图中假设曲线反推常数 |

可行性结论：三个 RR、六个区间端点、280 g/周缩放量及 log-linear 关系全部公开印出。
正文另印每 100 g/周结果，提供独立的缩放验证；无需猜测权重、截距或基线生存率。
绝对个人风险不可算，因为所选发表结果没有个人预测所需的基线危险函数和完整个人预后方程。
