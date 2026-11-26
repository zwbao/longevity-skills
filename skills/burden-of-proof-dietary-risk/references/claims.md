# 证据与来源核查

研究：Haile 等，Nature Medicine **31(7), 2244–2254 (2025)**；DOI 10.1038/s41591-025-03775-8，同行评议期刊论文。

研究设计：系统检索后的原创 Burden of Proof 荟萃回归，输入主要为前瞻性队列，含嵌套病例对照；没有随机干预或独立的个人预测验证组。Europe PMC / PubMed PMID 40588677 的 publication type 为 **Journal Article**，未标为 Review。清单 `evidence=cohort` 表示主要结论来自人群观察证据的汇总，不宣称单一新队列或 RCT。

物种：人（human）；无动物或细胞实验。研究总体针对成年人，未给可用于个人分层的年龄、地区或性别特异方程。附表 5 个别来源年龄列含低于成年界限的记录，不能据此宣称适用于儿童。

利益冲突：期刊页面与接受稿均声明作者无竞争性利益。资金为 Bill & Melinda Gates Foundation，OPP1152504；接受稿声明资助方未参与研究设计、数据收集、分析、解释、写作和发表决定。

## 全部分析组

以下为接受稿 Results 各小节印出的汇总样本和事件数，不是个人报告输出。六组可能复用研究/受试者，不能相加为独立总人数；无推导/独立验证划分，也没有新增实验对照组。每项 RR 以理论零摄入为参照，不等于每个原始研究都有完全不摄入的对照者。

| 暴露—结局 | 纳入研究 | 参与者 | 事件 |
|---|---|---:|---:|
| 加工肉—2 型糖尿病 | 15 前瞻性队列 + 1 嵌套病例对照；96 个观察量 | 1,115,885 | 64,607 |
| 加工肉—IHD | 11 前瞻性队列 | 1,173,821 | 31,549 |
| 加工肉—结直肠癌 | 18 前瞻性队列 | 2,678,052 | 30,259 |
| SSB—2 型糖尿病 | 18 前瞻性队列 + 1 嵌套病例对照；92 个观察量 | 563,444 | 39,505 |
| SSB—IHD | 8 研究；27 个观察量 | 961,176 | 24,542 |
| TFA—IHD | 6 前瞻性队列 | 226,509 | 12,548 |

各原始队列名称、病例数和样本数逐组列于附表 5；原始 log 效应量和标准误逐行列于附表 10。SSB—IHD 正文的结局说明分别写了 3 项仅死亡与 6 项兼有发病/死亡，引用有重叠，不将二者相加取代其明示的 8 项总数。

## 逐来源对照

| 论文声称什么 | 补充表实际有什么 | 作者代码实际算什么 | 同名或相近项目 |
|---|---|---|---|
| 六个暴露—疾病关系为非线性；RR 相对零摄入 | S13–S16 印出 39 个摄入点，以及含/不含异质性的 RR 与 UI 两列 | `bopforge` 建立样条集合，拟合偏倚与异质性；本技能不重新拟合 | 2022 年未加工红肉 Burden of Proof 是另一论文，不能替换加工肉参数 |
| 加工肉与 IHD 一星，其余五项二星 | 主表 2 的星级、ROS 和 BPRF；S17 为未修剪敏感性分析 | `Bop_summary_table.R` 读取已运行输出的 `summary.yaml`, `inner_quantiles.csv`, `outer_quantiles.csv` | 在线 VizHub 可更新，未将当前在线结果当作冻结的 2025 表值 |
| 糖尿病/癌症等 RR 曲线及保守 BPRF | S11 是样条阶数、结点数、先验；S12 是偏倚变量和 gamma，不是完整的最终样条系数 | 六份 processed_foods R 文件为清洗、单位处理及制表；多处 `FILEPATH` 占位，未附此次分析的全套已拟合结果 | `bopforge` 随包 continuous 示例是蔬菜—IHD，不是本论文的食品结果 |
| 食物摄入与疾病之间有群体关联 | S13–S16 没有个人基线风险、生存函数、风险联合项或干预前后协方差 | 上游流水线估计关联，不是随机饮食干预的效果预测器 | 不把一般“超加工食品比例”与本论文三类暴露互换 |

## 已打开的材料与列

核查日期：2026-11-25。环境未提供图书馆缓存路径，未复制任何全文 PDF 或缓存文件进仓库。

