# 论文与材料核对

研究设计：预先规定结局的随机试验个体参与者数据荟萃分析。PubMed PMID 21067804 标为 Meta-Analysis；仓库枚举没有 meta_analysis，使用 rct 表达合并证据来自随机干预，不能读成一项新 RCT，也不是叙述综述。
物种：人（human；Homo sapiens 为标准学名），没有本文自己的动物或细胞实验。

样本：共 26 项试验、169,138 人；标题 170,000 是约数。强化与较低强度他汀共 5 项 39,612 人（分配强化 19,829；较低强度 19,783），其中急性冠脉综合征 8,659、稳定冠心病 30,953；中位随访 5.1 年。他汀与对照共 21 项 129,526 人（他汀 64,744；对照 64,782），含早期 14 项 90,056 人及新增 7 项 39,470 人；中位随访 4.8 年。总分配 84,573 与 84,565。没有推导/外部验证个人队列。三项合格试验 CORONA、SPARCL、GREACE 共 11,342 人的个体数据不可用，未算入上述合并样本。

全部试验及人数（正文 Table、Webtable 2）：

| 比较 | 试验与人数 |
|---|---|
| 强化 vs 较低强度 | PROVE-IT 4162；A to Z 4497；TNT 10001；IDEAL 8888；SEARCH 12064 |
| 他汀 vs 对照 | SSSS 4444；WOSCOPS 6595；CARE 4159；Post-CABG 1351；AFCAPS/TexCAPS 6605；LIPID 9014；GISSI-P 4271；LIPS 1677；HPS 20536；PROSPER 5804；ALLHAT-LLT 10355；ASCOT-LLA 10305；ALERT 2102；CARDS 2838；ALLIANCE 2442；4D 1255；ASPEN 2410；MEGA 8214；JUPITER 17802；GISSI-HF 4574；AURORA 2773 |

利益冲突：多数原试验获药企研究经费；部分写作委员会成员接受药企报销科学会议费用；A Keech 与 J Simes 接受 Solvay 与这些研究相关的讲课酬金。协作组由英国 MRC、British Heart Foundation、此前的 European Community Biomed Programme、澳大利亚 NHMRC 与 National Heart Foundation 支持。正文称资助方不参与设计、数据收集、分析、解释、写作或发表。

## 访问记录与完整性（2026-11-25）

用户明确本机没有图书馆缓存路径，未复制任何缓存进仓库。

- 打开 [DOI](https://doi.org/10.1016/S0140-6736(10)61350-5) 与 [Lancet 全文页](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(10)61350-5/fulltext)，出版商页受 403/验证限制。
- 已完整读取 [PMC2988224 正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC2988224/)；含正文 Table、Figure 1–6 及其解释、Methods、Discussion、利益冲突及 Web Extra Material。正文只列一个文件 mmc1.pdf（388.6 KB）。
- [PMC 附录链接](https://pmc.ncbi.nlm.nih.gov/articles/instance/2988224/bin/mmc1.pdf) 和 Europe PMC 的 `/articles/PMC2988224/bin/mmc1.pdf` 返回验证 HTML；Europe PMC supplementaryFiles API 未在时限内返回文件。未把这些 HTML 当 PDF。
- 最终完整读取[同一附录的公开存档文件](https://rcastoragev2.blob.core.windows.net/44427189f279aba33d480d0556532287/mmc1.pdf)，397,931 bytes，18 个 PDF 页面，标题、封面 DOI 和作者与本文一致，封面注明随原稿同行评审。只在临时目录保存 PDF 与文本，不提交原文文件。文档元数据 Title 含较早的 144,000 字样，封面及实际正文均是最终 170,000 / 26 trials，不以过期元数据改写本文样本。
- 附录的目录页码与页脚相差一页；记录时以 Webtable/Webfigure 编号及实际 PDF 页码定位。PDF 第 1 页封面、第 2 页目录、第 3–4 页两表、第 5–15 页十一图、第 16–18 页试验参考文献，全部可读。没有缺失的附录文件。
- 正文与附录没有提供 GitHub、Zenodo、OSF、可下载个体数据或分析代码链接；仅说明 SAS 与 R 版本。未把普通软件主页当成本文分析仓库。此次复现不需要原始个体数据。

## 材料与实现的对应

| 论文声称什么 | 补充表/图实际有什么 | 代码实际算什么 | 同名或相邻项目 |
|---|---|---|---|
| 更大降幅与更低的主要血管事件发生率，正文给总体 RR 及乘法示例 | Webtable 1：试验、Entry lipid criteria、Baseline lipid profile 的 TC/LDL-C/HDL-C/TG、Mean absolute difference at 1 year 的同四列；脚注有换算因子 | 本地脚本只把个人降幅代入合并关系；不从试验均值拟合 | CTT 是协作组系列研究；不能混用 2005 或 2012 论文常数 |
| 首次事件和死亡类别有明确操作定义 | Webtable 2：人数、主要冠脉事件、各类卒中、CRV、主要血管事件、癌症、各死因及全部死亡 | 不用事件总数直接相除重建 logrank RR | 不是 ASCVD 十年风险评分 |
| 效应随试验年份变化 | Webfigure 1：Year/Outcome、两组 Events (% p.a.)、RR(CI) per 1 mmol/L，首年主要血管事件 RR 0.88 | 不进行按年累计或把总体 RR 当首年概率 | 不是年风险计算器 |
| 不同终点有不同总体效应 | Webfigures 2–8：主要冠脉事件、非致死 MI、CHD 死亡、血运重建、任何卒中、缺血性卒中、出血性卒中；各有试验、LDL-C reduction、两组事件、未加权 RR 与每单位 RR | 只输出主要血管事件，不拼接终点 | 不计算出血性卒中净危害 |
| 亚组比较与总体关系的稳健性 | Webfigures 9–10：Subgroup、两组事件率、每单位 RR(CI)、heterogeneity/trend；分既往病史、糖尿病、性别、年龄、血压、BMI、HDL、吸烟、GFR | 不选择或混合亚组系数 | 不把亚组差异当个人预测 |
| 观察期内未见癌症发生显著增加 | Webfigure 11：各试验癌症事件与 RR；后接试验参考文献 | 不输出个人癌症风险或“绝对安全” | 不能推断所有不良反应都不存在 |

正文的剂量与方案只用于识别研究比较，不进入个人报告。副作用记录并非全面药物安全评价；尤其不把“未显著”写成“无风险”。
