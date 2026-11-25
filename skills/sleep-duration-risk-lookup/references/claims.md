# 文献核查

研究设计：前瞻性队列的系统综述和剂量反应荟萃分析；Europe PMC 的 PMID 28889101 条目列出 meta-analysis、systematic review、review-article，故 manifest.evidence = review。不是随机试验，不是独立个人风险预测模型的推导和外部验证。

全部样本组：正文 Results / Literature Search 和 Study Characteristics 报告 67 篇文章、141 个按结局／性别拆分的报告，合计 3,582,016 名参与者。全因死亡：43 篇、57 报告、241,107 例；总 CVD：26 篇、37 报告、58,919 例；CHD：22 篇、27 报告、22,511 例；卒中：16 篇、20 报告、15,476 例。各结局及性别报告可能源于同一队列，不能将这些报告当作独立人群再次相加。单研究样本 724–1,116,936，随访 2.3–34 年。欧洲 22 篇、美国 16 篇、亚洲 27 篇、澳大利亚 2 篇。没有单独的训练、对照或验证队列；各研究睡眠参考组及调整变量列于表 S1–S4。表 2 的样本标记另指 40、26、20、17 个风险估计，不能替代上述总人数。

物种：人（human / Humans）；本文没有动物或细胞实验。讨论引用的机制研究不计为本文实验物种。

利益冲突：正文 Disclosures 为 “None.”。资助包括中国国家自然科学基金（81472978）、国家科技支撑计划（2012BAI02B02）、中国博士后科学基金（2016M602314）及同济医学院重大人类疾病创新团队项目；正文声明资助方未参与设计、收集分析、发表决定和写作。未披露本文工具或干预相关的商业雇佣或专利。

| 论文声称什么 | 补充表里实际有什么 | 作者代码仓库实际算什么 | 同名或相近项目是什么 |
|---|---|---|---|
| 非线性关联的选定小时点预测 RR 见正文表 2；参照为 7 小时 | S1–S4 是原始队列特征、睡眠分组、调整 RR 与协变量，不是本技能的另一个系数来源 | 正文只说明使用 Stata 12；正文及完整补充材料未列作者代码仓库或释放数据仓库链接 | 与 sleep-study-life-expectancy 的睡眠年龄输出无关，不能互换 |
| 观察到短睡眠与长睡眠两侧的人群关联 | S9–S12 是分层的每小时趋势；S7–S11 为夜间/全天、结局、地区和随访时长的分层曲线 | 没有可供本实现调用的作者程序；本技能只查正文表 2 | 不把 sleep-chart-biological-ageing 的年龄分组或其他睡眠评分当作本文方法 |
| 结局分析和异质性、偏倚与敏感性分析 | S5–S8 是 NOS 质量评价；S1–S6、S12–S13 图为森林图、偏倚和敏感性分析 | 没有以本工具重新进行荟萃分析 | 每小时线性 RR 与表 2 非线性点预测是不同分析 |

## 访问与补充文件清单

核查日期：2026-11-25。机器没有所述浙大缓存目录，未复制任何缓存全文进仓库。

