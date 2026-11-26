# 论文、附录与实现核查

**研究设计**：GBD 2017的人群比较风险评估（comparative risk assessment），
整合饮食调查、国家销售/食物供应资料及既有前瞻性观察研究荟萃分析，建模疾病负担。
这是产生新估计的系统分析，非随机试验，也不是只有文献总结的综述；manifest使用`method`。
出处为 Lancet 2019;393(10184):1958–1972；PubMed PMID 30954305，Europe PMC
PMC6899507。Europe PMC核心元数据的出版类型为Journal Article、research-article及
Research Support, Non-U.S. Gov't，未标为Review。作者为 GBD 2017 Diet Collaborators。

**全部样本组**：估计覆盖195个国家、21个GBD区域、1990–2017年、25岁及以上男女。
饮食调查入选时间为1980-01-01至2016-12-31，要求全国或次全国代表性，
排除非随机样本、特殊亚群、每5岁年龄-性别组不足20人的调查及非英文文献。
输入还包括Euromonitor销售、FAO供应量、Global Nutrient Database及24小时尿钠。
相对风险主要来自前瞻性队列荟萃分析；没有一组可统一报告人数的训练/验证病例对照队列。
正文没有给出这些来源合并后的独立个人总数，本技能不虚构总N。
正文另用美国NHANES个体数据做饮食因素相关性敏感性分析，未给该分析样本N；
它不是本技能的个人验证集。参考表的数据国家覆盖指数多数94.9%，加工肉/含糖饮料/
反式脂肪36.9%，尿钠26.2%，不是人的覆盖率。

**物种**：人（human，Homo sapiens）；本论文没有自己的动物或细胞实验。

**利益冲突与资助**：资助为Bill & Melinda Gates Foundation，作者声明资助方不参与
设计、收集、分析、解释或写作。正文 Declaration of interests 已核对，不能写成“无”：
JMG有Unilever资助；LJ有Mills Scientific Council个人费用；SL有Amgen、Berlin-Chemie、
MSD、Novo Nordisk、Sanofi-Aventis、Synlab、Unilever、Upfield费用及Preventicus非财务支持，
并任德国营养学会科学委员会成员和脂肪指南共同作者；WMä有Siemens Diagnostics、
Aegerion、Amgen、AstraZeneca、Danone Research、Pfizer、BASF、Numares、Berlin-Chemie
资助及费用，Hoffmann LaRoche、MSD、Sanofi、Synageva费用，Abbott Diagnostics资助，
并受雇于Synlab Holding Deutschland；WMe任UNFPA秘鲁项目分析员，机构不必然认可研究。
RMi有NIH、盖茨基金会、Unilever资助及World Bank、Bunge费用。
DM有NIH和盖茨基金会资助；GOED、DSM、Nutrition Impact、Pollock Communications、Bunge、
Indigo Agriculture、Amarin、Acasti Pharma、America's Test Kitchen费用；
Elysium Health（含股票期权）、Omada Health、DayTwo顾问角色及UpToDate版税；
是Tufts持有、尚未许可的反式棕榈油酸相关专利US8889739和US9987243共同发明人。
CDR有Dairy Management Institute费用；AES有IEM、Novartis、Servier、Abbott费用；
AGT有澳大利亚NHMRC资助。其余作者声明无利益冲突。

## 文件与访问记录

2026-11-25核查；下载均留在任务临时目录，未把完整论文或缓存文件放入仓库。

