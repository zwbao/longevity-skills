# 论文与材料核查

Wang 等，npj Aging **12:163 (2026)**，2026-07-30 发表；DOI [10.1038/s41514-026-00459-6](https://www.nature.com/articles/s41514-026-00459-6)。核查日期：2026-11-24。这是同行评审原创二次数据分析，人体主结论来自横断面关联；并非随机试验、治疗验证或已证实机制。

## 组别、物种和利益冲突

- NHANES 1999–2002：初始 21,004，分析 2,519；DunedinPACE ≤1 的 231，>1 的 2,288（Table 1）。甲基化样本限 ≥50 岁。CRP 替代敏感性分析 n=2,134；1999–2006、2011–2020 合并淋巴细胞分析 n=34,560。
- NHANES 2021–2023 用于 IBI/FI 分布比较，正文未给该比较的独立 n；不是对 IBI 切点预测准确性的外部验证。
- HRS 2016 n=2,849，用于 DunedinPACE 分布比较，不是用本技能算衰老速度的独立校准集。
- GSE236927：本文 WGCNA/B3 n=88。GEO 来源记录说明挪威 ≥70 岁居家成人筛查 n=437；PBMC 微阵列仅女性 n=96，排除异常后 95，有 FI 的 88。该来源研究的 FI 为 38 项，不可冒充 NHANES 49 项版本。
- GSE289417：本文单细胞比较为单核/巨噬细胞 2,066 与其他细胞 37,432；其中巨核祖细胞 14,637 是其他细胞的子组，不能重复相加。来源 GEO 记录为年轻 3 月龄与老年 >24 月龄 C57BL/6 小鼠，每年龄组 6 雌、6 雄；8 个 GEO 样本条目不能直接当作 8 只动物。细胞级比较未按供体汇总，仅支持定位描述。
- MR 使用欧洲血统 FI-37、FI-49、CRP、中性粒和 DunedinPACE 公共 GWAS；BLUE 工具为 149 变异，集中 RERE 区域。本文 Methods 未提供可明确定位全部数据的 accession ID 或各 GWAS 样本数，虽 Data availability 声称已提供；不自行补齐。
- 物种：人（human；GSE236927 记录为 Homo sapiens）、小鼠（mouse；GSE289417 记录为 Mus musculus）。这是对既有数据的跨物种分析，不是本研究新开展的人体治疗或小鼠干预试验。
- Competing interests：作者声明无利益冲突（“The authors declare no competing interests.”）。

## 四列对照

| 论文声称什么 | 补充材料实际有什么 | 公开代码或应用实际有什么 | 同名/相关项目辨别 |
|---|---|---|---|
| CRP mg/L × N/L 定义 IBI，探索切点 1.496 | S3D 拟合图标出切点和分段斜率；S4 C/D 明确 < 与 ≥ | 配套 Shiny 界面 CRP 标 mg/L，计数标 ×10⁹/L，说明栏列同一 IBI 切点；后台代码未公开 | 本技能只实现 inflammatory burden index；不复刻整个 FIRE 系统 |
| B3=(Z_ACP2+Z_PLBD2+Z_RNPEP)/3 后再次标准化 | S7/S8 是调控、通路和候选物图；不是固定标准化参数表 | 正文代码需合理请求作者；在线界面用 POAM 名称并称 gene weight coefficients，未见完整固定训练参数 | 正文 FIRE-AI、在线 FIRE-SCORE、B3/POAM 名称有差异；不能混用 |
| B3 内部高衰弱组 FI ≥0.25 | File S1 是 NHANES FI 项目评分规则 | 应用说明栏 FI threshold=0.21，非正文 B3 比较切点 | 本技能不计算 FI，不引入应用规则 |
| BLUE 有 529 基因，跨物种匹配 503 | S6–S8 描述关联、富集及候选物 | 无本文完整 BLUE 分析仓库 | 摘要写 503/513，而正文模块大小 529；不把 513 当成冻结基因名单长度 |
| IBI 关联 DunedinPACE、炎症为部分中介 | S2–S5 给回归/分层/中介结果 | 无个体预测模型截距或完整协变量参数 | DunedinPACE 是另外的甲基化算法，不能用 IBI 代替 |

## 全文、附件和公开来源清单

本机没有用户指定的图书馆缓存目录。全文与附件仅下载到 /tmp 阅读，未复制到仓库。

1. [期刊 HTML 全文](https://www.nature.com/articles/s41514-026-00459-6)、[正式 PDF](https://www.nature.com/articles/s41514-026-00459-6.pdf) 已打开；包括 Methods、Data availability、Code availability、声明。网页工具访问遇 Nature 身份跳转，但 curl 获取了完整正文。
2. [Table 1](https://www.nature.com/articles/s41514-026-00459-6/tables/1) 已打开；列名 Variables / Total (n=2519) / DunedinPACE ≤1 (n=231) / DunedinPACE >1 (n=2288) / Statistic / P。是群体统计量，没有个人 CRP/N/L 成套输入。
3. 页面只列一个 [Supplementary Information PDF](https://static-content.springer.com/esm/art%3A10.1038%2Fs41514-026-00459-6/MediaObjects/41514_2026_459_MOESM1_ESM.pdf)，全部文字已提取阅读，S3 页面另经渲染检查。含 S1 受试者流程、S2 FI/IBI 回归、S3 非线性和阈值、S4 亚组、S5 中介、S6 BLUE MR、S7 调控/通路、S8 网络药理，及 File S1。File S1 列名 Variable / Scoring，49 项；不是缺失的外部附件。S1 表内有排版/评分歧义，例如 BMI 和红细胞/血红蛋白行，未用于本技能。
4. [作者配套应用](https://tianwangwangwang.shinyapps.io/frailty-analyzer/) 冷启动后取得完整静态 UI。默认 CRP 2.5、中性粒 4.5、淋巴 1.8 只属于界面初始值；未得到论文印出的对应输出，不把自算结果当成验证示例。未向服务器提交任何患者数据。浏览器 CDP 连接超时，未依赖其输出；静态资料已足够核对输入和说明栏。
5. 期刊 Code availability 明示代码需向通讯作者合理请求。没有本文 GitHub/Zenodo/OSF 仓库链接可克隆，应用不是可下载的分析源码。
6. [GSE236927](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE236927) 和 [GSE289417](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE289417) 已经由 GEO 的 `targ=self&form=text&view=full` 记录打开。前者列 RAW.tar、non_normalized.txt.gz、run_GCF-2016-413.R.gz；后者列 RAW.tar。已打开前者 R 脚本，是原队列微阵列预处理，不是本文 IBI/B3 分析实现。原始表达压缩包未下载或重跑；不宣称已核对其中每项数据，本技能也不需要从这些数据估计任何常数。
7. [NHANES](https://www.cdc.gov/nchs/nhanes/) 和 [HRS data products](https://hrs.isr.umich.edu/data-products) 数据入口已打开。这些是来源数据库而非附带冻结模型的作者发布包；未下载受试者原始数据。IEU/EBI、KEGG、MSigDB、DGIdb 为文中点名数据库，无随文固定参数文件；不以重做 GWAS/网络分析来填补个人模型。

## 对结论的限制

S3C 图中非线性 P 标注与正文叙述有差异，Table 1 IBI 中位数也与跨周期段落不一致；本技能不从图线读出截距或校准常数。正文已强调横断面、细胞构成重叠、水平多效性和缺乏实验验证。中介比例、MR 效应和分段斜率是群体结果，不是个人“炎症造成的衰老百分比”。配套应用的临床分型或药物内容不纳入报告。
