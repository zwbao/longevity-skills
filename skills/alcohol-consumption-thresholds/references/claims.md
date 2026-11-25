# 来源核查

- **研究设计**：原创人体前瞻性队列个体数据合并分析（含嵌套病例对照及EPIC-CVD case-cohort设计），不是饮酒干预试验或综述。PubMed PMID 29676281；Wood等，Lancet 391(10129):1513–1523，2018。分析软件Stata 14.2/15.1不等于公开了分析程序。
- **全部样本组**：主分析599,912名当前饮酒者，ERFC 247,504（81项研究）、EPIC-CVD 26,036（22个中心，作为1项研究）、UK Biobank 326,372（1项研究），合计83项研究、19个高收入国家。可用信息总计786,787人，排除基线不饮酒的186,875人。正文同时把186,875标为19%，与上述分母不相符；保留人数，不使用该百分比。无单独训练/验证集。重复测量/终生暴露校正子集71,011人、37项研究、152,640次测量，不是新增独立样本。eTable 2另外展示能区分的ex-drinkers 29,726和never-drinkers 53,851，不等于所有排除者。
- **物种**：人（human）；未做动物或细胞实验。
- **利益冲突**：已核对正文pp1521–1522 Declaration of interests，不能标“无”。ASB有研究外Merck、Biogen、Bioverativ、Novartis、Pfizer资助；BMP参与Zoll LifeCor试验DSMB及Johnson & Johnson资助YODA项目；HMK报告Janssen/Medtronic数据共享研究协议、UnitedHealth/IBM Watson/Element Science/Aetna个人费用、Hugo平台、FDA/Medtronic资助及CMS合同；JD报告Merck、Novartis、Pfizer、AstraZeneca等资助或咨询/非财务支持；OHF有Nestle、Metagenics研究外资助；WK有AstraZeneca、Novartis、Pfizer、The Medicines Company、GSK、DalCor、Sanofi、Berlin-Chemie、Kowa、Amgen个人费用及Roche Diagnostics、Beckmann、Singulex、Abbott资助/非财务支持。ML报告NIH、National Kidney Foundation及Johns Hopkins NIH资助；SKi报告VASCage公共资助。ASB、EDA、JD、MS、SGT、SKa、MD、EB、NvS、PJN等还报告文中列明的公共/慈善资助（MRC、BHF、NIHR、EU/ERC、日本JSPS、澳大利亚NHMRC、荷兰卫生部门、NIH）；其余作者声明无竞争利益。文中未列本方法专利或饮酒干预产品。

## 材料与访问记录（2026-11-25）

本机没有用户指定的浙大缓存根目录，未复制任何缓存文件。以下PDF仅下载到`/tmp`阅读，没有放入仓库。

