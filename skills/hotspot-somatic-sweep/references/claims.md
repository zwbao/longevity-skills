# 论文证据与实现边界

研究：Watson 等，Nature，2026，DOI 10.1038/s41586-026-11269-x。2026-11-11 在线发表；本次页面尚无卷期。PubMed PMID 43015468 的出版类型为 Journal Article，非综述、非预印本。

设计：依托 UKCTOCS 生物样本库的纵向、观察性病例对照研究，结合演化模拟和独立 UK Biobank 人群验证。虽然样本来自随机筛查试验，但本研究明确称 observational case-control，研究者没有比较随机干预的疗效，因此标 `case_control`，不标主要终点 RCT。

全部样本组与独立分析：

- UKCTOCS 原始试验招募 202,638 名绝经后女性，入组年龄 50–74 岁，其中 50,640 人进入含年度血样的 multimodal arm。此研究选择 47 名后来发生 AML 且有至少两次诊断前样本的女性，取得 249 份样本；初选 47 名对照、249 份匹配样本，其中一名随后发生 MDS 而排除，最终对照为 46 人。不能把最初 249 份对照样本称为排除后的最终分析样本数。病例诊断年龄中位 72、范围 53–83 岁，诊断前样本最多十份、中位五份。
- 细胞组成分析：94 份全基因组亚硫酸氢盐样本来自 23 名病例和 23 名对照（部分人重复采样），88 份通过覆盖要求；表 11 的 44 case、44 control 是样本数而不是各 44 名独立参与者。
- 测序技术验证：Horizon Myeloid DNA Reference Standard 含面板内 14 个 SNV 和 5 个 indel，稀释至 25%、1%、0.1%，并含未稀释标准品和 65 岁供者外周血 DNA 对照、技术重复；另有模拟 mCA 与结构变异测试，不是额外的人群风险验证。
- UK Biobank 最终 Methods：排除基线既往癌症后 424,089 人，继续排除后来出现其他血液恶性病的 4,035 人，剩 420,054 人；未来 C92 髓系白血病病例 516 人。热点携带者 5,034 人，其中病例 114、非病例 4,920；双驱动携带者 106 人，其中病例 23；扫荡携带者 388 人，其中病例 42。Figure 5f 报告 OR 107（95% CI 75–150）。这些数仅是研究背景，不是报告中的个人风险输出。
- 模拟：200,200 个模拟个体，943 个模拟 AML。图 5 的人群预测值不能当成人体个人临床概率。

物种：人（human，Homo sapiens）。包括人血液 DNA、人体样本和标准 DNA/计算模拟；本文没有小鼠或其他动物实验，不把计算模拟当成物种。

利益冲突：S.A.、A.G.-M.、U.M. 报告 Mercy BioAnalytics Ltd 的个人咨询费（2024 年 5 月至 2025 年 3 月），以及 Intelligent Lab on Fiber、RNA Guardian、MercyBio Analytics、CleoDx 支付给所在机构、与卵巢癌早期检测有关的研究支持。不得写“所有作者无利益冲突”。

| 论文声称什么 | 补充材料实际有什么 | 作者代码实际做什么 | 同名或邻近项目的区别 |
|---|---|---|---|
| 高 VAF 热点与未来髓系白血病相关 | 最终正文印出热点替换、支持读段过滤和扫荡切点；表 6 有 UKCTOCS 原始计数/VAF，不是 UKB 逐人结局表 | Figure_5f.ipynb 读取受控 UKB 表后画 VAF 散点及 0.3 竖线；数据未分发，notebook 没有一个可直接调用的个人风险方程 | TETRIS-seq 是上游测序处理工具，不是个人 AML 风险评分 |
| 可从连续血样推断克隆结构和适应度 | 表 8 克隆结构与推断依据，表 9 适应度和建立时间；Supplementary Note 4 解释优化过程 | Code_for_inferring_acquisition_age_and_fitness_v16.py 做个体轨迹最大似然优化 | 本技能只用单次热点记录，不复刻纵向推断 |
| 早期低速克隆可获得更强驱动突变并扩张 | Supplementary Notes 1–5、Figures 1–60 与正文动力学和模拟图 | Figure_5b_e.ipynb、sim_fast.py 等计算模拟；与真实 UKB 分开 | 论文模拟阳性预测值不是个人诊断，不能移植到本报告 |

## 已核对的版本差异

- 最终正文、Figure 5f 写 27 个基因组热点位置；Figure_5f.ipynb 开头仍写 23。实际冻结最终 Methods 印出的蛋白替换，不凭计数补名单。
- Reporting Summary 的 Replication 行写 UKB n=335,090；最终 Methods 写 420,054。采用最终正文并保留此差异；不能把两组人数合成同一验证队列。
- Reporting Summary 的 Blinding 声称测序/主要变异检测时未知病例身份；最终 Methods 说 sequencing and analysis 未盲法。引用最终 Methods，不在技能中宣称盲法验证。
- EGA 项目标题仍用 “decades preceding”，期刊版标题为 “years preceding”；依据明确的 DOI 和代码链接核对为同一研究，不从标题差异另创研究。
