# 来源与可行性核查（2026-11-25）

没有用户所述的图书馆缓存目录；未将全文缓存、PDF、OSF原始附件或研究仓库复制进本技能。所有取证临时文件留在技能目录之外。运行数据只有作者发布的22条数值曲线，以及本技能的合成示例CSV。

## 正文及附件逐项检查

| 来源/文件 | 实际访问结果与读取内容 | 计算依赖 |
|---|---|---|
| [BJSM正式文章页](https://bjsm.bmj.com/content/57/15/979) | 直接访问403；对应正式发表全文从[PMC10423495](https://pmc.ncbi.nlm.nih.gov/articles/PMC10423495/)成功取得HTML并读取正文、表1、图注、利益冲突、补充材料目录；不是只有摘要 | 强度、适用条件、22个结局的独立验证数值 |
| [bjsports-2022-105669supp001.pdf](https://pmc.ncbi.nlm.nih.gov/articles/instance/10423495/bin/bjsports-2022-105669supp001.pdf) | 期刊列出的唯一补充PDF；BMJ highwire 131452及版本化DC1链接403，PMC附件链接返回验证码。Europe PMC `/webservices/rest/PMC10423495/supplementaryFiles`返回ZIP但240秒中断；从已传输PDF流恢复了全部20页并逐页取文本，图像页9、11及偏倚图另渲染读取。原始ZIP/PDF下载不完整，未把恢复件当作原始附件分发；尾部字体表有恢复警告 | eMethods 1–6、eFigure 1、eResults 1–4、参考文献已查看；页9强度例图可清楚读取；没有用恢复文本中的乱码数字作常数 |
| [OSF PNVDC目录](https://osf.io/pnvdc/) | 直接页面/API403；经Jina读取OSF公开项目及API目录，确认以下四个文件，非“没有补充内容” | 发现与核对文件清单 |
| [Details of included studies and original and harmonized exposures.xlsx](https://osf.io/3nhxe/) | 原文件下载接口403；打开OSF的MFR渲染预览读取可见行。列包含研究/类别标识、作者、年份、队列、国家、结局、样本量、年龄、随访、共病和早期事件处理、插补、活动领域、原始单位/类别、统一mMET值及换算说明。预览如Nunez 2018 / 45 and Up Study为226584人，分钟类别转中等强度mMET。没有宣称遍历下载完整工作簿 | 不用于个人计算或重新拟合；最终曲线齐全 |
| [List of excluded articles.xlsx](https://osf.io/6dm3b/) | 原文件下载403；OSF MFR预览可读题名、作者、年份、期刊、卷期页、DOI与排除原因，例“All outcomes out of review’s scope”。没有宣称读取全部工作表行 | 无计算依赖 |
| [MOOSE checklist.docx](https://osf.io/4gpr7/) | 经公开下载链接的Jina转换读取3页、35项报告核对清单及对应页号 | 无计算依赖 |
| [Exposure harmonisation flowchart.tiff](https://osf.io/8wy9f/) | 原TIFF下载403；打开MFR转换的单页PDF查看器，通过渲染截图实际查看流程：非数值/区间转点值、按强度时长换算、去除职业活动、按体重换算、扣除静息消耗 | 与正文换算原则一致；不在个人输入中套用研究缺失值插补 |
| [作者Shiny公开界面](https://shiny.mrc-epid.cam.ac.uk/meta-analyses-physical-activity/) | 远程打开超时；完整源代码从以下GitHub仓库取得，数据源路径与查询函数已读取 | 不依赖在线界面 |

OSF预览途径为 `https://mfr.de-1.osf.io/render?url=https%3A%2F%2Fosf.io%2Fdownload%2F<guid>%2F%3Fdirect%26mode%3Drender`，文本/截图经`r.jina.ai`读取。读取不到的原文件不假称已经完整下载。以上受限原文件没有任何本计算尚缺的参数；个人计算使用的数据文件均完整克隆取得并逐文件哈希。

## 作者仓库与冻结数据

已克隆并读取：

- [meta-analyses/meta-analysis](https://github.com/meta-analyses/meta-analysis)，commit `0afc735e57ba7f92e2128b931ebe7e32685d747b`。检查README、`script/master_script.R`、`script/analysis.R`、`script/all-functions.R`、原始变量CSV、`data/output/rr-main-last-knot-0.75-analysis-total-pop.csv`和`data/csv/MA-DR/0.75/`。与表1对应22条曲线完整保存在本技能data/，每条1000行；未调整任何数值。主文件夹还含其他研究结局，不一并发布。
- [meta-analyses/meta-analysis-shiny](https://github.com/meta-analyses/meta-analysis-shiny)，commit `0ba05ea6cae82039a261f17c368433e9d67f7ab5`。检查README、setup.R、data-processing.R、server.R。`get_ma_table`对4.375、8.75、17.5分别使用`which.min(abs(...))`，再保留两位小数；这是本技能查询规则出处。

上游研究数据的每个文件URL和SHA-256在skill.json.data_files。GitHub仓库没有显式许可，故字段如实记为`redistributable: unknown`，不把文章CC BY自动宣称为代码仓库许可。冻结的是公开研究数值，不含研究者代码或参与者级数据。表1选取单元格由正式CC BY 4.0文章转录，已在table1.md注明出处、许可和选列处理。

## 可行性结论

本计算的全部常数来自正文，全部查表行来自作者公开CSV，全部复现期望值来自正式文章表1和补充页9。未使用未公开样条系数、未估计新权重、未拟合第三方结果。相关访问限制保留在上表，但没有造成所实现读出的参数缺口，因此可以实现并标为复现原文示例的A类。
