# 证据核对

研究设计：原创人体方法研究，对RENO Diet-Heart Study基线进行横断面回归；虽然母研究计划随访5年，本方程不是随访风险预测或随机试验。PubMed列Research Support, U.S. Gov't, P.H.S.，没有Review类型。

全部样本组：基线508人，完成REE测量的498人进入本研究；女性247（正常体重135、肥胖112），男性251（正常体重129、肥胖122），合计正常体重264、肥胖234。肥胖按原文理想体重百分比界定，不等同现代BMI切点。含FFM的完整分析为482人（Table 2女性244、男性238）；Table 3的LBM比较则为女性245、男性238，Figure 1亦标女性245。原文这些计数不一致，均照其位置记录，不能改称同一个完整数据样本。没有独立外部验证组。

物种：人（human，Homo sapiens）。参考文献中的大鼠研究不是本文实验，不计入本文species。

利益冲突：已读全文，未见单列Competing interests/Disclosures声明，不能声称“无利益冲突”。p.241列资助Student in Health Sciences grant AM07478及National Heart, Lung and Blood Institute/NIH grant HL 34589；未见作者专利或企业雇佣披露。

| 论文声称什么 | 正文/补充表实际有什么 | 代码仓库实际算什么 | 同名或相关方法有什么区别 |
|---|---|---|---|
| 常规测量能预测健康成人REE | p.244 Eq 3完整四输入系数；p.246 Eqs 7、8简化式 | 未点名公开代码仓库，只有SPSS-X软件；本实现直接采用印刷系数 | 不是Harris–Benedict、Owen或Cunningham方程 |
| 简化不影响总体预测关系 | p.246说明相关r=1.0；并非每人的两个数完全相等 | 同时输出两式，不混同 | 简化舍入引起固定可计算差异，不是测量不确定性区间 |
| MSJE群体预测接近实测均值 | Table 3明确区分Measured和MSJE；本技能复现MSJE列均值 | 不计算群体标准差、相关系数或个体误差 | Table 1实测REE不能直接当个人预测示例 |
| FFM单项最强相关 | Eq 1给全组FFM式；Table 2列REE、Weight、Height、Age、Percent IBW、BMI、WHR、Sex的相关 | 本产品不输入FFM，不实现缺项回退 | Figure 1女性FFM式图注截距360而正文369；Figure 2女性体重式图注斜率10.0而正文10.9，本技能不用这些冲突式 |
| 观察对象覆盖一定年龄、体重范围 | Table 1列Weight、Height、Age、Percent ideal body weight、Body mass index、Waist-to-hips ratio、Percent body fat、REE；Table 3列Measured、MSJE、Owen、HBE、Cunningham | 输入范围另区分工程合理范围与样本观测范围 | 男性年龄Table 1为19–76，Subjects正文为19–78；总体为19–78，采用正文男性范围 |
| 方程仍需其他人群评估 | p.247明确需要其他人群验证与直接代谢测量 | 不声称对中国人、患病或妊娠哺乳者已验证 | REE不等于总能量消耗，不输出活动系数或摄入处方 |

Tables 1–3及Figures 1–2已读；原文未点名补充文件或公开数据代码。出版社附件列表未能独立完整读取，不能宣称无附件；访问记录见contract.md。
