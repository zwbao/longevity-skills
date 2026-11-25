# 证据核查

论文：Paluch 等，Daily steps and all-cause mortality: a meta-analysis of 15 international cohorts，The Lancet. Public health，2022；7:e219–e228。

研究设计：PubMed（PMID 35247352）出版类型为 Journal Article、Meta-Analysis、Research Support, N.I.H., Extramural。15个人体前瞻性队列按统一方案进行研究内分析，再汇总研究层效应；不是个体数据合并建模或随机分配步数的试验。包含8个当时未发表的队列分析，因此不是仅概述已发表研究的综述。schema 没有 meta_analysis，evidence 使用 cohort 表示基础证据设计。

全部样本组：正文主表合计47471人、3013例死亡，中位随访7.1年，总297837人年。没有另设模型训练组、外部验证组或病例对照样本。较低步数四分位是队列内参考组。所有15队列包括：

| 队列 | 人数 | 死亡 | 数据汇总时发表状态 |
|---|---:|---:|---|
| BRHS | 1397 | 240 | 已发表 |
| CARDIA | 2110 | 72 | 已发表 |
| NHANES | 2382 | 507 | 已发表 |
| NES | 416 | 76 | 已发表 |
| NNPAS1 | 3043 | 122 | 已发表 |
| Tasped | 2576 | 219 | 已发表 |
| WHS | 16741 | 504 | 已发表 |
| ActiFE | 1240 | 367 | 未发表 |
| ARIC | 452 | 25 | 未发表 |
| BLSA | 382 | 22 | 未发表 |
| CPS-3 | 720 | 6 | 未发表 |
| FHS | 4548 | 157 | 未发表 |
| HAI | 3793 | 138 | 未发表 |
| JHS | 401 | 87 | 未发表 |
| NAVIGATOR | 7270 | 471 | 未发表 |

样条分析排除使用低频扩展滤波的BLSA，含14队列；不是另一个验证人群。年龄亚组为<60及≥60，性别另行分层，7个队列报告步频指标。排除前两年死亡的敏感性分析含13队列（排除CPS-3和ARIC）。样本以高收入国家志愿者和白人为主；设备和佩戴位置有差异。

物种：人（human / adults），没有动物或细胞实验。

利益冲突：按 Declaration of interests 核对。AEP和CFP获得CDC本项目资助；BJJ获British Heart Foundation资助；MRC和RSV获NHLBI/NIH资助；I-ML、KPG、PP获NIH资助；KRE获NIH、Robert Wood Johnson Foundation、美国及北卡交通部门资助，获得NIH咨询费并任ACSM理事；DD获德国研究基金会资助、老龄会议旅费、波士顿大学授课酬劳，另有无偿演讲和校友理事角色；JS获NIA/NIH资助。其他作者声明无利益冲突。声明未列出本文计步干预或设备相关专利/雇佣。资助方CDC参与研究设计、解释和写作，未参与数据收集或分析。

| 论文声称什么 | 补充表里实际有什么 | 代码仓库实际算什么 | 同名的另一个项目是什么 |
|---|---|---|---|
| 日均步数增加与较低全因死亡风险关联，平台范围随年龄组不同 | 图S2c第19页用统一参考值仍显示老年组约6000–8000、较年轻组约8000–10000；图S2b是各队列四分位中位数图 | 未提供公开仓库；数据和分析代码需申请。本地只比较印出的范围 | 未使用其他同名项目、后续论文或第三方计算器 |
| 四分位HR为人群层关联 | S3列HR及95% CI；S1a/S2a为森林图；没有个人风险计算表 | 不将四分位中位数视为个人切点，不拟合曲线 | 不使用其他步数研究的阈值或效果 |
| 步频独立关联并不一致 | S4–S7给不同步频指标的森林图及中位数，方案说明残差调整 | 本地不算步频风险 | 不借用实验室步频处方 |
| 研究存在残余混杂、反向因果和设备误差 | S4、S5与S8–S11为敏感性结果；S1a列设备和有效佩戴规则 | 本地不做设备校准，也不将观察关联改写为因果预测 | 未引入其他设备算法 |

## 打开的材料与表头

2026-11-25核查。无用户提供的本地全文缓存目录。DOI/期刊页返回访问限制；PMC作者接受稿完整HTML可直接读取，明确标记最终期刊版本为2022年。PMC附录链接出现下载验证页；从出版社静态附件地址成功取得完整PDF并提取阅读。未把全文或附件复制进仓库。

- [文章全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC9289978/)：Methods、Results、Discussion、主表、Figure 1–4图注、Data sharing与Declaration of interests。
- [期刊入口](https://www.thelancet.com/journals/lanpub/article/PIIS2468-2667(21)00302-9/fulltext)：403，未假称从该页读取了正文。
- [唯一附录](https://ars.els-cdn.com/content/image/1-s2.0-S2468266721003029-mmc1.pdf)：封面及编号第1–60页；PMC对应文件名为 NIHMS1787838-supplement-MMC1.pdf。
- S1a，第3–4页：Study、Case Ascertainment、Device Type / Settings / Instructions、Stepping Metrics Included、Device Wear Criteria、Summary of Covariates。
- S1b，第5页：Study、Detailed Description of Covariates in Final Model。
- S1c，第6–9页：各研究和性别列；N、Age、BMI、race/ethnicity、慢性病、Average Steps/day、compliant days、minutes/day of wear等行。
- S2，第10–11页：Study、Selection、Comparability、Outcome、Overall Score及评分定义。
- S3，第12页：四分位对比的Fixed/Random、HR、95% CI。
- S1–S3图组，第13–23页：总体、年龄、性别森林图、漏斗图、样条及四分位中位数；S2c页面图像另行核查。
- S4–S7图组，第24–27页：步频森林图和四分位中位数。
- S4，第28页：Steps/d Quartile、Total、deaths、HR [95% CI] Model 1/2。
- S8–S10，第29–32页：早期死亡剔除、随访期和发表状态分析。
- S5与S11，第33页：Study left out、HR、95% CI及leave-one-device-out曲线。
- 第34–60页：研究方案及待填写的表壳。第39页为日均数定义；第54页Table 3列Model 1–4、HR (95% CI)；第59页Table 5B分年龄组列Median [IQR]、n Events/n Total、Person years、Cases per10000 person-years、Model 1/4 HR。空白表壳不是已发表的系数或个人算例。

没有发现其他补充文件或已发布代码/数据地址；Data sharing 的按申请提供不能记成已下载。Europe PMC补充文件接口也尝试过，但实际使用的是出版社PDF。

## 不一致与处理

正文主表ActiFE为1240、NAVIGATOR为7270；附录S1c按性别列分别合计1241、7271。这里使用正文主表总数，未静默修正附录。S3页脚写“k=14 studies (all included)”与正文15队列总分析不同，其最高四分位CI下端印0.38，摘要印0.39；不将S3混用为个人风险模型。附录第39页Peak 60-min定义误写30分钟，正文定义为60分钟；本技能不使用步频。以上不影响两处一致印出的年龄范围。

图S2c图注直接给出两个平台范围，但没有个人算例。保留draft，测试不以群体HR或软件自算结果充当论文复现。
