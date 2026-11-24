# 证据与材料核对

**研究设计**：系统综述与剂量反应荟萃分析。PubMed PMID 40713949 标记 Meta-Analysis；
不是新随机试验。纳入设备测得步数先于结局的成人前瞻性研究，合并的是观察性关联，
即使个别研究的参与者来自干预队列，也不等于随机分配的步数效应。manifest 使用 `evidence: review`。

**样本与物种**：人（原文 adults / participants；human）。系统综述 57 项研究、35 个队列；
荟萃分析 31 项研究、24 个队列。32 项研究是一般成人样本，25 项平均年龄至少 65 岁；
12 项研究涉及特定疾病、残疾或危险因素人群，这些分类有重叠。不同结局的参与者也重叠，不能相加为独立总样本。
没有独立的个人预测训练/验证队列，没有动物或细胞实验。表 1、表 3 和附录表 1 按结局及是否入荟萃分析列出样本。

| 结局 | 综述研究数（表3） | 合并研究数 | 合并参与者数 | 确定性（表3） |
|---|---:|---:|---:|---|
| 全因死亡 | 25 | 14 | 161176 | 中等 |
| 心血管病发生 | 9 | 6 | 111349 | 中等 |
| 心血管病死亡 | 7 | 3 | 120758 | 低 |
| 癌症发生 | 3 | 2 | 100505 | 低 |
| 癌症死亡 | 3 | 3 | 105660 | 中等 |
| 2型糖尿病发生 | 6 | 4 | 61594 | 中等 |
| 痴呆/认知结局 | 4 | 2 | 79699 | 中等（痴呆） |
| 抑郁症状 | 6 | 3 | 77565 | 中等 |
| 跌倒 | 4 | 4 | 94901 | 极低 |
| 身体功能 | 5 | 未合并 | 2657（综述） | 低 |

合并纳入/排除按结局决定，不能把各行综述研究数相加。
跌倒四项均为老年人群；排除其中一个大型研究后关联可变为无关联或反向，不能据此判断个人安全。
特定疾病研究（如不可手术肺癌、肝病、心力衰竭）未与一般人群相应结局合并。

**利益冲突与资助**：正文 Declaration of interests 声明无利益冲突。
资助来自 National Health and Medical Research Council、New South Wales Health、Ian Potter Foundation；
正文说明资助方未参与研究设计、收集、分析、解释或撰写。原始纳入研究各自资助详列于附录表 5，不能以综述作者的声明替代原始研究的所有利益关系。

| 论文声称什么 | 补充表里实际有什么 | 代码仓库实际算什么 | 同名的另一个项目是什么 |
|---|---|---|---|
| 表2公开步数与九项结局的HR及CI | 表8另以7000步为参照，并警告与主分析不可直接比较 | 作者没有公开仓库链接，代码仅按请求提供；本地实现只检索表2 | 未使用其他步数荟萃分析或步数计算器 |
| 多种结局关联非线性 | 表10列五种模型的BIC，不是完整的可计算系数表；附图展示敏感性分析 | 没有重拟合、插值、反推连续系数 | 不以Paluch、Stens等不同研究的曲线补齐 |
| 证据强弱因结局而异 | 表7列NOS评分，表1–2列队列特征及原始研究结果 | 只采用正文表3的GRADE标签，不将评分转为个人风险 | 无 |
| 步频证据有限，身体功能未合并 | 表9及附图28–29涉及步频，不是表2日步数的换算模型 | 不接受步频、距离、时长来推算日步数或身体功能 | 无 |

## 已打开材料与定位

核对日期：2026-11-25。机器未提供浙大缓存目录，未复制任何缓存文件。