| 材料 | 访问与核查 |
|---|---|
| [DOI](https://doi.org/10.1016/S0140-6736(18)30134-X)、[Lancet文章页](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(18)30134-X/fulltext)、[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S014067361830134X) | 尝试打开，403；浏览器CDP连接检查超时，继续使用公开副本 |
| [PubMed](https://pubmed.ncbi.nlm.nih.gov/29676281/) | 核对书目及PMCID；直接抓取受限，搜索索引可读 |
| [UCL记录](https://discovery.ucl.ac.uk/id/eprint/10055938/)及[全文PDF](https://discovery.ucl.ac.uk/id/eprint/10055938/1/1-s2.0-S014067361830134X-main.pdf) | 已完整下载、读正文及表图；11页，首页注明2018-05-31修订版，CC BY 4.0 |
| [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5899998/) | 常规路径出现验证码；`/articles/5899998/`可读全文与附件清单，清单只有一个mmc1.pdf |
| [Europe PMC](https://europepmc.org/articles/PMC5899998)与REST检索 | 页面403、REST请求超时，不作为数据依据 |
| [Supplementary appendix](https://ars.els-cdn.com/content/image/1-s2.0-S014067361830134X-mmc1.pdf) | PMC附件链接遇验证码，Elsevier CDN成功下载49页（封面+编号1–48），核对Annex 1–6、eTable 1–10和eFigure 1–22目录及相应页；Annex 4、eFigure 13与22重点核查；图形页34、47已渲染检查 |
| [UK Biobank原问卷链接](https://biobank.ctsu.ox.ac.uk/crystal/docs/TouchscreenQuestionsMainFinal.pdf) | Annex 1引用的采集工具；旧链接返回HTML，不是可读PDF。未从它取任何参数，所需8克单位在Annex 1直接印出 |

全文PDF SHA-256：`f5a7e41acd12dbc6c58a532a03018b388f4fcae8a0ed894c41cde815ebaa4e43`。
附录PDF SHA-256：`b9f95a8b0b9e9387facafe865e825e3a10e803b41a12255f6c8d86fb3b6174cb`。

## 补充材料内容与列

附录pp1–2说明ERFC/EPIC-CVD/UK Biobank饮酒量统一方法；pp3–4为研究简称；p5列End point与ICD-10 codes；pp6–7为寿命模型公式；pp8–9为表图目录；p48为研究者名单。

| 表/页 | 已核对的列或内容 | 本技能用途 |
|---|---|---|
| eTable 1 pp10–11 | Study、Ascertainment method、Format、Calculated or Reported | 确认自报/问卷来源，非个人换算表 |
| eTable 2 p12 | 暴露组；Characteristics；N；Mean(SD)/% | 背景人群和非饮酒者差异 |
| eTable 3 p13 | Study、Participants、Deaths、各心血管结局事件数 | 人群事件，不作个人风险 |
| eTable 4 p14 | ERFC、EPIC-CVD、UK Biobank；all participants与repeat/lifetime measurements；Number、Mean | 区分基线量与校正usual量 |
| eTable 5 p15 | Level of adjustment；各CVD结局HR(95%CI) | 协变量敏感性，不作为生存模型系数 |
| eTable 6 p16 | 肺癌/消化系统癌；Level of adjustment；cohorts/events；HR(95%CI) | 不用于输出 |
| eTable 7 p17 | 性别；Outcome；No. of events；HR(95%CI)；I² | 不把亚组结果写成个体效应 |
| eTable 8 p18 | Sensitivity analyses；Outcome；events；HR(95%CI)；I² | 不用于输出 |
| eTable 9 p19 | ≤2/>2饮酒天/周；Baseline characteristic；n；Mean(SD)/% | 周总量不刻画模式 |
| eTable 10 p20 | wine/beer/spirit；characteristic；n；Mean(SD)/% | 不据饮料类别更改切点 |
| eFigures 1–12 pp21–33 | 筛选、暴露分布、相关性、结局/性别/年龄/不饮酒者/插补等敏感性图 | 未数字化曲线 |
| eFigure 13 p34 | 死亡率二阶分数多项式曲线，未印出可调用系数 | 不重建曲线 |
| eFigures 14–21 pp35–46 | 固定效应、事件筛选、饮酒模式、研究/个人特征亚组、漏斗图 | 不作为额外参数 |
| eFigure 22 p47 | 超过/低于假设阈值的人群对比，男性112与196克阈值示例 | 与Figure 4四档对比定义不同，不混用 |

## 声称—实际材料—代码—同名方法

| 论文声称 | 附录实际提供 | 公开代码实际提供 | 容易混淆的方法 |
|---|---|---|---|
| 当前饮酒者中最低全因死亡风险约在100克/周或以下 | 分档、敏感性图、分数多项式方法 | 本文未链接GitHub、Zenodo、OSF或成品代码/系数文件 | 不是面向所有人的安全上限，非当前指南更新 |
| 较高周饮酒档与40岁起算寿命差有关 | Annex 4公式与eFigure 22另一种阈值对照 | 原始个体资料来自合作队列，并非公开个体数据包 | Figure 4四档查表不是重新拟合生存曲线；不与GBD酒精模型互换 |
| 每英国单位8克 | Annex 1 pp1–2直接印出 | 无需外部代码 | 一英国单位不等于一杯或其他国家标准杯 |

正文Table 1是基线人群，Table 2是协变量调整的HR，Figure 3是每100克**usual**量的相对HR；均不提供本人的绝对风险。公开数据源CDC WONDER/Eurostat是Annex 4寿命模型的外部死亡率来源，不是本技能运行依赖，未下载重建。无单独补充文件遗失；附录中引用的外部问卷旧链接不可读已如实注明。
