# 论文证据与实现范围

研究设计：Cederroth，medRxiv 2026，第三版（2026-11-12），原创人体横断面分析。研究对象虽来自 STOP 队列，本研究是同次测量的横断面关联，不是随访预测或干预试验。来源是 medRxiv 第三版全文与官方版本 API，并非已发表期刊论文。

样本：LifeGene 邀请 26,282 人参加 STOP，5,593 人完成问卷；927 人接受临床评估，排除 664 人后剩 263 名无耳鸣成年人（526 耳），自报女性 178 人、男性 85 人，20–84 岁。听力与 OAE 可用 526 耳，言语测试 257 人、511 耳。ABR 记录 168 人、336 耳（Chartr 190 耳，Eclipse 146 耳）；质控后 I/III/V 潜伏期分别 324/322/321 耳。Eclipse 波 I 振幅可用 72 人、140 耳，有言语数据者 134 耳。联合设备潜伏期完整案例模型为 163 人、298 耳（Chartr 176 耳、Eclipse 122 耳），其中 135 人贡献双耳；振幅模型限 Eclipse 68 人、122 耳。S12 来自 298 耳的潜伏期模型。没有外部验证组或另外的干预/对照组，不能把两耳当成两个独立人。

物种：人（human）。正文讨论的小鼠、沙鼠等属于引用他人的实验，不是本文新增实验。

利益冲突：作者任 Tinnitus UK 专业顾问委员会成员及 American Tinnitus Association、Swiss Tinnitus Liga、Tinnitus Quest 科学顾问委员，是 JARO 主编；该项目获 Decibel Therapeutics 资助，Otometrics 与 Interacoustics 提供设备。原文称作者回避期刊编辑处理。本文分析称未获直接资助，数据采集由 Swedish Research Council、Decibel Therapeutics、Tysta Skolan 支持；VR 2023-02326 支持作者部分薪资，Decibel 参与 ABR 自动质控。原文称资助方未影响收集、分析、解释或发表决定。利益声明虽提及期刊编辑审稿流程，本技能使用的仍是 medRxiv 预印本，保持未经同行评审状态。

| 论文声称什么 | 补充材料实际内容 | 公开代码实际算什么 | 同名或相近项目的区别 |
| --- | --- | --- | --- |
| 扩展高频 PTA 与言语表现的关联强于常规 PTA | S7 是单变量多项式拟合统计；不是可直接计算所有个人得分的完整模型 | Data/Code 页未列代码；数据尚待伦理批准 | eHF PTA 不是 PTA4，不能互换；技能不把 S7 的 R² 当个人概率 |
| 年龄与波 I 潜伏期存在交互 | S9 为联合设备模型的完整系数与 HC3 推断；S12 为固定其余协变量后的数值预测 | 未公开可下载模型或中心化配置 | 早期 v1/v2 使用旧题名且混用振幅设备；本技能只用修订 v3 |
| 波 I 振幅不独立预测言语得分 | S10 为 Eclipse-only 模型，S11 为聚类/设备敏感性分析 | 不实现振幅模型 | 振幅 µV 与潜伏期 ms 是不同输入 |
| 75 岁时潜伏期延长对应较大的词语下降 | S12 印出固定年龄、潜伏期坐标的 WS/PS 均值与均值置信区间 | 本技能仅转录并查 S12，不重建 S9 | 不是真实随访变化、干预效果、个人置信区间或耳蜗突触病诊断 |

## 已读取文件和列

唯一的补充文件为 `344934_file02.pdf`（20 页），来源链接见 contract.md。图 S1：按年龄分层的 PTA4/eHF 分布；图 S2：OAE 与 WS/PS 拟合图。无其他补充文件或代码链接。

| 表 | 页 | 列与用途 |
| --- | --- | --- |
| S1 | 4–5 | Characteristics、No (%)；社会人口及疾病情况 |
| S2 | 6 | Variable、<35、35–44、45–54、55–64、65–74、75+；分年龄描述统计 |
| S3 | 7 | Variable、Man、Woman；分性别描述统计 |
| S4 | 8 | Variable、Low/Medium/High eHF loss；按 eHF 三分位描述统计 |
| S5 | 9 | Variable、n、各阶 R²/p、Best_fit_model、Best_R²、Decision_rule；年龄轨迹拟合 |
| S6 | 10 | model、outcome、term、estimate、std.error、statistic、p.value、conf.low/high；年龄/性别探索模型 |
| S7 | 11 | Outcome、Predictor、n、各阶 R²/p、Best_model、Best_R²、Decision_rule；单变量模型 |
| S8 | 12 | Model Phase、Outcome、Observations、Parameters_including_intercept、R²、Adjusted_R²、Delta_R²、Nested_model_p、AIC |
| S9 | 13–14 | Variable、WS/PS estimate、robust_se、t、CI_Lower/Upper、robust_p；均值中心化但缺完整中心化常数 |
| S10 | 15–16 | 与 S9 同类列，增加 W1Amp_c、Age_x_W1Amp；Eclipse-only，仍缺完整中心化常数 |
| S11 | 17–18 | model、Term、β、HC3/CR3 SE、95% CI、p、CR3 df；设备与双耳相关敏感性分析 |
| S12 | 19 | Age Group、W1.Latency Level、W1.Lat (ms)、WS/PS Predicted、SE、95% CI [L]/[U]；本技能全部数值来源 |
| S13 | 20 | Age_Group、Overall_Median_Age_Cutoff、n、Median_Age、WS/PS Mean/SD、Correlation、Slope、HC3 推断；非个人预测表 |

S9/S10 跨页延续 PS 行处重复出现 WS 表头；按上下文读取为 PS 延续，不混入 WS。S12 两个明确的 WS/PS 表块没有这种问题，依年龄与潜伏期坐标逐行合并。

摘要将测听频段概括为 0.5–16 kHz；Methods 写实际测量 0.125–16 kHz，PTA4 为 0.5/1/2/4 kHz、eHF PTA 为 10/12.5/14/16 kHz。技能的 ABR 输入不受该频段概述差异影响。主文预测段与 S12 的端点舍入一致；不把摘要的“约 1.8 ms”当成原表精确的 1.83 ms。
