# 证据与材料核对

研究设计：原创人类遗传关联研究；从既有 GWAS 建立候选评分，在 UK Biobank 验证、测试已有疾病状态。主结果是基线患病状态的横断面关联，不是药物随机试验或个体未来发病概率验证。Europe PMC PMID 30104762 的出版类型包含 research-article、journal article、research support，不是综述。

物种：人（human / Homo sapiens）。Reporting Summary 明确无动物及细胞系实验。

样本：LD 参考为 1000 Genomes Phase 3 version 5 的 503 名欧洲人。UK Biobank 共 409,258 名英国祖源参与者，平均年龄 57 岁，55% 女性；招募年龄 40–69。验证集 120,280，独立测试集 288,978；去亲缘敏感性分析 222,529。乳腺癌验证/测试分别限于 63,347/157,895 名女性。

| 疾病 | 发现 GWAS 病例/对照（合计） | 验证集病例/非病例（合计） | 测试集病例/非病例（合计） |
|---|---|---|---|
| 冠状动脉疾病 | 60,801 / 123,504（184,305） | 3,963 / 116,317（120,280） | 8,676 / 280,302（288,978） |
| 心房颤动 | 17,931 / 115,142（133,073） | 2,024 / 118,256（120,280） | 4,576 / 284,402（288,978） |
| 2 型糖尿病 | 26,676 / 132,532（159,208） | 2,785 / 117,495（120,280） | 5,853 / 283,125（288,978） |
| 炎症性肠病 | 12,882 / 21,770（34,652） | 1,360 / 118,920（120,280） | 3,102 / 285,876（288,978） |
| 乳腺癌 | 122,977 / 105,974（228,951） | 2,576 / 60,771（63,347） | 6,586 / 151,309（157,895） |

来源为正文 Table 1。非病例数和 GWAS 合计是对表中人数的算术展开，并非新增队列；表内各 GWAS 是已有联盟研究的汇总，本文没有提供组成联盟每个队列的完整逐人数据。上述展开不作为个人评分验证示例。

利益冲突：Khera 与 Kathiresan 是利用遗传风险评分判断风险并指导治疗的一项专利申请的共同发明人；Kathiresan 与 Ellinor 获 Bayer AG 向 Broad 提供的心肌梗死及心房颤动遗传与治疗研究资助（Competing interests）。

| 论文声称什么 | 补充材料实际有什么 | 公开代码与数据实际提供什么 | 同名或相关项目区别 |
|---|---|---|---|
| 五种疾病的高多基因风险尾部与较高患病比值比相关 | 正文 Table 2、3 和补表 7、10 给人群比例、OR、CI、P | 五份完整逐变异权重，足够重算原始和；没有逐人完整剂量与总分配对 | 后来的多祖源 CAD 或 GPSMult 并非本文 2018 v3 模型 |
| 用验证集最大 AUC 选择最优模型 | 补表 1–5 列各疾病的 31 个候选；补表 6 跨策略比较 | 发布文件已固定最优模型，无需用户重训或运行 LDpred | PGS Catalog 收录本研究评分；本技能直接用作者 Broad v3，未混用后续版本 |
| 分数与疾病风险梯度对应 | 补图 1 比较 CAD 三种评分；补图 2、3 为预测/观察患病率 | 公开权重没有个人百分位参照、概率模型截距与完整校准参数 | Hail 是通用基因组分析软件，并非本论文个人风险解释器 |

## 实际打开的材料与列

核查日期 2026-11-26。用户未提供本机订阅缓存目录，没有复制任何缓存到仓库。

- [Nature 期刊页面](https://www.nature.com/articles/s41588-018-0183-z)：读原始 HTML；列出两份 ESM PDF。web 工具跳转受限，公开 curl 成功。
- [Broad 保存的期刊全文 PDF](https://www.broadinstitute.org/files/publications/2019/01/s41588-018-0183-z.pdf)：已读 1219–1224 正文、Methods 和报告摘要。PMC 网页遇校验，Europe PMC fullTextXML 首次 503；没有将这些失败当作全文不可用。
- [MOESM1](https://static-content.springer.com/esm/art%3A10.1038%2Fs41588-018-0183-z/MediaObjects/41588_2018_183_MOESM1_ESM.pdf)：完整打开。补图 1–3；补表 1–5：Derivation Strategy、Tuning Parameter、N Variants Available / N Variants in Score (%)、OR per SD (95% CI)、AUC。补表 6：Disease、Derivation strategy、N variants available / N variants in score (%)、Tuning parameters、AUC (95%CI)。补表 7、10：High GPS definition、Reference group、Odds ratio、95% Confidence interval、P-value。补表 8：Baseline characteristics、Remainder of population、Top 8% of GPSCAD distribution、P-value。补表 9：Disease、N variants available / N variants in score (%)、Proportion of variance explained (%)。最后为补充参考文献，没有其他未下载补表。
- [MOESM2](https://static-content.springer.com/esm/art%3A10.1038%2Fs41588-018-0183-z/MediaObjects/41588_2018_183_MOESM2_ESM.pdf)：完整打开，Life Sciences Reporting Summary 两页；设计、排除、软件、材料、物种及人体信息，不含额外模型参数。
- [Broad/CVDKP 当前数据页](https://hugeampkpncms.org/node/1199)：找到对应 DOI 下五个链接。论文旧链接为 `http://www.broadcvdi.org/informational/data`；实际获取的是当前页链接的 Broad 官方服务器文件。每份 zip 已完整下载并读取全部行。共同列：`variant, effect_allele, effect_weight, chr, position_hg19, A1, A2`。文件注释明确 hg19 和效应等位基因含义。所有行符合列数/有限权重/效应等位基因属于等位基因对的审计，具体版本见 `weights.json`。
- [Hail](https://github.com/hail-is/hail)：已克隆当前提交 `80cd5e05290e591e11be86e0c933f4741f42837e`，读取 README 和方法目录。它是通用平台；不能把当前代码当作论文当年的分析版本或声称用它复现了队列结果。正文没有链接论文专用 GitHub、Zenodo 或 OSF 包。
- [Europe PMC 元数据](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41588-018-0183-z&format=json)：确认原创出版类型、2018 年卷 50 期 9、页 1219–1224。

## 原文内部差异

Methods 的 Statistical analysis within the testing dataset 有一处写 288,278，正文、Table 1、其余 Methods、图注和补表一致为 288,978；本技能记后者，并不据这处笔误生成输入或常数。Supplementary Table 6 的 CAD 最优 pruning/thresholding 可用/总数顺序与 Table 1 的对应表有出入；本技能使用最终发布的 LDpred 模型，不使用该候选数据。Supplementary Table 7 标题的 GPS 6,630,100 是测试集中可用位点，脚注与正文给出的完整模型是 6,630,150。

高尾部的“三倍风险”来自调整协变量后的群体 odds ratio，不能等同个人未来风险比或绝对概率。不能把论文示例人群比例或 OR 当作由单个人原始分数就能推出的结果。
