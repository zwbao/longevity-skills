# 产品合同与复现范围

1. 用户提供同次身高、体重、测量时年龄，以及明确的吸烟史和相关既往慢病史；可提供目标体重，性别仅作可选上下文。
2. 技能已核对并冻结正文表 2 的全部九档 HR、组别置信区间和切点，运行时不取外部数据，不要求用户提供论文或队列。
3. 报告计算 BMI 并查对应人群关联，最多比较用户指定体重下的表值；不估计个人绝对死亡风险、寿命或减重获益，不提供药物剂量或启停建议。

流水线已授权按论文实施，无额外合同审批步骤。

## 可行性与材料审阅（2026-11-25）

用户明确此机无浙大缓存目录。DOI 和 Lancet 文章页访问返回 403，PMC 全文可经网页工具阅读，Europe PMC fullTextXML 完整下载成功。全文只列一个补充文件 `mmc1.pdf`（67 页）。PMC 文件端点触发验证，已从 Europe PMC supplementaryFiles 合法开放接口下载 ZIP 并提取、打开该 PDF，审阅目录、eTables 1–23、eFigures 1–11、eAppendices 1–6，重点读取 eTable 8（p20）、eFigure 1（p37）、eAppendix 2（pp51–53）。来源原文件只在临时目录，不复制入仓库。

- 全文：https://pmc.ncbi.nlm.nih.gov/articles/PMC4995441/
- XML：https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4995441/fullTextXML
- 出版社：https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(16)30175-1/fulltext
- 原附录：https://pmc.ncbi.nlm.nih.gov/articles/instance/4995441/bin/mmc1.pdf
- 已读取的附录下载镜像：https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4995441/supplementaryFiles
- 合作组织链接 https://www.phpc.cam.ac.uk/ceu/research/global-bmi-mortality-collaboration 返回 403；正文称其提供队列网页及经费信息，未将其标为代码或数据发行地址。

正文方法提及 SAS 9.3 / Stata 12；附录 p51 说协调中心向参与研究提供 Stata 脚本，但未列公开代码地址、GitHub、Zenodo、OSF 或个体数据下载。不能声称复现原回归；本工具只使用已打印查表，没有需要从未公开代码重建的参数。eFigure 8（p45）是给定假设参照风险下的绝对风险示意，不能作为个人校准。

## 计算与范围

BMI = weight_kg / (height_cm / 100)²；表中单位为 kg/m²。正文 Table 2 的列是九个 BMI 区间；行是 Participants/deaths、HR (95% CI)。`presets.BMI_ROWS` 每行依次为下限、上限、HR、CI 下限、CI 上限。区间统一左闭右开，不在表内则拒绝，不插值。

正文方法写排除 BMI<15 或 ≥60，以及年龄<20 或 >90。附录分析计划 p51 写 BMI<15 或 >60，年龄<20 或 ≥90；正文表 2 和 eTable 8 最后一档均为 40–<60。因此 BMI 依最终表格取 [15,60)，年龄取两段描述的较窄交集 [20,90)。manifest 的 population.age_years 仅能表达闭区间，note_zh 和运行时另执行严格 <90；不把 90 岁静默纳入。

原研究各队列既往病记录不同，eTable 2 列出 Heart disease、Stroke、Cancer、Other vascular disease、Respiratory diseases；eAppendix 2 还明确包括神经退行性病。工具要求上述集合均无已知病史，是保守产品适用筛查，不能声称完全复原每个队列纳排。单独糖尿病的排除是敏感性分析（eTable 19），不擅自加到表 2 的条件里。排除最初 5 年随访属于研究设计，工具不以任何输入声称用户未来必然存活。

身高 100–250 cm、体重 20–500 kg 是检测录入单位错误的工程范围，不是论文阈值。身高可换 m×100、mm×0.1、in×2.54；体重可换 g×0.001、lb×0.45359237。单位因子为精确单位定义，与论文回归常数无关。不声明未经核对的 LOINC。年龄和性别不调整表值。

## 先写复现测试

实现前先写 `tests/test_manifest.py::test_table_2_printed_categories`，用表 2 打印的每个区间下限作为输入，断言相应 HR 和 CI 三元组；完整九档均精确匹配表的两位小数。skill.json 中逐格引文保留原文小数中点。eTable 8（p20）的 All geographic regions 行独立核对转录，与表 2 一致，但不是另一项独立验证研究。没有反推常数或拟合第三方结果。

论文没有个人身高、体重的算例。CLI 测试的身高 200 cm、体重 120 kg 是明确标记的合成输入，使 BMI 落在论文打印的 30.0 下限，期望 HR 1.45（1.41–1.48）来自表 2。目标 110 kg 同样是软件夹具，BMI 27.5 对应打印 HR 1.20（1.18–1.22）；不把这些身高体重说成论文病例。

## 目标情景

支持 --targets；只允许 weight_kg，身高固定。levers.json 写当前表值、目标表值及单项目变化。BMI 对体重导数为 1/height_m²，对身高 cm 导数为 −2×BMI/height_cm；HR 档内导数为零，切点处为 null。敏感度是查表函数的数学属性，不是生理效应。目标表值之差仅为描述性差异，不把两档 CI 合成变化的 CI，也不将其转换成个人死亡概率。
