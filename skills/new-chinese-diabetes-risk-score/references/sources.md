# 材料核对记录

检索日期：2026-11-25。机器没有用户所述浙大缓存路径；未把任何下载的完整文章或缓存文件复制到仓库。

| 来源 | 结果 |
|---|---|
| [DOI入口](https://doi.org/10.2337/dc13-0593) | 返回403 |
| [期刊文章页](https://diabetesjournals.org/care/article/36/12/3944/33144)及摘要入口 | 直接访问403；Jina读取也只得到安全验证页面 |
| [PubMed](https://pubmed.ncbi.nlm.nih.gov/24144651/) | 题名、作者、2013年36卷12期3944–3952页和研究类型可核对；Multicenter Study，不是综述 |
| [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3836161/) | 浏览器验证阻挡，未用摘要替代全文 |
| [Europe PMC](https://europepmc.org/articles/PMC3836161)及EBI全文XML接口 | 页面403；XML请求40秒超时 |
| [CDC文章存档](https://stacks.cdc.gov/view/cdc/28193) | 成功；列出正文PDF、NXML、Table 1–3和Fig.1的图像及license.txt |
| [CDC全文PDF](https://stacks.cdc.gov/view/cdc/28193/cdc_28193_DS1.pdf) | 成功；完整9页，全部正文与表1–3及图1已核对，表2另作图像检查 |
| [CDC正文NXML](https://stacks.cdc.gov/view/cdc/28193/cdc_28193_DS2.txt) | 成功；与PDF比对，核对定义、全部样本、利益冲突、结论及外部链接 |
| [Supplementary Data DC1](https://care.diabetesjournals.org/lookup/suppl/doi:10.2337/dc13-0593/-/DC1) | 原文p.3944和NXML唯一补充材料链接；HTTP/HTTPS与静态获取均未取得，直接请求返回403；未取得文件名、表号或列名 |

web-access的Chrome/CDP前置检查连接超时，因此没有可用浏览器会话可再访问附件。上述限制没有被描述为“作者未公布补充材料”。正文及NXML没有发布代码仓库、GitHub、Zenodo、OSF或个体数据链接，未凭空克隆其他同名项目。

## 已打开的表与计算依赖

- Table 1（p.3946）：列为Exploratory population、Validation 1、Validation 2；男女分开，含N、年龄、BMI、腰围、血压、家族史等及未诊断糖尿病。用于样本说明，不作为个人默认值。
- Table 2（p.3947）：行是六项因素的类别，列为β-Coefficient、OR (95% CI)、Score。本技能只用类别和Score；这是完整所需权重表，没有缺失计算常数。
- Table 3（pp.3948–3949）：方法、风险因素、原始AUC/切点以及两个验证组的AUC/敏感度/特异度；用于辨别验证1是新发、验证2是现患，不转成个人概率。
- Fig.1（pp.3950–3951）：不同评分在总体、男性和女性中的群体判别性能；不是个体预测值查表。
- Supplementary Data：未打开内容，不能报告其列名；本实现没有使用它。
