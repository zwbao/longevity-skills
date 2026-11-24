# 论文与材料核查

## 研究背景

- 研究设计：人群观察性纵向队列，联合认知变化与失智发生时间建模；不是随机试验。预印本，未经同行评审。PubMed PMID 43060060 标记 Preprint；版本 1 发表于 2026-11-09，年份为 2026。
- 全部样本组：HRS 总认知分析 N=30509；PGI 分析 EUR=8728、AFR=1608、AMR=1182，合计 11518。APOE 表 S1/S3/S4 对应 N 分别为 10684/2240/1697，与 PGI 不是同一分母。正文称有 APOE 数据者 16802，其中 4288 为一拷贝、373 为两拷贝；不能将这个可用数据总数视作每个模型的拟合人数。LBC1936 为独立验证队列，基线 1091，经资料可用性筛选后 989；145 例失智，APOE 可用 934，年龄 11 岁认知数据 929；不是病例对照设计，没有独立“健康对照组”。
- 物种：人（human / Homo sapiens）。本文没有动物或细胞实验。
- 利益冲突：文章页 Competing Interest Statement 声明作者无利益冲突。资助为 NIH R01AG073593、T32DA007261、P2CHD042849、P30AG066614。

## 获取记录（2026-11-24）

本机没有用户所述的图书馆缓存目录。DOI、medRxiv v1 文章页、`.full`、`.full.pdf` 与 `.supplementary-material` 的直接访问遇到 Cloudflare；浏览器 CDP 前置检查因 WebSocket 连接超时失败。PubMed 与 [PMC13779053](https://pmc.ncbi.nlm.nih.gov/articles/PMC13779053/) 可确认身份，PMC 当时仅提供摘要和 PDF 链接，PDF 下载也未成功；Europe PMC 页面/XML 未成功。OpenAlex 条目及 [Tucker-Drob 实验室出版物页](https://labs.la.utexas.edu/tucker-drob/publications/) 只给同一 medRxiv 原文入口，没有另用其他版本替代。

随后通过 web-access 所述 Jina Reader 文本转换，成功读取以下**原 medRxiv 文档**：

| 文档 | 原始地址 | 读取情况 |
|---|---|---|
| 文章页 / 声明 | https://www.medrxiv.org/content/10.64898/2026.11.06.26367441v1 | 已读摘要、作者声明、利益冲突、数据可用性 |
| 正文 / Online Methods | https://www.medrxiv.org/content/10.64898/2026.11.06.26367441v1.full | 已读全文文字、图注与方法；公式图片不作为抄录系数来源 |
| Supplementary material 页面 | https://www.medrxiv.org/content/10.64898/2026.11.06.26367441v1.supplementary-material | 列出下列两个文件，均已打开转换内容 |
| Supplementary Note / 367441_file03.docx | https://www.medrxiv.org/content/medrxiv/early/2026/11/09/2026.11.06.26367441/DC1/embed/media-1.docx?download=true | 转换显示 13 页；含敏感性分析文字和 Figures S1–S11 图注；不从图片读点估计 |
| Supplementary Tables / 367441_file04.xlsx | https://www.medrxiv.org/content/medrxiv/early/2026/11/09/2026.11.06.26367441/DC2/embed/media-2.xlsx?download=true | 已打开目录和 S1–S18 所有工作表的转换文本，使用 S1/S3/S4 的 APOE 行 |
| Data/Code | https://www.medrxiv.org/content/10.64898/2026.11.06.26367441v1.external-links | 仅说明 HRS 和 LBC 数据可申请；未列公开代码仓库 |

正文、Supplementary Note、表格、Data/Code 页没有指向本研究分析成品的 GitHub、Zenodo 或 OSF 链接，因此没有论文指定的仓库可克隆。公开方法名称 Mplus、SBayesRC、PRS-CSx、PLINK2 不是本研究已发布成品。没有申请访问参与者数据，也没有将“不能访问原始数据”等同于“系数未公开”。原始二进制下载未成功；以上核查依据服务转换的原文表格，来源和这一访问限制均保留。

## 补充材料目录与列审计

| 表 | 实际内容和列 |
|---|---|
| S1 | LBC 与 HRS EUR 验证因素；Model Parameters 的 Predictor、N、认知水平/变化 Beta、S.E.、p，以及 Unique (Direct) Effect 的 Beta、S.E.、Hazard、95% CI Hazard、p；Mediation Analysis 为 Total Effect / via Level / via change，各有 Beta、S.E.、Hazard、95% CI、p，路径另有 % of Total |
| S2、S3、S4 | EUR、AFR、AMR 的遗传因素；同 S1 两块列结构，含 APOE 行和其他 PGI 行；S2 的 APOE 与 S1 HRS 相同，直接 CI 下限有差别 |
| S5、S6、S7、S8 | 全样本、EUR、Black、Hispanic 的基线流行病学风险因素；同样含回归和中介 Beta、S.E.、HR、95% CI、p；不作为本技能计算输入 |
| S9 | Lancet 风险因素和 HRS 流行病学/遗传指标对应关系，不是模型常数表 |
| S10 | GWAS 来源、祖源、病例/对照/总样本数；不是可用于个人 PGI 的逐 SNP 权重文件 |
| S11 | HRS 基线描述；Variable、M、SD、Min、Max |
| S12 | HRS 教育编码；Years of Schooling、Degree、Education |
| S13 | 有无代理回答的敏感性分析；回归参数及中介分析两块，同上 |
| S14 | TICS 代替总认知的敏感性分析；回归参数及中介分析两块 |
| S15、S16 | 即刻回忆代替总认知的流行病学/遗传模型；回归参数及中介分析两块 |
| S17 | LBC 标准化认知测验跨评估波次的描述统计 |
| S18 | LBC 多变量 factor-of-curves；Cognitive domain、Unstandardized loadings（Gi、Gs）、Standardized loadings（Gi、Gs）、Residual variances and covariances |

Supplementary Note 给出代理回答、TICS、即刻回忆的敏感性分析及 Figures S1–S11；没有另外的可下载 Appendix/eMethods/模型权重文件。Online Methods 在正文。所有本实现所需的常数来自表中数值和正文剂量定义，不依赖未读取的图像标注。

## 声称、数据、代码与同名方法

| 论文声称 | 补充表实际提供 | 代码仓库实际计算 | 同名或相关的其他项目 |
|---|---|---|---|
| ε4 与失智关联主要经认知变化，效果因祖源而异 | S1/S3/S4 逐祖源 APOE log HR 与 HR，足以重算剂量相对风险 | 未发现作者发布的分析代码；本实现仅指数换算，不声称重跑 Mplus | 一般 APOE 风险查表、商业 PRS 与本研究系数不是同一方法 |
| PGI 可区分病前与衰老相关路径 | S2–S4 汇总回归效应；S10 为 GWAS 来源 | 作者使用 SBayesRC/PRS-CSx 构建 PGI，未在上述材料发现逐 SNP 成品权重 | 这些软件是通用估计工具，不能代替作者权重或标准化过程 |
| LBC 验证 HRS 的主要模式 | S1 有 LBC APOE 估计，S17/S18 为认知描述和载荷 | 未重拟合 LBC；其下降 beta 与 HR 不一致，排除计算 | LBC 与 HRS 不是可互换的基线危险率或随访人群 |
| 流行病学因素与不同路径相关 | S5–S8 是队列关联 | 本实现未计算教育、运动、药物或生活方式目标收益 | 不能将 Lancet 风险因素清单当作本研究中的治疗因果模型 |

预印本、队列可迁移性、表内差异及测试容差详见 contract.md。现用药和常规体检不改变 APOE 模型结果，报告不提供剂量或启停药物指令。
