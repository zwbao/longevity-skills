# 证据与实现边界

研究设计：Europe PMC / PubMed（PMID 28698222）出版类型为 Meta-Analysis、Systematic Review、Journal Article；本技能 evidence=review。主要证据是人体随机试验的系统综述及荟萃分析，另有作者原创的组水平分段回归；不是一项新的个体随机试验或临床预测模型。

样本组：49 项随机试验，17 个国家，共 1863 人，平均年龄 35±20 岁。试验均比较相同 RET 下的蛋白补充与安慰剂或不补充；同时存在两个对照时取安慰剂组。10 项研究纳入已有抗阻训练经验者，14 个研究组仅女性；13 项研究含作者定义的老年（>45 岁）人群。Supplementary Table 2 列出各组 N，多蛋白来源试验共享对照，部分 N 标为问号，不把重复对照相加。没有新的独立验证组。Figure 5 的拐点分析是其中 42 个 DXA 研究组、723 人（年轻和老年，包含干预和对照组），不可误写为 1863 人的个体模型。Supplementary Figure 4 的 1RM 汇总是 28 项研究、1078 人，FFM 汇总为 28 项研究、1107 人；各分析样本不同。

物种：人（Humans）；没有本论文自己的动物或细胞实验。

利益冲突：正文披露 SMP（Stuart M Phillips）获得 US National Dairy Council 的研究资助、差旅及讲课酬金，该机构也资助本综述纳入的试验。2020 年更正（10.1136/bjsports-2017-097608corr1，PMC7513243）补充 Brad Schoenfeld 在撰写论文时任 Dymatize Nutrition 顾问委员会成员，并在更正时仍任职。此更正不改数值结果。

| 论文声称什么 | 补充材料实际有什么 | 本技能代码实际算什么 | 同名或相关方法区别 |
|---|---|---|---|
| 总蛋白摄入与 RET 后 FFM 关系可用分段回归描述；拐点 1.62，95% CI 1.03–2.20 g/kg/day，p=0.079 | Supplementary Table 2 是蛋白组成、安排和各组人数；不是个体摄入、体重和预测值数据 | 总蛋白 g/d 除以体重 kg，再比较印出拐点 | 不是个人需要量方程，也不是补剂量计算器 |
| Methods 把分段回归的第二段斜率设为零 | Supplementary Figure 3 展示基线摄入的另一组回归，非 Figure 5 总摄入模型 | 不拟合回归，不预测 FFM | 不能用基线摄入斜率替代总摄入拐点 |
| 额外的平均 FFM 和 1RM 增益 | Supplementary Figure 4 的组平均增益及百分比；Supplementary Figure 2 为肌纤维与股中部 CSA 森林图 | 不把这些组均值算作个人输出 | 不是个人增肌或力量效果估计 |
| 年龄与训练状态影响部分组水平效应 | Table 1 为系数、CI、异质性、p 值；Supplementary Table 3 为其他单变量元回归 | 年龄仅用于成人输入检查，性别不参与公式 | 不建立年龄或性别专属摄入切点 |
| 全部数据在正文及补充文件中 | 两份 Appendix、三份 Table、四份 Figure；没有独立 GitHub、Zenodo、OSF 代码或数据链接 | 运行时完全离线，仅使用冻结常数 | RevMan、Stata、GraphPad Prism 是原研究软件，不是已发布的作者代码仓库 |

正文与摘要差别：摘要年龄效应的 p=0.002，但 Table 1、Results、Figure 4 与 Summary box 为 p=0.02；按正文记述，不用于个人计算。正文 Table 1 基线摄入系数 CI 上限 1.27，Supplementary Figure 3 图注为 1.26；均不进入本技能。不能用这些差异制造个人修正参数。

论文年按卷期使用 2018，尽管在线发表于 2017。无减重能量限制试验；女性和老年证据较少。FFM 不等同纯骨骼肌，也不代表健康寿命。