1. [期刊文章页](https://www.nature.com/articles/s41591-025-03775-8)：取得摘要、Data availability、Code availability、利益冲突、补充材料链接；正文受订阅限制。期刊 PDF 未能直接取得完整文档。
2. [Zenodo 作者接受稿记录](https://zenodo.org/records/16955948)：文件 `24032025_NMED-A137099B_Haile_clean_20250423_-_gates.pdf`，记录明确标 Accepted Version，与上述期刊 DOI 相同。直接下载和预览返回 403；经 web-access 允许的 Jina 公开文本读取通道取得 96 页全文及附录，读到 Results、Discussion、Methods、主表 1–2、数据/代码声明和附录。全文只在临时目录使用。
3. [期刊 Supplementary Information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-025-03775-8/MediaObjects/41591_2025_3775_MOESM1_ESM.pdf)：47 页，实际打开并提取文本；PDF 第 44–45 页作图像核对。S1–S3 为 PRISMA/GATHER 清单；S4 为提取模板；S5 列有 risk factor、outcome、author/year、study name/location/design、sex、follow-up、age start/end、exposure/outcome ascertainment、events 和 sample size；S6–S9 为偏倚变量定义和研究设计/非饮食/饮食混杂评分；S10 列 risk、outcome、author/year、sex、alternative/reference exposure、log RR、SE；S11 为 spline degree/interior knots、priors/constraints；S12 为 selected bias covariates 与 gamma mean/sd；S13–S16 为摄入量、with-heterogeneity RR(UI)、without-heterogeneity RR(UI)；S17 为不修剪的 RR、BPRF、ROS、星级、发表偏倚、研究数和选定协变量。全部补充表位于这一份 PDF，没有遗漏未下载的单独电子表格。
4. [Reporting Summary](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-025-03775-8/MediaObjects/41591_2025_3775_MOESM2_ESM.pdf)：5 页扫描 PDF，全部页经 OCR 读取；确认二次数据、观察性研究、无随机化/盲法及两份代码仓库链接，不含新增计算系数。
5. [processed_foods 代码](https://github.com/ihmeuw-msca/burden-of-proof/tree/main/risks/processed_foods)：克隆并读到六份 R 脚本；仓库 commit `c8ad876a579cfd136850c13549aa706cd0fa2437`。所需输入/输出指向本地占位路径；本技能没有运行上游训练。
6. [bopforge](https://github.com/ihmeuw-msca/bopforge)：克隆并核对 continuous pipeline 的函数和随包示例；commit `0d9156ed6fc66150190ae596deca9474a0b1774f`。它提供拟合引擎，不提供本次六个饮食模型的全套已拟合对象。
7. [Burden of Proof VizHub](https://vizhub.healthdata.org/burden-of-proof/)：打开正式版数据声明指向的页面和前端；读取 risk、risk_cause 元数据，确认 processed meat=117、SSB=118、TFA=123。尝试六组 `api/v1/output_data?risk=...&cause=...`（117/976、117/441、117/493、118/976、118/493、123/493），均返回 403，未取得连续风险结果；未把失败解释成“没有公布”。采用已完整取得的期刊附表作为唯一运行时数值来源。
8. [Europe PMC 元数据](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41591-025-03775-8&format=json&resultType=core)：PMID 40588677，无 PMCID；卷期为 2025 年 7 月。OpenAlex locations 只有期刊与 PubMed，未列另一个开放副本；ResearchGate 为出版社第一页预览，未当作全文。

## 需要保留的差异与限制

- 附表 S13 的 50 g/d 加工肉—结直肠癌：with-heterogeneity 为 **1.26 (1.08, 1.47)**，右列中心值为 1.27；不能把右列中心值与左列区间混在一起。
- S15 的 750 g/d SSB—IHD 左列中心值 **1.29**，右列 1.28；S16 的 4% TFA—IHD 左列 **1.3**，右列 1.29。运行时统一保留左列，不自行“纠错”。
- S14 没有 150 g/d 行；虽然前后均印 1.15，仍不能假定缺行也相同。
- 接受稿 SSB—IHD Results 写 exposure-averaged BPRF=1.03、同时写至少 2%；摘要和主表 2 为 2%。本工具不用这个不一致的汇总 BPRF 计算个人读数，仅使用 S15。
- 附录标题沿用 Figures 1–6，接受稿正文整合为 Fig. 1–3 的各 panel；精确出处以附表号和 PDF 页为准。
- RR 是全研究平均关联；可能混合发病和死亡结局（SSB—糖尿病仅发病）。残余混杂、饮食回忆误差和研究间异质性仍存在。
- TFA 研究聚焦工业来源，并纳入部分总 TFA 研究（作者假设主要为工业来源）；不能解释为反刍动物来源反式脂肪的单独风险估计。
- 范围内有读数不等于该点证据密集；报告会提示超出论文概括证据的摄入密集范围上端。零参照仅定义 RR=1，不代表个人零风险。
