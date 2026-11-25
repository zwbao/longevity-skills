# 材料审计

核对日期：2026-11-25。机器未提供图书馆缓存目录；没有把任何缓存原文或 PDF 放入仓库。

- 期刊文章页：[BJSM 56/13/755](https://bjsm.bmj.com/content/56/13/755)。直接访问被 403 拒绝；不是据此判断内容不存在。
- [PubMed PMID 35228201](https://pubmed.ncbi.nlm.nih.gov/35228201/)：核对作者、卷期年 2022、Meta-Analysis 类型、PMCID PMC9209691。
- PMC 网页先遇浏览器挑战；[Europe PMC 全文 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9209691/fullTextXML)成功读取全文、Table 1、图注、声明及全部补充链接。XML SHA-256：`ffe5462b860ed16387503b573c56b65debce95491864b1900fdc387496625c8a`。
- 唯一补充文件：[期刊 inline-supplementary-material-1.pdf](https://bjsm.bmj.com/content/bjsports/early/2022/01/19/bjsports-2021-105061/DC1/embed/inline-supplementary-material-1.pdf?download=true)，PMC 文件名 `bjsports-2021-105061supp001.pdf`。先经网页工具读取索引文本，直接下载被403拒绝；随后从 [Europe PMC supplementaryFiles](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9209691/supplementaryFiles) 成功完整下载 ZIP 并读取 38 页 PDF。早期短时下载不完整，最终完整 ZIP 已成功列出并解压。PDF SHA-256：`bd415fdb2786409902dc0b0df177831b044ea2c5ed3475079f41c0acdbb0e9fe`。
- 同一 ZIP 其他 10 个文件是正文 Figures 1–5 的 GIF/JPG 两套格式，未发现额外附录、程序或数据表。图3糖尿病面板已直接查看图片，与 Table 1 数值一致。

附录内容清单：

| 文件内位置 | 内容及已核对列 |
|---|---|
| Table 1，p1–5 | MEDLINE/Embase 检索策略，检索编号及语句 |
| Table 2，p6–8 | NOS：选择、可比性、结局评价、星数和定义 |
| Table 3，p9–11 | GRADE：研究数、设计、偏倚、不一致、间接性、不精确、发表偏倚、人数、病例、RR/CI、确定性 |
| Table 4，p12–18 | 未进入荟萃分析的结局；研究、队列、人群、病例/人数、随访、暴露、效应、协变量、质量 |
| Table 5，p19 | 同队列多篇发表排除清单，文献及排除理由 |
| Table 6，p20–31 | 纳入研究；作者/年份、国家/队列、人群、结局/病例/人数、随访、暴露测量及类别、效应、协变量、质量；糖尿病在p27–28 |
| Figures 1–7，p32–38 | 逐一排除、暴露测量亚组、质量亚组、性别亚组、CVD结局亚组、分部位癌症两组及线性分析 |

全文、附录和链接清单中没有本研究发布的 GitHub、Zenodo、OSF、独立 eMethods 或独立数据文件；因此无仓库可克隆。本文引用的其他论文和公共运动指南不是本研究发布的补充数据。仅固定本技能所需的数值和短引文，不保存原始长文。