- 期刊页：[AHA DOI 页面](https://www.ahajournals.org/doi/10.1161/JAHA.117.005947)，访问受 403 限制。
- 完整文章：[PMC5634263](https://pmc.ncbi.nlm.nih.gov/articles/PMC5634263/)；另从 [Europe PMC fullTextXML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5634263/fullTextXML) 获取完整正文、表格与材料链接，阅读 Methods、Results、Discussion、Disclosures 和 Supporting information。
- 出版类型：[Europe PMC DOI 检索](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1161/JAHA.117.005947&format=json)，卷 6、期 9、2017，Yin 等；同行评议期刊版。
- 唯一补充文件：[JAH3-6-e005947-s001.pdf](https://pmc.ncbi.nlm.nih.gov/articles/instance/5634263/bin/JAH3-6-e005947-s001.pdf)，67 页，3,657,996 字节，SHA256 `ae0d7d6d2d4f5567a304b78625964b7b7e2d44a5c03a13b2e20e1e6891b31ef0`。PMC 直接下载先返回 Preparing to download，AHA 及 Europe PMC 静态直链也未给出 PDF；最终通过 [Europe PMC supplementaryFiles](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5634263/supplementaryFiles) 的完整 ZIP 成功取得并打开 PDF。ZIP 还含正文图 1–6 的 JPG/GIF，并非另外的研究数据文件。
- 已提取并检查整个 PDF 的文本、逐表表头及内容分布，并渲染查看图 S7 的分层曲线。没有未下载的补充表。正文及 PDF 未列 GitHub、Zenodo、OSF 或其他发布代码/个体数据链接，因此没有需另克隆的作者仓库。

页码指补充 PDF 自封面开始的文件页码。

| 材料 | PDF 页 | 列名／内容 | 在本技能中的用途 |
|---|---:|---|---|
| Data S1 | 2–3 | PubMed / Embase 检索策略、排除理由、各结局文章数与报告数 | 核实综述设计与材料完整性 |
| Table S1 | 4–15 | Author, publication year, country; Study name; Age at baseline (years); Follow-up (years); Exposure; Exposure assessment; Sex, Sample size(cases); Sleep categories; corresponding relative risk (95% CI); Covariates in fully adjusted model | 核实全因死亡队列、测量及混杂调整 |
| Table S2 | 16–23 | 同 S1，另有 CVD incidence or mortality | 核实总 CVD 混合结局 |
| Table S3 | 24–29 | 同 S1，另有 Outcome，含 CHD incidence / mortality | 核实 CHD 混合结局 |
| Table S4 | 30–36 | 同 S1，另有 Stroke incidence or mortality | 核实卒中混合结局 |
| Table S5–S8 | 37–41 | Author / Study name; Selection; Comparability; Outcome; Total score | 四类结局的 NOS 质量评价，不作为个人输入权重 |
| Table S9 | 42–43 | Short sleep / Long sleep；No; RR (95% CI); Phet*; I²; Phet† | 全因死亡分层趋势 |
| Table S10 | 44–45 | 同 S9 | 总 CVD 分层趋势 |
| Table S11 | 46–47 | 同 S9 | CHD 分层趋势 |
| Table S12 | 48–49 | 同 S9 | 卒中分层趋势 |
| Figures S1–S4 | 50–53 | 最短/最长对参考组的森林图 | 不作为个人连续预测公式 |
| Figures S5–S6 | 54 | 偏倚 trim-and-fill 校正图 | 不修改正文表 2 |
| Figures S7–S11 | 55–59 | 非线性分层曲线 | 不从曲线读取或拟合新常数 |
| Figures S12–S13 | 60 | 卒中敏感性分析 | 不修改正文表 2 |
| Supplemental References | 61–67 | 纳入与排除的参考文献 | 核对材料范围，无另列代码/数据附件 |

正文表 1 列名：n；Shortest vs Reference、Longest vs Reference 下分别列 RR (95% CI)、I²、P Value。它的极端分组结果不用于本查表。正文表 2 列名与输出定义见 contract.md。

## 不一致与解释限制

正文短睡眠全因死亡极端组 CI 下限写 1.09，表 1 写 1.10；短睡眠总 CVD 每小时趋势在摘要/正文的区间上限为 1.08，补充表 S10 Total 为 1.09；本技能不调用这些趋势或极端分组估计。摘要概括低点约 7 小时，而正文卒中低点为约 6–7 小时，表 2 的 6 小时卒中 RR=0.99；保留该值，不强行将所有 RR 设为至少 1。

大多来自自报，夜间与全天睡眠混合；睡眠质量未单独建模；残余混杂和反向因果不能排除。亚组中总 CVD、CHD 发病和死亡的关联不同，不能将表 2 总体结果标作纯发病风险。研究观察关联不能证明干预获益。
