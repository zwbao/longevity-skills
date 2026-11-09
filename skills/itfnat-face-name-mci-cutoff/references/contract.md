# ItFNAT 延迟自由回忆与 MoCA 切点：合同、数值来源与核对

## 产品合同

1. 用户提供自己神经心理报告上的 ItFNAT 延迟自由回忆（DFR）校正分和/或 MoCA 校正总分（按意大利常模校正）。
2. 技能自带论文表 4 的切点、灵敏度和特异度，不向用户要论文、常模表或补充材料。
3. 报告给出每个分数落在切点哪一侧，以及该侧的似然比。不能算的：原始分到校正分的换算（公式在常模论文 Manippa 等 2025、Dapor 等 2025，不在本文）；个人患病概率（表 3 logistic 回归没印截距，预测值又依赖样本病例比例）；两项合并的结论（论文没有评估合用）。

## 来源

| 代号 | 出处 | 用到什么 |
| --- | --- | --- |
| [P] | Scaramuzzi GF, Ventrella T, Iacobellis S 等. Delayed associative memory and recall error patterns in mild cognitive impairment: discriminant capacity of the Italian face-name association test. GeroScience. 2026. doi:10.1007/s11357-026-02599-9 | Data analysis 的 ROC 方法；表 4 的切点、灵敏度、特异度、准确率、AUC；Results 末段的 PLR、NLR；表 1 和 Participants 的人群 |

全文经浙江大学图书馆订阅（WebVPN）在 Springer 页面读取；表 1–4 在单独的表格页，同样经 WebVPN 打开并逐格核对。期刊页面没有列出补充材料；Data availability 写明数据不公开、可向通讯作者申请；没有代码仓库。

## 计算（照原文）

- 切点（表 4，Youden 指数最优）：DFR 校正分 ≤ 3.21、MoCA 校正总分 ≤ 23.99 为阳性（偏向轻度认知障碍）。等于切点算阳性，照“≤”。
- 似然比：阳性 = 灵敏度 /（1 − 特异度），阴性 =（1 − 灵敏度）/ 特异度，灵敏度和特异度取表 4。

| 测验 | 灵敏度 % | 特异度 % | 阳性似然比 | 阴性似然比 |
| --- | --- | --- | --- | --- |
| ItFNAT DFR | 60.00 | 80.56 | 3.086（正文印 3.086） | 0.497 |
| MoCA | 65.00 | 72.22 | 2.340 | 0.485（正文印 0.485） |

## 核对（印出的数）

1. DFR：60.00/(100 − 80.56) = 3.0864，正文 “its positive likelihood ratio (PLR = 3.086)”。测试 `test_paper_dfr_positive_likelihood_ratio`。
2. MoCA：(100 − 65.00)/72.22 = 0.4846，正文 “The MoCA low negative likelihood ratio (NLR = 0.485)”。测试 `test_paper_moca_negative_likelihood_ratio`。
3. 表 4 准确率：认知健康 72 人（表 1），特异度 80.56% = 58/72、72.22% = 52/72；灵敏度 60.00%、65.00% 对应 60 名有 ROC 分数的轻度认知障碍者中 36、39 人；(36 + 58)/132 = 71.21%、(39 + 52)/132 = 68.94%，与表 4 一致。正文 MoCA 的 NPV 71.23% = 52/(52 + 21) 也一致。测试 `test_table4_accuracy_is_consistent`。轻度认知障碍组进 ROC 的人数（60，少于入组的 64）是由这些百分比推出的，论文没有直接写。

## 正文与表 4 的出入

- 正文写 MoCA “sensitivity of 78.1%, specificity of 65.0%, and overall accuracy of 72.2%”、DFR “overall accuracy of 65.4%”，与表 4（MoCA 65.00/72.22/68.94，DFR 准确率 71.21）不一致。表 4 的数能复现正文自己印的 NLR 0.485、NPV 71.23% 和准确率，所以技能照表 4。
- 正文一处说 PLR 3.086 意味着“twice as likely”，讨论又说“three times as likely”；数值 3.086 对应约 3 倍，报告用数值本身。
- 正文结果段说 “numerically higher AUC observed for the MoCA”，表 4 是 DFR 0.711 > MoCA 0.705；讨论段写 DFR 更高。照表 4。
- 图注把 DFR 写成 “Delayed Face Recognition”，FRi 写成 “Face Recognition Index”，与方法（Delayed Free Recall、Free Recall index）不一致；照方法。

## 没有做的

- 不从原始分换算校正分：校正方程在 ItFNAT 常模论文（Manippa 等, Clin Neuropsychol 2025, doi:10.1080/13854046.2025.2592647）和意大利 MoCA 8.1 常模（Dapor 等, Neurol Sci 2025, doi:10.1007/s10072-025-08066-1），本文没有印。
- 不算患病概率或预测值：表 3 只印斜率（Age 0.021、Education −0.069、DFR −0.206），没有截距；阳性、阴性预测值随人群病例比例变化。
- 不合并 DFR 和 MoCA：论文分别报告两条 ROC，只做了 DeLong 比较，没有评估合用，两个似然比也不独立。
- IR、DTR、FRi、OMi、IFi、ISi 只有组均值和 ANCOVA（表 2），没有切点，不做个人读出。