- [出版社文章页](https://www.thelancet.com/journals/lanpub/article/PIIS2468-2667(25)00164-1/fulltext)及
  [ScienceDirect文章页](https://www.sciencedirect.com/science/article/pii/S2468266725001641)：尝试打开；直接抓取遭 403/安全验证，不能据此认为未发表附件。
- [出版社正式全文PDF](https://www.thelancet.com/pdfs/journals/lanpub/PIIS2468-2667%2825%2900164-1.pdf)：搜索工具可读取全文，表格转写存在误差。
- [ONAPS保存的出版社排版PDF](https://onaps.fr/wp-content/uploads/2025/10/2025-07-Daily-steps-and-health-outcomes-in-adults.pdf)：成功取得并读取14页正式期刊全文。
  题名、作者、DOI、页码e668–e681与期刊一致；表2 p e676渲染后视觉核对。
- [Elsevier补充附录mmc1.pdf](https://ars.els-cdn.com/content/image/1-s2.0-S2468266725001641-mmc1.pdf)：成功下载并打开，113个PDF页（封面加112个编号页），封面注明2025-08-27更正。
  全文只点名这一份在线附录；文件内包含下列所有Supplementary Files、Tables和Figures。
- [PubMed 40713949](https://pubmed.ncbi.nlm.nih.gov/40713949/)：核对出版类型、卷期年及勘误关联。
- 勘误[PubMed 40883040](https://pubmed.ncbi.nlm.nih.gov/40883040/)与Elsevier元数据可读；
  DOI 10.1016/s2468-2667(25)00199-9 的 Lancet/ScienceDirect 通知全文、PDF及Jina路径受阻。
  已直接取得更正附录，不把二手对勘误的转述当作核对结果。
- Elsevier article API仅返回元数据；正文 Data sharing（p e679）明确无额外数据、代码需索取，未指向 GitHub、Zenodo、OSF 或独立数据下载。

## 附录内容清单与列名

| 文件内项目 | 印刷页 | 已核对的内容或列名 | 与计算的关系 |
|---|---|---|---|
| Supplementary File 1a–1c | 3–8 | PRISMA正文/摘要、MOOSE核对项及位置 | 报告规范，不提供查表系数 |
| Supplementary File 2 | 9–16 | 分结局数据库检索策略 | 搜索方法 |
| Supplementary Table 1 | 17–40 | Study; Study name/country; Study entry; Sample; Exclusion criteria; Age; Sex/sample size/race; Step-monitoring device/wear location; Baseline step counts; Follow-up/events | 研究人群与分组 |
| Supplementary Table 2 | 41–51 | Study; Cohort; Outcome ascertainment; Median steps by category; Adjusted Hazard Ratio | 原始研究分组结果，不代替主文合并表 |
| Supplementary Table 3 | 52–57 | Cohort/country; Author/Year; Device type/wear location; Minimum wear time; Stepping rate measures | 没有统一设备换算常数 |
| Supplementary Table 4 | 58–62 | Cohort/country; Author/Year; Covariates | 各研究调整变量，非个人风险公式 |
| Supplementary Table 5 | 63–68 | First author/year; Funding source | 资助 |
| Supplementary Table 6 | 69–72 | First author/publication date; Title; Exclusion reason | 排除记录 |
| Supplementary Table 7 | 73–81 | Study; Publication; Selection; Comparability; Outcome; Overall score; Quality rating | NOS偏倚评价 |
| Supplementary Table 8（更正版） | 82 | Steps/day; 九项结局; k; n; HR (95% CIs) | 不同参照的事后分析，不用于本计算；页图及脚注已核对 |
| Supplementary Table 9 | 83–88 | Data source; Study; Study entry; Country; Sample age/female%; Sample size; Accelerometer model/wear location; Cadence measures; Main findings | 步频研究 |
| Supplementary Table 10 | 89 | Outcome; Linear; Splines; Quadratic; Cubic; Quadratic + cubic | 模型BIC，不含完整连续模型系数 |
| Supplementary Figures 1–8 | 90–97 | 分结局PRISMA流程 | 筛选流程 |
| Supplementary Figures 9–13 | 98–100 | 年龄/设备亚组曲线 | 不从图片反推数值 |
| Supplementary Figures 14–19 | 101–106 | 敏感性分析1–3 | 不并入主表 |
| Supplementary Figures 20–26 | 107–110 | 留一分析 | 说明结果对单个队列敏感 |
| Supplementary Figure 27 | 111 | 全因死亡漏斗图 | 发表偏倚 |
| Supplementary Figures 28–29 | 112 | 步频荟萃分析 | 非本技能输入 |

本文摘要、正文表格、图和机器转写间的差异及采用规则详见 [contract.md](contract.md)。
原始PDF仅存临时工作目录；仓库只保存所需数字转录及来源说明。
