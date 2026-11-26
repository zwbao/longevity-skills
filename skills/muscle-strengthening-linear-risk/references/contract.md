# 产品合同与可行性核查

1. 用户提供一个七天周期的力量/抗阻/自重训练总时长（分钟或小时）和实足年龄；可选提供目标周时长及性别。
2. 技能使用已核对并固定在 presets.py 中的表 1 线性 RR 和 95% CI；运行时无需下载，也不让用户寻找研究材料。
3. 报告只给四个主要结局相对零时长的线性模型群体关联，以及目标相对当前的同模型比较；不能给个人绝对风险、寿命、因果收益、最佳时长、药物或训练处方，也不能重建图 4 非线性曲线。

本次为用户授权的 LONGPI_PIPELINE 任务，按以上限定范围实现，无外部发布操作。

## 获取和打开的材料

核查日期：2026-11-26。用户指明本机无浙大缓存。原始文件只在 /tmp 中阅读，未复制到仓库。

- 期刊文章页：https://bjsm.bmj.com/content/56/13/755 以及早期上线页 /content/early/2022/01/19/bjsports-2021-105061。搜索索引返回正文片段，直接打开 403。
- PubMed：https://pubmed.ncbi.nlm.nih.gov/35228201/，核对 Meta-Analysis 出版类型、作者、卷期年 2022 和 PMC9209691。
- PMC HTML 遇浏览器检查；Europe PMC HTML 403。Europe PMC 全文 XML 成功下载并读取：https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9209691/fullTextXML 。核对方法、结果、表 1、图注、脚注及全文链接。
- 期刊主文 PDF 403；开放许可的原刊 PDF 镜像成功打开：https://todayspractitioner.com/wp-content/uploads/2022/09/Muscle-Strengthening-Study-PDF-1.pdf 。部分字体提取乱码，因此计算常数以 Europe PMC 全文 XML 表 1 为准，并核对原刊图 3。
- 期刊 Data supplement 1：https://bjsm.bmj.com/content/bjsports/early/2022/01/19/bjsports-2021-105061/DC1/embed/inline-supplementary-material-1.pdf?download=true 直接打开 403；旧式 suppl URL 与合并 with-ds PDF 亦未成功。
- 完整补充包成功下载：https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9209691/supplementaryFiles 。唯一附录为 bjsports-2021-105061supp001.pdf，共 38 页（作者 Haruki Momma）；解压后打开全文、提取所有表，并逐页渲染查看 pp.32–38 的七张补图。包内其余文件是主文图 1–5 的 jpg/gif，已查看图 3 和图 4。
- 全文和补充 PDF 没有命名或链接 GitHub、Zenodo、OSF 分析代码/数据项目；方法只写 Stata 17。不存在需要克隆的论文代码仓库。无未下载的补充文件。

## 附录清单与列

| 材料 | PDF 页 | 内容与列 |
|---|---|---|
| Appendix Table 1 | 1–5 | Ovid MEDLINE/Embase 检索步骤、Searches；无计算参数 |
| Appendix Table 2 | 6–8 | First author/year；NOS Selection、Comparability、Outcome 各项与 Stars |
| Appendix Table 3 | 9–11 | No. of studies、Study design、Risk of bias、Inconsistency、Indirectness、Imprecision、Publication bias、Other considerations、Participants/Cases、Relative effect (95% CI)、Certainty |
| Appendix Table 4 | 12–18 | 被排除的结局：作者、国家/队列、人群、结局/确认/例数与样本数、随访、暴露测量/分类、效应值、协变量、质量评分 |
| Appendix Table 5 | 19 | Reference、Main reason for exclusion；同队列重复出版物 |
| Appendix Table 6 | 20–31 | First author/year、Country/Cohort、Participants characteristics、Outcome/Case ascertainment/Case/Participants、Follow-up、Exposure measurement、Exposure category、Effect estimates、Covariates、Quality assessment |
| Appendix Figures 1–5 | 32–36 | 逐一排除、测量方式、NOS 质量、性别、CVD 结局类型的敏感性/亚组森林图；RR、CI、权重/异质性 |
| Appendix Figures 6–7 | 37–38 | 部位癌症两组及每十分钟线性剂量反应森林图；RR、CI、权重/异质性 |

## 使用的完整参数

正文表 1 的 Dose–response meta-analysis (10 min/week increase) 列：

| 结局 | RR | CI 下限 | CI 上限 |
|---|---:|---:|---:|
| All-cause mortality | 0.99 | 0.98 | 1.00 |
| CVD | 0.996 | 0.99 | 1.003 |
| Total cancer | 0.99 | 0.98 | 1.004 |
| Diabetes | 0.98 | 0.97 | 0.99 |

方法节明确分析研究特异线性斜率并采用随机效应合并，最低组为 none。按 log(RR) 线性模型，输入周分钟数 x 与参照 r 的换算为 `RR10 ** ((x-r)/10)`。置信端点采用相同幂变换；x-r 为负时排序端点。零时长相对零时长的 RR=1 是参照定义，不是绝对基线风险为零。目标情景以同一估计斜率计算时长差，不把当前/目标的不确定性当作独立估计。

这是已发表线性模型的数学换算，并不声称论文已验证任意个人时长下的预测。没有使用额外截距、绝对基线风险、拟合常数、图像数字化或外部输出。CVD 的 0.996 与图 3 舍入为 1.00 相容；总癌症 CI 上限用表 1 的 1.004 而非图 3 的 1.00。不同部位癌症未纳入产品范围。

`levers.json` 的敏感度为 `RR(x) * log(RR10) / 10`，单位是每增加一分钟周总时长的 RR 变化率；当前、目标、单输入变更的差值均是模型量，不是收益或优化建议。

输入 unit=min 指“一周总时长”，不是速率单位；h→min 因子精确为 60，匹配 schema/units.json。时间范围 0–10080=7×24×60 仅防止超过一周物理时间预算，绝不作为模型支持范围。18 岁是纳入年龄下限；120 岁是软件排错上限，不是研究上限。年龄/性别不进入合并斜率。

## 复现范围及不能计算的内容

先写 tests/test_manifest.py::test_printed_table1_ten_minutes，将原文十分钟增量作为输入，表 1 四行的 RR/CI 作为期望，之后实现计算。容差 1e-12 只覆盖浮点误差；这个测试仅核查单位增量与原印常数，不是独立个体预测验证。目标比当前多十分钟的端到端测试也断言相同原印值。

图 4 是另一套限制性三次样条模型。方法仅给三个结点的百分位（10%、50%、90%），没有四个结局的完整结点时长、样条回归系数及协方差，也没有完整预测值网格；附录表 6 是原研究分类效应，不是已拟合样条参数。正文/图 4 的极值注释不能代替这些参数。技能不拟合或重建样条，也不让线性模型去复现图 4 的极值。线性与非线性模型结果不同，报告必须显示这一点。因此当前实现的每一个计算常数都有原文位置，而非线性模型明确在合同外。

来源材料检查在实现前完成；原始文件未收入仓库，常数转录及核查文字保留出处。原文开放许可 CC BY 4.0。
