# 原文与实现核对

核对日期：2026-11-26。年份采用卷期年1998，作者记作Bush等。

- 研究设计：原创多中心横断面问卷效度研究的事后分析；PubMed列为Multicenter Study，JAMA列为Original Investigation。不是综述，也不因问卷与访谈先后顺序随机化而称为干预RCT。
- 全部样本组：VA三家门诊9513人，排除330人，9183人获寄基线HHQ，6116人回复；其中2875名过去一年至少饮酒五杯者获寄DPQ。从饮酒者加权随机抽取447人，重度饮酒者超额抽样2:1。排除无电话24人、未接听19人、病重或听力原因5人、女性6人，余393人；110人未返DPQ、18人未完成AUDIT-C、22人未完成访谈，最后243名男性进入分析。正文将参与者与204名未参与者比较。无另一个独立验证队列，三个访谈参照条件是同一样本中相互重叠的组，不是互斥病例对照。
- 物种：人（human）。
- 利益冲突：已读文末资助和作者单位说明，资助来自美国VA、University of Washington Alcohol and Drug Abuse Institute及VA Seattle相关项目；作者任职VA及华盛顿大学。未见独立利益冲突声明，不能写成“声明无冲突”；未见该问卷相关专利或商业受雇声明。

| 论文声称什么 | 补充表里实际有什么 | 代码仓库实际算什么 | 同名的另一个项目是什么 |
| --- | --- | --- | --- |
| 三题可用于识别重度饮酒及当前酒精相关问题 | 页面未列独立补充表；正文Measures包含全部题目、选项和权重 | 原文未链接代码；本技能按正文逐项计分并求和 | 十题完整AUDIT含其他内容，不由本技能替代 |
| 两个筛查切点有不同的灵敏度与特异度取舍 | Table 3为正文图表，图片访问失败；正文Results及Comment印出切点 | 仅比较总分与切点，不输出人群灵敏度或个体概率 | 后续女性验证、改动单次杯数及标准杯定义的版本不在本次方法内 |
| 研究有选择和回复偏倚，需其他人群确认 | 不是另有女性或外部验证样本的补充表 | 性别仅用于适用性说明，不生成女性阈值 | 后来同名计算器不是本论文代码来源 |

## 访问记录和材料清点

- 本机未提供浙大缓存目录，因此没有缓存文件被复制进仓库。
- 已完整阅读[JAMA文章页及全文](https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/208954)，包括Methods、Results、Comment及文末说明；[PubMed条目](https://pubmed.ncbi.nlm.nih.gov/9738608/)用于核对发表类型和书目信息。
- 原有B级登记的理由是没有预测长期年龄相关结局，并非缺计分常数。本次按修订标准重判，以个人筛查读出为A依据。
- 页面查找Supplement未见结果；未列Appendix、eMethods、Supplementary Tables、代码仓库或数据下载链接。以DOI加supplement、code、data、GitHub、Zenodo、OSF进行检索，未发现属于本研究的新增发布物；命中后来引用本文的研究不能当作本论文补充材料。
- 正文说完整DPQ可向作者索取，页面无对应下载；没有获取，也不假定其内容为空。本技能只用正文已完整打印的三题，不要求完整DPQ。
- Table 1标题为Demographic and Clinical Characteristics of Participants and Nonparticipants；Table 2为AUROCs and Corresponding Statistics；Table 3为Performance of Screening Questionnaires Compared With 3 Comparison Standards；Figure 1为ROC比较图。图片未读到，不能记录其列名或表内数据为已核对。
- 逐一尝试这四项的View Large与Download链接，浏览工具返回cache miss；CDN带签名与无签名链接直接请求均返回403；旧JAMA data/Journals图片路径亦不可访问。对应资源为 `ioi70602t1.png`、`ioi70602t2.png`、`ioi70602t3.png`、`ioi70602f1.gif`，位于 `https://cdn.jamanetwork.com/ama/content_public/journal/intemed/5227/`。
- 直接HTTP取文章HTML遇到验证页；web-access的CDP依赖检查显示Chrome存在但代理连接超时。因此全文阅读使用浏览工具可访问的JAMA全文正文，未声称成功浏览图片。正文的全部计分及切点已读到，没有缺少计算参数。

所有输出数值只来自正文Measures的逐项映射及正文Results/Comment的切点，不从未打开的图表抄数。
