# 证据核对

研究设计：原创人群风险模型推导及外部验证。主要模型在前瞻性 CONOR 队列建立；外部验证包括观察队列及随机试验数据的二次利用，本文主结论不是一项治疗随机试验的主要结局。PubMed（PMID 34120185）收录为 Journal Article；发表卷期年 2021，European Heart Journal 42(25):2455–2467。

物种：人（human；Homo sapiens），没有动物或细胞实验。

全部直接推导/验证组（Main Table 1）：

| 用途 | 组别 | 入选人数 | 主结局事件 |
|---|---|---:|---:|
| 推导 | CONOR | 28,503 | 10,089 |
| 外部验证 | ARIC | 5,153 | 427 |
| 外部验证 | CPRD | 319,390 | 31,484 |
| 外部验证 | HYVET | 3,381 | 225 |
| 外部验证 | MESA | 2,977 | 501 |
| 外部验证 | PROSPER | 3,254 | 396 |
| 外部验证 | SPRINT | 4,460 | 186 |

外部验证合计 338,615 人、33,219 个事件；七组总计 367,118 人（211,184 女、155,934 男）。均为本次分析筛选后的样本，不能拿 PROSPER 原试验 5,804 人或 MESA 原始 6,814 人代替。本研究没有另设病例对照组。HYVET、PROSPER、SPRINT 合并分析时考虑了试验治疗分配的效应。

地区校准还用 WHO 死亡率及 NCD-RisC 风险因子分布。补充 Methods Box 3 提及乘数来源 CPRD 2,589,074、Swedish Patient Registry 5,252,592、Estonian biobank 67,474、HAPIEE 16,521 人；正文汇总相关 SCORE2 来源为男 4,056,218、女 3,869,443，732,471 个事件。这些是模型校准背景，不是额外的个人预测验证样本；不同来源统计的总体不强行合并。

治疗收益演示子集为 HYVET/SPRINT 高血压者 5,579 人及 PROSPER 血脂较高者 3,051 人；本技能不实现该部分。

利益冲突（发表全文已核对）：R.P. 报告 Australian NHMRC 显著资助；P.V. 报告 Servier、Hygeia Hospital Groups Ltd 和 ESC 的个人报酬；L.P. 获 BHF Programme Grant RG/18/13/33946 支持；其余作者声明无与本文相关潜在利益冲突。资金来源还包括 NIH/NHLBI 等、HYVET 的 British Heart Foundation 与 Servier International、PROSPER 的 Bristol-Myers Squibb 研究者发起资助；文中说明资助方不参与该工作设计、完成或发表。未见本文算法的专利声明。

| 论文声称什么 | 补充材料实际有什么 | 公开代码实际算什么 | 同名/相关项目辨别 |
|---|---|---|---|
| 年龄、吸烟、糖尿病、SBP、TC、HDL 及年龄交互可估计老年人 CVD 风险 | Methods Table 3 给男女系数与十年 S10/meanLP，Methods Tables 1–2 给地区校准与公式 | 没有发布模型仓库链接；本实现只抄已印常数 | 不等于 SCORE2（较年轻人群）或旧 SCORE O.P.（死亡风险） |
| 模型可用于五年和十年风险 | 十年有完整步骤；五年见 Figure S8 分档图，未见五年连续方程所需 S5 | 没有假装从公开代码找到 S5；只实现十年主结局 | 不使用第三方 SCORE2 包参数替代本篇原文 |
| 校准到四个地理风险地区 | Table 1 的全地区校准参数与 Table 3 的算例低地区参数不一致 | 采用全地区参数表，保留两个预期失败的最终示例测试，validation=draft | 不是中国特异风险模型，不能把族群当地区 |
| 可估计含 HF 的次要结局及治疗收益 | Table 4 给 HF 乘数，Methods 给 HR 组合演示 | 本实现均不输出；目标重算也不冒充治疗效应 | 不是 SCORE2-Diabetes、ASCVD/PCE 或治疗决策工具 |

已发现的文本问题：摘要事件句存在缺字，以正文和 Table 1 的总计为准；统计方法中把较年轻人的并行模型写成 SCORE2-OP，结合引用对应的 SCORE2 论文识别为笔误，不复制该错误。补充 ARIC 描述开头称横断面 visit 6，但同段后文及正文明确本研究取 visit 5 基线进行随访风险验证；本技能不把主研究设计错标为横断面。补充 Tables 1–3 与 Figure 2 的数值冲突详见 contract.md。
