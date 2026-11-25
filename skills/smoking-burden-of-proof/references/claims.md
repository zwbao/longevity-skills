# 证据和材料核对

论文：Dai 等，Health effects associated with smoking: a Burden of Proof study，Nature Medicine **28**, 2045–2055（2022），DOI 10.1038/s41591-022-01978-x。经同行评审。Europe PMC/PMID 36216941出版类型为research-article、Journal Article、Research Support, Non-U.S. Gov't；不是随机试验，也不因使用系统检索就标成没有新分析的综述。本技能用`evidence=method`表述这篇对既有人群观察数据重新进行方法学荟萃分析的研究。

研究设计：系统检索和剂量反应荟萃分析；主曲线采用前瞻性队列和病例对照数据，心血管年龄模式另外纳入横断面数据。对照为从不吸烟或原研究报告的非吸烟组；原研究对照定义差异作为偏倚特征处理。没有本研究新招募的病例/对照，也没有独立个人风险验证队列。

全部样本结构：正文报告审查21,108条记录、纳入793项研究；Supplementary Table 3逐研究列出样本量、病例、对照、暴露组、随访和结局，不能跨重复队列简单相加成人数。Supplementary Table 5分别列出剂量反应559个unique sources、634个source–outcome组合、2,575条观察；心血管年龄模式159个unique sources、244个组合、1,318条观察。它们与正文793的计数口径不同，不能当作新增人数或独立训练/验证集。

正文详细示例：肺癌371条观察，25项前瞻性队列加53项病例对照，25个地区；COPD 51条观察，11项队列加4项病例对照，36个地区（表2却列13项研究，保留不一致，不合并）；2型糖尿病102条观察，24项队列加4项病例对照，15个地区；乳腺癌93条观察，14项队列加9项病例对照，14个地区；前列腺癌78条观察，21项队列加1项嵌套病例对照，15个地区。研究计数不作为个人结果。

物种：人（human / Homo sapiens）；没有本研究自己的动物或细胞实验。适用成人≥30岁；乳腺癌和宫颈癌仅女性、前列腺癌仅男性；其他结局未分性别或地点。

利益冲突：作者声明无竞争利益。资助来自Bill & Melinda Gates Foundation与Bloomberg Philanthropies；正文称资助方未参与设计、收集、分析、解释、写作或投稿决定。

| 论文声称什么 | 补充材料实际有什么 | 代码仓库实际算什么 | 同名的另一个项目是什么 |
|---|---|---|---|
| 当前吸烟与36个结局的关联，使用MR-BRT及BPRF | MOESM1完整PDF含Sections 1–9、Tables 1–11、风险曲线、敏感性分析及方法 | `risks/smoking/continous_risk`拟合曲线、生成抽样及年龄调整；`binary_risk`处理二分类 | 同系列其他Burden of Proof论文不是本论文，不借用其系数 |
| 精确暴露点的平均RR和95%UI见正文表2 | Supplementary Table 8是原始研究的log RR/SE，不是模型的个人预测表 | 拟合依赖外部数据与模型输出路径 | VizHub是持续更新展示页，本技能固定使用2022表2 |
| 每个风险结局对的证据星级来自BPRF和ROS | Sections 4、6列曲线、离群值处理和单调约束敏感性 | 仓库有evidence-score计算流程 | 星级不是临床诊断或个人高危等级 |
| 心血管吸烟关联随年龄变化 | Section 5.2.2、Figures 2–4展示年龄模式与衰减因子图 | `05_01_age_rr_trend.R`、`05_02_age_specific_rr_curves.R`实施调整 | 本技能只用表2参考年龄，不从图像拟合衰减参数 |

## 已打开的文件与表头

- [期刊全文](https://www.nature.com/articles/s41591-022-01978-x)：包含Results、Discussion、Methods、Tables 1–2、Extended Data图注、Data/Code availability和利益冲突；同篇[Europe PMC全文](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9556318/fullTextXML)用于结构化核对表值。期刊页列出的独立补充文件共两份，均已下载打开。
- [MOESM1 Supplementary Information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-022-01978-x/MediaObjects/41591_2022_1978_MOESM1_ESM.pdf)：Sections 1–9均已定位。Table 1为结局及定义；Table 2为Extracted variable/Extraction guidance；Table 3含Cause、NID、Underlying NID、Author、Year、Study name、Population、Location、Study design、Sex、Study Follow-up、Age start/end、Exposure assessment、Endpoint、Disease ascertainment、Person-years、Events、Sample size、Outcomes、Cases、Controls、Control pool、Exposed；Table 4含研究标识和cv_adj_L0/L1/L2、cv_exposure_study、cv_older、cv_subpopulation等偏倚列；Table 5是来源与观察计数；Table 6为Risk-outcome、Type of risk、Spline degree/# interior knots、Priors & constraints；Table 7为Risk-outcome、Unit of risk、Selected bias covariates、Mean gamma solution；Table 8为Cause、NID、Outlier flag、Reference exposure、Alternative exposure、Log relative risk、Log standard error；Tables 9–11是PRISMA和GATHER清单。
- [MOESM2 Reporting summary](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-022-01978-x/MediaObjects/41591_2022_1978_MOESM2_ESM.pdf)：3页图像PDF，已渲染并OCR阅读。核对了无原始招募、性别限定、样本结构、代码和数据链接。
- [作者代码](https://github.com/ihmeuw-msca/burden-of-proof)：已克隆，阅读README、smoking/config.R及吸烟计算流程；固定commit见合同。没有运行需要集群和原始数据的完整拟合。
- [作者数据展示](https://vizhub.healthdata.org/burden-of-proof/)：已打开网页及公开metadata/risk、metadata/risk_cause、metadata/env和肺癌output_data；字段risk、linear_cause、linear_cause_lower/upper、age_group_name、sex_name等。未把可变网页网格替代原表。

## 原文内部差异

摘要和Discussion为8个强至很强、21个弱至中等、7个无明确关联；Table 1政策摘要却写8/24/4。表2逐行星级与8/21/7一致；本技能只读取表2逐行结果。正文称5星例子包含外围动脉病，Table 1叙述却点名膀胱癌，故不从政策摘要重建星级。COPD研究数差异见上。正文Methods的抽样分位表述也有明显不一致（把95% UI的抽样顺序写成25th and 95th draws）；本技能直接使用印出的UI，不据该表述重算区间。Reporting summary的软件版本与正文不完全一致，与离线查表无关。

没有将原研究的预测误差、研究样本量或证据星级解释成个人风险；没有从不显著关联推导“安全”。
