# 资料与可行性审计

核查日期：2026-11-25。无机器上的图书馆缓存目录；没有把图书馆缓存文件复制进仓库。原始下载暂存于 /tmp；仓库仅冻结为计算所需而提取的CSV。

- [出版社文章页](https://www.bmj.com/content/353/bmj.i2716)：尝试打开，返回403；PMC网页受浏览器验证限制。web-access的CDP连接检查超时，未依赖登录浏览器。
- [Europe PMC出版记录](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1136/bmj.i2716&format=json)：确认 PMID 27301975、PMCID PMC4908315、2016年、系统综述/荟萃分析类型。
- [Europe PMC完整JATS全文](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4908315/fullTextXML)：成功读取全文，包括方法、全部结果、表1/表2、讨论、利益冲突、资助和数据共享声明；非摘要替代。许可为CC BY 3.0。
- [全部补充文件包](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4908315/supplementaryFiles)：成功下载、解包。XML仅列两份补充文件；包另含正文图像，并无额外eMethods、代码或数据文件。
- **Appendix 1: Supplementary tables S1–S21**，`aund029745.ww1_default.pdf`：已打开、提取全文，实际计算用PDF第69页S13和第70页S14，另渲染两页并对照列对齐、空格和空单元格。
- **Appendix 2: Supplementary figures S1–S109**，`aund029745.ww2_default.pdf`：已打开、提取109图标题及内容；包含高低摄入比较、森林图、非线性散点曲线、漏斗图和影响分析，未用于图像读数或重建参数。

PMC附录链接（文章JATS中的media文件）：

- https://pmc.ncbi.nlm.nih.gov/articles/instance/4908315/bin/aund029745.ww1_default.pdf
- https://pmc.ncbi.nlm.nih.gov/articles/instance/4908315/bin/aund029745.ww2_default.pdf

单独PMC文件访问遇到网页验证，BMJ静态补充URL尝试亦被拦截；上列Europe PMC补充文件包提供同名两份完整PDF，因此不存在尚未取得的已列补充文件。原文未链接GitHub、Zenodo、OSF或其他发布代码仓库；分析软件是Stata 12.0。Data sharing声明为“No additional data available.”，没有可以或需要克隆的论文代码库。

## 表格目录与列

| 材料 | 内容与已核对的列 |
|---|---|
| S1 | PubMed/Embase检索策略，检索项编号及组合 |
| S2 | Exclusion reason、Reference number，以及文献列表 |
| S3–S7 | 冠心病、卒中、心血管、总癌症、全因死亡：Author/publication year/country、Study name、Study period、Number of participants/gender/age/cases/deaths、incidence or mortality（适用时）、Dietary assessment、Exposure and subgroup、Whole grain consumption frequency or amount、Relative risks (95% confidence intervals)、Adjustment for confounding factors |
| S8–S12 | 呼吸、感染、糖尿病、神经系统、非心血管非癌症死亡，同样的研究特征与暴露、RR、调整项列 |
| S13 | Coronary heart disease、Stroke、Cardiovascular disease、Total cancer、All-cause mortality，每个结局g/d及RR (95% CI)，末行Pnonlinearity |
| S14 | Respiratory disease mortality、Diabetes mortality、Infectious disease mortality、Nervous system disease mortality、All noncardiovascular, noncancer causes of death，各有g/d、RR (95% CI)，末行Pnonlinearity |
| S15–S16 | 亚组名、n、RR (95% CI)、I²、Ph1、Ph2；每3份/日增量分析，不用于本查表 |
| S17–S21 | 各研究选择/可比性/结局评估条目及Total score，质量评分不属于个人输入 |

## 冻结数据

`data/nonlinear_rr.csv`列为outcome、g_d、rr、ci_low、ci_high、table。只包含有RR的144行，参照行缺CI保留空字符串。提取保留原表小数精度；S13最后两行和S14从120开始的空格已按PDF视觉核对。数据文件SHA-256记在skill.json中。来源署名：Aune D, Keum N, Giovannucci E, Fadnes LT, Boffetta P, Greenwood DC, Tonstad S, Vatten LJ, Riboli E, Norat T. BMJ 2016;353:i2716, Appendix 1 Tables S13–S14；按CC BY 3.0提取整理，不代表作者认可本实现。

下载文件指纹（用于来源核对，不随技能分发整份PDF）：

- `aund029745.ww1_default.pdf`: `9078afd128dc09103884eb4292be8a96b05839d5062aa5ab9f50469035eb41d4`
- `aund029745.ww2_default.pdf`: `23eb6f323e69756df266453c864646b6e79a67e2d35cda2c80f9a36fd744abb6`
