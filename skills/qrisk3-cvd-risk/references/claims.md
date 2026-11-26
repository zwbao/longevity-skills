# 论文与可执行材料核查

研究设计：英格兰 QResearch version 41 的前瞻性开放队列，1998–2015年。分别建立男女 Cox 模型，并按诊所分出验证集；不是随机试验，不是中国居民验证。Europe PMC PMID 28536104 标记 research-article / validation study / journal article。卷期 BMJ 357:j2099（2017），作者 Julia Hippisley-Cox、Carol Coupland、Peter Brindle。

全部样本：1309家诊所，981家推导、328家验证。推导筛查8,602,833人，剔除缺Townsend 31,433人、既往CVD 344,669人、他汀使用336,928人，纳入7,889,803人（女性4,019,956、男性3,869,847）；验证筛查2,918,082人，分别剔除13,862、118,057、114,865人，纳入2,671,298人（女性1,360,457、男性1,310,841）。年龄25–84岁，推导有363,565个新发CVD事件、约50.8百万人年。验证集仍用同一医疗信息系统；不能称作跨国家独立验证。

物种：人（human；Homo sapiens为标准学名，原文使用patients），没有动物或细胞实验。

利益冲突：JHC为Nottingham临床流行病学教授、QResearch共同负责人及ClinRisk有偿董事；CC为Nottingham医学统计学副教授及ClinRisk有偿统计顾问；PB部分由NIHR CLAHRC West、Bristol Clinical Commissioning Group、West of England Academic Health Science Network资助。QResearch为Nottingham和EMIS的非营利合作项目。论文声明本研究无外部资助。不能写成“无利益冲突”。

| 论文声称 | 补充材料实际提供 | 代码实际计算 | 同名或相近项目 |
|---|---|---|---|
| A是QRISK2-2017；B加新风险因素；C再加SBP标准差 | 完整病例HR及B模型亚组表现、B模型年龄交互图 | 冻结C文件是男女模型C，含SD；仅10年生存率非零 | 不是QRISK2；不是不含SD的模型B |
| 新变量除HIV/AIDS外入模 | HR和验证统计而非一整套机器系数 | C源提供完整高精度中心化、主效应、类别、交互和基线生存率 | 不采用非官方R包的重写系数，也不使用现行网页默认值 |
| 良好校准/区分度，整体表现与QRISK2接近 | 补表6按年龄、族裔和疾病给出均值及95%CI | 本技能只算个人模型预测，不重训/不再现队列级表现 | 不是诊断、ASCVD-only/死亡风险或心脏年龄 |
| 表6及图3/4列临床示例 | 没有补齐Townsend或网页缺失值处理 | 本工具要求明确Townsend，不作静默估计 | 不以第三方或线上计算器输出来冒充论文印出值 |

## 材料逐项访问记录（2026-11-25）

无用户指定的本地全文缓存。BMJ文章页及related/supplement入口多次返回403，作者Nottingham仓库PDF也遇验证页；PMC常规页面受reCAPTCHA影响。成功读取 Europe PMC REST fullTextXML（完整正文、Tables 1–6、图注、利益冲突、数据共享声明），之后PMC带查询参数的文章页也成功取得。全文只留临时目录，没有将PDF或全文缓存复制进仓库。

- 全文：https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5441081/fullTextXML
- 两个补充文件：Europe PMC `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5441081/supplementaryFiles`，长时间响应后成功下载ZIP；包含 `hipj036510.ww.pdf`（15页，469524字节）、`hipj036510.wf1.pdf`（8页，222637字节）和正文图片。此前BMJ、PMC、Europe PMC普通PDF路径的失败不再视为材料缺失。
- 正文Figures 3/4：从PMC官方CDN下载并目视核对勾选项、数值和空白邮编，ZIP还提供同图；不以图注替代截图检查。
- 原始C：论文所指向qrisk.org旧源代码入口现404。克隆公开存档仓库sisuhealthgroup/qrisk3并冻结其 `src/lib/original/qrisk3.c`；头部明确Copyright 2017 ClinRisk Ltd、LGPL v3及附加展示声明。原始SVN路径由该头部记录，但没有声称今天访问到了SVN。只使用原始C，未使用库的JS重写。
- 论文没有提供可公开下载的个人级QResearch训练数据或GitHub/Zenodo/OSF数据仓库；Data sharing指向开源算法。计算不需要训练数据。

## 已打开表的列名与用途

| 材料 | 列/轴 | 参数可用性 |
|---|---|---|
| 正文Table 1 | Characteristics；Derivation / Validation cohort；Women / Men；计数、百分比、Mean(SD) | 队列描述，不能替代中心化常数 |
| 正文Table 2 | Age group；Women / Men；Incident cases；Person years；Rate (95% CI) | 发病率而非个人风险样例 |
| 正文Tables 3/4 | Predictor variables；Model A / B / C adjusted HR (95%CI)，性别分表；脚注变换及交互列表 | 可核对逐项HR，不能从表单独实现全部绝对风险 |
| 正文Table 5 | Model A/B/C，Women/Men；D、Harrell C、R²及95%CI | 验证指标 |
| 正文Table 6 | Characteristics；Examples 1–6；性别、年龄、BMI、比值、SBP、族裔、吸烟、全部病史、SD、A/B/C风险 | 缺Townsend；第6例SD是No |
| 补表1，PDF pp1–5 | Group Name；ReadTerm；ReadDesc | 冠心病、卒中/TIA诊断编码，不是回归系数 |
| 补表2，p6 | Women / Men；CVD cases；pyrs；age standardised rate per 10,000 pyrs；total cases；total pyrs | 族裔发病汇总；不用于个人公式 |
| 补表3，p7 | event type；GP/HES/ONS data及col %；total；GP data only及row % | 事件首次数据来源 |
| 补表4，pp8–9 | model B complete case 1；model B complete case 2；Model C complete case；adjusted HR (95%CI) | 完整病例敏感性分析，不是主要多重插补模型 |
| 补表5，pp10–11 | 同上；含erectile项 | 同上 |
| 补表6，pp12–13 | Sub-group；statistic；Women / men mean (95% CI) | B模型分层D、Harrell C、R²；非个人风险输入输出 |
| 补图PDF pp1–8 | age / BMI vs adjusted hazard ratio；年龄×糖尿病、Townsend、家族史、AF、SBP、CKD、ED、激素、偏头痛、SLE及吸烟类别 | 正文称模型B；图像没有完整系数表或个人绝对风险示例。后几页为空白/分页残页，逐页渲染检查过 |

排版/信息不一致保留说明：补表4标题也印作“men”，但没有ED且与正文对补表4/5的男女描述不一致；不靠该标题决定模型性别。正文Table 2列标题写per1000而补表2写per10,000，不用这些发病率作公式。正文印度人年印8,819,177，而补表2 total pyrs为819,177；此汇总差异不进入个人计算。抽取事实以注明出处为准，不擅自修正模型常数。

边界：这是英国人群观察性模型的估计，仍在验证，不能替代医生评估，也不能证明改变某项就能获得对应治疗收益；不能据此开始、停止或调整药物。
