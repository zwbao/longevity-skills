# 证据与实现核对

研究设计：APRICOT 随机试验资料的回顾性二次分析，主要是治疗前实验室指标与肝组织学的横断面分期建模，另有随访活检验证；不是随机治疗效果比较。清单采用 `rct_secondary` 表示试验资料的二次分析，不把治疗分组当作本指数的因果证据。[PubMed PMID 16729309](https://pubmed.ncbi.nlm.nih.gov/16729309/) 标注 Comparative Study 等出版类型，是原创研究而非综述。

全部样本组：APRICOT 共入组 868 人；因组织学不可解读排除 36 人，基线分析 832 人，来自 19 国 95 中心。随机分训练集 555、基线验证集 277；训练集轻/中/进展期分别 198/242/115（表 2）。表 4 含 INR 的模型可用 505 人，以 ALT 替代后可用 553 人；表 5A、5B 总计有可计算 FIB-4 的 830 人。另对 283 名治疗结束后六个月有随访活检者验证，并对基线验证集中的 92 名有中心病理读片者验证；两者均不能加到 832 后声称独立新增受试者。没有健康对照组。

物种：人（human，Homo sapiens）。本文没有新的动物或细胞实验。

利益冲突：Wiley 题名脚注声明“Potential conflict of interest: Nothing to report.”；作者单位包含 IST GmbH。PubMed 资助字段列出 NIH K23 DK064578、R01DA16078。没有把“无可报告冲突”扩写成“无任何资助”或无产业关联。

原文来源：[Sterling 等，Hepatology 2006，43(6):1317–1325](https://onlinelibrary.wiley.com/doi/full/10.1002/hep.21178)。核对日期：2026-11-26。

| 论文声称什么 | 补充表里实际有什么 | 代码仓库实际算什么 | 同名或相关的另一个项目是什么 |
|---|---|---|---|
| Results 印出年龄、AST、ALT、血小板构成的简化 FIB-4，并给两个个人算例 | 页面未列出补充表；完整公式在正文 | 未链接作者代码；本实现直接计算正文公式，复现 5 和约 1.0 | 后续 HCV 单感染、脂肪性肝病等 FIB-4 验证，不是本研究的原验证人群 |
| Table 5A 用两切点区分 Ishak 0–3 与 4–6 | 不依赖补充材料；FIB-4 列为 ≤1.45 / >1.45、<3.25 / ≥3.25 | 按该列判断 low / indeterminate / high | APRI 不是 FIB-4，不能替换公式；后来的其他切点不混入 |
| Table 5B 另用两切点区分 Ishak 0–1 与 2–6 | FIB-4 列为 ≤0.6 / >0.6、<1.0 / ≥1.0 | 独立输出次要终点的切点位置，不改变表 5A 输出 | 不等同于其他体系的 F2/F3/F4 诊断 |
| Figure 1 展示三个组织学分层的概率曲线和示例 | 未找到完整三分类概率模型的截距/阈值及系数 | 不生成个体概率，不拟合曲线或反推参数 | 公共计算器输出的百分比不是本次实现依据 |
| Discussion 限定 HIV/HCV 共感染、代偿、ALT 升高人群 | Patients 列完整排除标准；无新增文件 | 原人群提示始终保留，另提示血小板与指数超范围 | 不是通用衰老时钟或长期死亡风险模型 |

表格列名及用途：Table 1 为 Training set / Validation set，患者特征均值、标准差或比例；Table 2 为 Mild (0–1) / Moderate (2–3) / Advanced (4–6)，组织学计数和比例；Table 3 加 P 列，比较训练集中三个分层的特征；Table 4 为 Exploratory Factor / Odds Ratio / Lower 95% Limit / Upper 95% Limit / Significance，分别列含 INR 和替换为 ALT 的探索模型；Table 5A 为 Group (N) / FIB-4 / Stage 0–3 / Stage 4–6 / Sensitivity / Specificity / PPV / NPV；Table 5B 将分期列换为 Stage 0–1 / Stage 2–6。Table 4 不提供可直接用于三分类概率的全部参数；公式简化版本已单独印在 Results。

验证集的 AUROC 为 0.765（Figure 2B，进展期），表 5A 低切点 NPV 为 89.9%，高切点 PPV 为 65.0%、特异度为 96.8%；这都是队列性能，不是用户自己的概率。摘要四舍五入为 90%、65%、97%，并以严格不等号描述切点；程序按表格等号，差异见合同。表 5B 是另一结局，不能把其性能当成表 5A 的性能。

代码、数据和补充资料的检索途径及访问限制见 [contract.md](contract.md)。未发现属于此文的新材料，不把他文的 supplementary 文件当作此文补充表。旧证据库不在本次修改范围。
