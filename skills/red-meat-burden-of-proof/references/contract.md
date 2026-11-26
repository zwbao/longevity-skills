# 产品合同与复现范围

1. 用户提供自己习惯性日均未加工牛、羊、猪肉摄入量（g/d），年龄及性别；可选提供自己指定的另一个摄入点。加工肉、总肉量、单顿摄入量不能替代这个输入。
2. 技能使用已核对并冻结到presets.py的Supplementary Table 7保守区间列，不要求用户找论文或公共数据，运行不联网。
3. 报告只返回已印出摄入点的人群相对风险、保守95%不确定区间和可选表值比较；不计算个人绝对风险、寿命变化、因果效应、最优摄入量或用药方案。

流水线任务已授权实现这一范围，不另设合同确认步骤。

## 可行性核查（先于实现）

论文：Lescinsky等，Nature Medicine 28:2075–2082 (2022)，DOI 10.1038/s41591-022-01968-z。2026-11-25访问。机器无用户指定的全文缓存；全部材料经公开来源读取，下载文件及克隆仅放/tmp，不入库。

- [期刊全文](https://www.nature.com/articles/s41591-022-01968-z)：已读结果、方法、数据/代码可用性、利益冲突。正文Table 1政策摘要与Table 2结果表均打开。主图1–4及Extended Data 1–4是曲线、漏斗图和流程图，不从图像拟合常数。
- [Supplementary Information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-022-01968-z/MediaObjects/41591_2022_1968_MOESM1_ESM.pdf)：下载并提取全文，打开Sections 1–7、Tables 1–8、Figures 1–8；表7印刷页39–40（PDF第40–41页）另渲染逐格核对。全部计算所需的54行均在表7印出。
- [Reporting Summary](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-022-01968-z/MediaObjects/41591_2022_1968_MOESM2_ESM.pdf)：3页扫描PDF，渲染及OCR阅读，核对25岁至95岁以上的研究对象和各结局样本数。期刊页面只列这两份补充文件，均已打开。
- [作者代码](https://github.com/ihmeuw-msca/burden-of-proof)，克隆commit `c8ad876a579cfd136850c13549aa706cd0fa2437`：阅读README、risks/red_meat下的README、prep_diet_data_function.R、model_functions.R、redmeat_aggregate_curve.R，并检查仓库文件列表。包含模型引擎、处理管线和抽样/汇总代码；红肉脚本使用FILEPATH、模型pkl和GBD draws等外部依赖，红肉目录没有已拟合完整模型。没有执行重新拟合。
- 正文链接的[limetr](https://github.com/zhengp0/limetr)（`f61b8170b24aae74dfbb1e8a59903b60daa78407`）及[xspline](https://github.com/zhengp0/xspline)（`c5f5fe6b0e89130156ebc3a7bc0fb3eab36e0674`）均克隆，阅读README与文件结构：通用混合效应回归与样条工具，不作为红肉数值来源。
- [Burden of Proof可视化与数据](https://vizhub.healthdata.org/burden-of-proof/)：打开页面和前端请求路径，取得metadata/risk、metadata/risk_cause，以及risk=116下cause=441、429、493、495、496、497、976的output_data、study_data、study_citations。路径为`https://vizhub.healthdata.org/burden-of-proof/api/v1/<endpoint>?risk=116&cause=<id>`。每个output_data有100个曲线点；study_data分别为115、49、43、31、35、35、99条；citation分别19、10、10、6、6、6、15条。页面当前分类把出血性卒中拆为两个cause，不用这些更新的接口数据替换2022年印刷表，也不混拼成论文模型。
- [Europe PMC元数据](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41591-022-01968-z&format=json&resultType=core)：出版类型含Systematic Review、Journal Article、research-article；PMCID PMC9556326，evidence填写review（系统综述/荟萃分析，无新受试者数据）。

CDP预检连接超时；公开全文及补充文件已用curl成功取得，不依赖浏览器登录。没有未下载的期刊补充文件。

## 表格合同与常数

|来源|列名/内容|是否用于计算|
|---|---|---|
|正文Table 1|Background; Main findings and limitations; Policy implications|解释证据边界|
|正文Table 2|Health outcome; ROS; Average BPRF; Star rating; RR at 50 g/d (conservative 95% UI); RR at 100 g/d (conservative 95% UI)|独立核对50和100两列；星级来自此表|
|补充Table 1|Outcome, Report, Study name, Population, Location, Study design, Sex, Follow-up, Age start/end, Exposure assessment, Endpoint, Disease ascertainment, Person-years, Events, Sample size|核对队列，无个人系数|
|补充Table 2|Report, Cohort name, Outcome, Exposure Measurement Score, Exposure Assessment Score, Outcome Assessment Score, Confounders Score, Quality Score|研究偏倚，不作个人评分|
|补充Table 3|Section and Topic, Item, Checklist item, Location where item is reported|PRISMA正文清单|
|补充Table 4|Section and Topic, Item, Checklist item, Reported (Yes/No)|PRISMA摘要清单|
|补充Table 5|GATHER检查项及对应位置|透明报告清单|
|补充Table 6|提取字段及说明；含effect_size、lower、upper、cohort_exp_unit_rr、cohort_exp_level_rr、参考组/对照、病例数等|数据提取模板，不是个人公式|
|补充Table 7|Outcome; Intake (g/day); Relative risk (conservative 95%UI); Relative risk (conventional 95%UI)|只使用保守列的RR、下限、上限；6个结局各9行|
|补充Table 8|Outcome; Report; Reference group exposure; Alternative group exposure; Log effect size; Log effect size standard error|原始研究估计，不混用为拟合结果|

没有缺少查表所需的系数、权重或切点。代码只是查表；无需完整样条参数，也没有尝试反推常数。表7的conventional UI不含研究间异质性，不用于个人报告。

## 参照点及原文异常

表7的缺血性卒中行在0 g/day为1.03 (0.98,1.07)，25 g/day为1 (1,1.01)。不能强行把零摄入设为1，也不能反推出精确最低风险摄入点。报告保存原表标度，不宣称六种结局统一以零摄入为参照。IHD零摄入的上限印为1.01，同样不修正。乳腺癌结果段落末尾出现“colorectal cancer”，结合本段标题与Table 2应属文字错写；本实现按表格结局名标为乳腺癌。

## 输入限制与目标比较

- 网格0、25、50、75、100、125、150、175、200 g/d来自表7，不是安全阈值。非表点、超范围均退出3；不取最近点，不插值、不外推，也不要求用户把实际值改成表点。
- 日均习惯摄入、生/熟重及份量的可比性由用户数据来源决定；论文没有统一个人生熟转换因子。原研究提取时对未说明份量使用的85 g假设不应用到个人食谱。不声明无法核实的LOINC。仅接受g/d，accept为空；未验证其他单位的换算不放入清单。
- 年龄只做适用性检查：研究为25岁以上成人；120岁是实现的质量检查上限，不是论文推导人群最大年龄。性别female仅控制乳腺癌适用性；male/unknown该结果为null，不从男女合并结果推算男性乳腺癌。
- `--targets`只允许同一输入的已印出点。levers.json的`current`与`targets.outputs`均为完整原表输出，`levers[].delta`只给RR均值之差，绝不相减区间端点伪造差值区间。
- 敏感度是邻近已印出表点及RR差；`derivative:null`明确不存在连续导数。没有对未印出点的风险方程。目标比较是对表值做算术，不是减肉干预预测。没有从RR推绝对风险所需的个体基线发生率和预测时间窗。

## 先写测试，再写实现

先保存tests/test_manifest.py的Table 2和Table 7原文期望值并运行，确认因脚本尚不存在而失败，再实现脚本。Table 2独立覆盖50/100 g/d六个结局的全部36个数；S7覆盖全部54组三元组。精确比较印刷舍入值，不声称重现作者未舍入模型。另检查错误单位、缺项、范围、非表点、性别、年龄、目标输入及旧结果清理。validation的reproduced仅指已发表表值查询复现。

表格数据来自CC BY 4.0论文；presets.py是数值转录与中英名称映射，未复制全文或PDF。归属Lescinsky等(2022)，[许可证](https://creativecommons.org/licenses/by/4.0/)。