| 来源 | 实际访问结果与用途 |
|---|---|
| [DOI](https://doi.org/10.1016/S0140-6736(19)30041-8)、[Lancet全文](https://www.thelancet.com/article/S0140673619300418/fulltext)、[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0140673619300418) | 尝试打开文章页，403；没有只依赖摘要 |
| [PMC文章页](https://pmc.ncbi.nlm.nih.gov/articles/PMC6899507/) | 标准入口有验证码；`?pdf=1`入口取得完整HTML并检查所有补充链接，只有mmc1.pdf |
| [Europe PMC全文XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6899507/fullTextXML) | 已下载并读取全部正文、表、附录引用和声明；唯一supplementary-material为mmc1.pdf；无独立GitHub/Zenodo/OSF链接 |
| [Monash机构期刊版PDF](https://researchmgt.monash.edu/ws/files/280108765/280108522_oa.pdf) | 已下载，15页全文；第3页表格逐项视觉核对 |
| [Oxford ORA](https://ora.ox.ac.uk/objects/uuid%3Aa5dae6f5-7460-49e3-b541-81ecc6d8c30e) | 403，未作为数据来源 |
| [出版商补充附录](https://ars.els-cdn.com/content/image/1-s2.0-S0140673619300418-mmc1.pdf) | 直接下载成功，94页；提取全部文本，读取方法、Tables A/B及Supplemental Tables 1–10和Figures 1–6结构；没有其他Supplementary Tables文件 |
| [2021年更正](https://pmc.ncbi.nlm.nih.gov/articles/PMC8267852/) | 已读取；补入作者Nayu Ikeda，未更改参考表 |
| [GHDx](https://ghdx.healthdata.org/)、[GBD 2017数据来源清单](https://ghdx.healthdata.org/gbd-2017/data-input-sources) | 尝试访问，403；没有把打不开写成无数据；未下载个体数据 |
| [Global Nutrient Database](https://nutrition.healthdata.org/global-nutrient-database) | 尝试访问，工具无法打开；未用于本技能 |
| [Euromonitor](https://www.euromonitor.com/) | 尝试访问，403；销售数据未下载，非本技能依赖 |
| [FAO food balance sheets旧链接](https://www.fao.org/economic/ess/fbs/en/) | 打开后转到FAO统计部门页；并非本论文特定数据下载，不作为个人换算参数 |

没有可克隆的作者代码仓库链接。论文正文说Python 3.5，附录说线性模型用R的lmer4、
ST-GPR用Python的PyMC2；这些是分析工具说明，不是发布好的个人预测模型。
本技能仅需印出的最终15行表，不执行上述人群模型。

## 附录内容与列名审计

页码为附录内部页，PDF页号需加1。

| 部分 | 列或主要内容 | 与个人读出的关系 |
|---|---|---|
| Table A，p3 | dietary factor；Sales、FFQ、HBS、FAO；Country level covariate | 输入源和国家协变量，不是个人评分权重 |
| Crosswalks，p3–4 | 跨调查来源校准方程；膳食钠→尿钠的multiplier描述 | 未印出这个钠乘数；不做此换算 |
| ST-GPR及分布方法，p4–7 | 均值、方差、分布家族及ensemble方法 | 人群重建步骤，不是个人输入公式 |
| Table B，p7–8 | dietary factor；BMI、Total Serum Cholesterol、Fasting Plasma Glucose、Systolic Blood Pressure | 代谢中介的有无，不是加分表 |
| TMREL，p8 | 疾病最低风险暴露按全球死亡负担加权，指回正文Table | 直接使用正文最终值；不反推分疾病权重 |
| PAF，p8–9 | 暴露分布、RR、TMREL、病因死亡/DALYs及中介矩阵描述 | 不实现个人PAF或寿命预测 |
| Supplemental Table 1，p11 | 风险-结局；队列/试验/病例对照证据数量及方向、剂量反应、机制支持、证据等级 | 证据审计，不是个人病例数据 |
| Supplemental Table 2，p12–13 | Risk、Outcome、Citation/Note | 已打开；所引荟萃分析，不提供个人摄入例子 |
| Supplemental Table 3，p14–15 | Risk–Outcome、Category/Units、Morbidity/Mortality、Sex、25–29至95+岁RR及区间 | 有人群关联RR，但本技能不据此输出个人风险 |
| Supplemental Table 4，p16 | Measure、Cause；DALYs/Deaths各1990/2017 | 全球结果，不是给定个人输入的预测值 |
| Supplemental Table 5，p17–21 | Location Name、Cause；DALYs/Deaths各1990/2017及UI | 地区/SDI年龄标准化率 |
| Supplemental Table 6，p22–25 | Location Name、Cause；DALYs/Deaths各1990/2017及UI | 地区/SDI比例 |
| Supplemental Table 7，p26–53 | Location Name、Cause；DALYs/Deaths各1990/2017及UI | 国家率 |
| Supplemental Table 8，p54–80 | Location Name、Cause；DALYs/Deaths各1990/2017及UI | 国家比例 |
| Supplemental Table 9，p81–83 | Risk、Cause、Measure、Attributable burden (95% UI) | 各饮食风险的全球疾病负担 |
| Supplemental Table 10，p84–87 | Risk、Location、Measure、Attributable burden (95% UI) | 各SDI层的年龄标准化负担率 |
| Supplemental Figures 1–2，p88–89 | 估计流程图、ST-GPR流程图 | 不提供新的个人换算常数 |
| Supplemental Figures 3–6，p90–93 | 地区与20个人口最多国家的饮食风险死亡/DALYs排序 | 人群排序，不能用于给个人项目加权 |

## 声称、材料、代码和同名方法

| 论文声称 | 补充材料实际内容 | 本技能实际计算 | 同名或相邻方法 |
|---|---|---|---|
| 15项食物/营养素暴露与最低风险参考点 | 附录TMREL段解释加权方法，最终表在正文 | 个人记录减正文参考点，及除以参考点的比例 | 不是HEI、AHEI、DASH或地中海饮食评分 |
| 人群饮食风险与慢性病负担有关 | Tables 3–10为RR、归因负担及不确定性 | 不算个人死亡概率、DALYs或风险下降 | 不是GBD后续年份的更新表，也不是现行膳食指南 |
| 原始摄入与参考水平之间存在差距 | 正文结果给全谷物29 g/23%、牛奶71 g/16% | 用印出的输入与参考点按舍入精度复现 | 不是训练/外部验证了个人营养诊断 |
| 钠采用24小时尿钠口径 | 跨来源校准乘数未印出，参考区间1–5 g/d | 只比较完整24小时尿钠 | 不把膳食盐重或随机尿当作24小时排泄 |

参考值在本研究的历史建模框架内使用。观察研究残余混杂、食物定义不一致、
输入测量误差、能量替代未明确、部分数据缺失和食物间相关性都限制个人解释。
本技能没有把总体死亡负担、地区排序或验证误差放进个人结果。
