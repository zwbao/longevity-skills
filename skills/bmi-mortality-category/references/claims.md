# 研究与来源核对

研究设计：人类前瞻性队列的个体参与者数据荟萃分析，非随机干预试验；Europe PMC PMID 27423262 的 pubType 包含 Meta-Analysis、Multicenter Study、Journal Article。manifest 以 cohort 表示支撑主要结论的观察性随访设计。

全部样本组：239 项研究提供 10,625,411 人资料，跨 32 国。eFigure 1 中全体可分析人群为 237 项、10,622,450 人、1,601,774 例死亡；排除基线疾病后为 236 项、9,104,247 人、1,210,250 例死亡；再排除随访最初 5 年为 213 项、7,805,434 人、949,010 例死亡；进一步限从不吸烟者即主分析 189 项、3,951,455 人、385,879 例死亡。另有两项合格研究未提供个体数据（307,667 人、39,611 例死亡），不计入分析；不能当作验证组。没有个人预测模型的独立训练/验证分组。

主分析地区（eTable 8）：欧洲 89 项、1,135,600 人、56,477 例死亡；北美 40 项、1,415,087 人、219,922 例；东亚 46 项、1,074,385 人、100,784 例；澳大利亚/新西兰 11 项、149,602 人、4,656 例；南亚 3 项、176,781 人、4,040 例。合计与主分析相符。表 1 六档和表 2 九档采用不同参照档，不互换数值。

物种：人（human）；正文和附录的研究对象均为人，没有动物或细胞实验。年份采用 Lancet 388(10046):776–786 的 2016 卷期年。

利益冲突：已核对正文 Declaration of interests。EDA 获 MRC、BHF、NIHR、NHS Blood and Transplant、欧委会科研经费及 Elsevier France 个人费用；DW 自 2014 年起全职受雇 Roche、获个人费用并持股；PG 获中国青年人才计划及 BHF 经费；BJC、JG、GKR、VB 获 Cancer Research UK/MRC 经费，BJC 另获 BHF Oxford 经费；MW 获 Novartis/Amgen 个人费用；OHF 获 Nestle/Metagenics 科研经费；RJK 获 NHMRC 经费；NS 获 AstraZeneca、Boehringer Ingelheim、Janssen 个人费用；EB 获澳 NHMRC 和 National Heart Foundation 经费；SGT 获 MRC/BHF 经费；JD 报告 BHF、NIHR Cambridge、BUPA、diaDexus、ERC、EU、Evelyn Trust、Fogarty、GSK、Merck、NHLBI、NIHR、NINDS、NHS Blood and Transplant、Novartis、Pfizer、MRC、Wellcome Trust 经费。其余写作委员会成员声明无竞争利益。本文无待推荐的干预药物或专利工具。

| 论文声称什么 | 正文/补充材料实际有什么 | 公开代码实际算什么 | 同名或相近项目区别 |
|---|---|---|---|
| BMI 与全因死亡呈非线性关联 | 表 2 九个区间和 HR/95% CI；eTable 8 All geographic regions 行一致 | 未找到公开代码发行；本技能只查印出的表 | 不等于 Flegal 的六档分析，也不等于绝对风险计算器 |
| 年龄、性别、地区存在异质性 | 表 3、图 1–3、eTables 8–13、eFigures 2–4 给分层结果 | 不拟合或叠乘亚组 HR；个人结果始终用表 2 | 不从中文输入默认选择东亚；不声称个体校准 |
| 排除吸烟及既往病、延迟随访起点减少偏倚 | 表 1，eTables 4–7，eFigure 1，eAppendix 2 | 个人历史只控制适用性，不能完成原队列统计排除 | 戒烟者不是 never-smoker |
| 有绝对风险示意图 | eFigure 8 假设参照档死亡风险后画出的说明图 | 未将假设风险当作基线生存函数 | 不能给用户预测某年死亡率或寿命 |

## 已打开材料索引及列结构

唯一补充 PDF `mmc1.pdf`（67 页）包含：

- eTable 1（pp3–10）：Study、Ref、Country、Population source、Weight & height assessment、Total participants、Mean(SD) BMI/age、性别/吸烟、随访及死因计数；eTable 2（pp11–14）逐研究病史记录；eTable 3（p15）ICD-8/9/10 死因编码。
- eTables 4–7（pp16–19）：六档 BMI 下研究数、参与者数、死亡数、HR/CI；分别变更纳排、吸烟状态及标准 CI。
- eTable 8（p20）：九档 BMI 列，各地区的 No. participants/deaths、HR(95% CI)、I²(95% CI)，为表 2 核对来源。eTables 9–11（pp21–24）：六档按地区、性别、基线年龄分层。
- eTable 12（p25）：人群归因比例；eTables 13–14（pp26–27）：每 BMI 增加单位量的全因/死因别 HR；eTables 15–16（pp28–29）：九档/六档的死因别 HR。
- eTables 17–23（pp30–36）：固定效应、限制随访、种族调整/排除糖尿病、病史完整性、入组年、BMI 获取方式及职业人群等敏感性分析；保留各 BMI 档 HR/CI，不作为本工具个人计算的额外系数。
- eFigures 1–11（pp37–48）：流程、年龄/性别/地区/死因分层、纳排比较、随访年龄、假设绝对风险及研究层回归图；不从图形拟合缺失模型。
- eAppendices 1–6（pp49–67）：调查者、分析计划、PRISMA-IPD、检索、参考文献及正文图。分析计划点名 Stata 脚本但未发布代码链接。未发现其他补充文件或公开代码/个体数据发行。

访问链接和遇到的访问限制详见 [contract.md](contract.md)。摘要和正文表 2 的数值一致；正文与附录在年龄 90、BMI 60 的端点措辞不同，处理已明示于合同。
