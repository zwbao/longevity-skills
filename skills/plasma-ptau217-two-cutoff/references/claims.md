# 论文声称什么 / 补充材料有什么 / 代码 / 同名项目

- **研究设计**：横断面诊断准确性研究，样本来自两个队列（巴西 Cog-Aging-Study 是纵向队列，本文用的是一次采血；阿根廷 GeNED.ar 是进行中的研究）。PubMed 出版类型：Journal Article（原创研究）。
- **全部样本组**：
  - 巴西 Cog-Aging-Study：共 353 人；114 人有脑脊液、304 人有血浆；只有脑脊液 49、只有血浆 239、两者配对（12 个月内）45、不配对 20。血浆混合模型：CU 92、MCI 139、DAT 73（n=304；比值模型 n=298）。脑脊液混合模型：CU 28、MCI 36、DAT 47。切点验证子集：45 人（A− 17、A+ 28）。
  - 阿根廷 GeNED.ar：134 人，都有血浆，无脑脊液；CU 81、MCI 35、DAT 18（比值模型 n=131）。
  - 合并：CU 173、MCI 174、DAT 91。补充表 4 脚注写 “pTau217-models, n=134; pTau217/Aβ42-models, n=131”，和合并人数对不上，像是从补充表 3 抄过来的。
  - 遗传分析：质控后巴西 148、阿根廷 126（正文）；补充图 17 写巴西 n=173。两处不一致，照正文。
- **物种**：人（Homo sapiens）。
- **利益冲突**：论文 Competing interests：“The authors declare no competing interests.”

| 论文声称 | 补充材料实际有什么 | 代码仓库 | 同名的另一个项目 |
| --- | --- | --- | --- |
| 血浆 pTau217 和 pTau217/Aβ42 能识别脑脊液定义的淀粉样蛋白病理，并和临床诊断一致（摘要、结果） | 表 2：45 人配对子集的阳性/阴性预测值、敏感度、特异度 | 无（“No custom code was developed”，分析用 R mclust、bootLR、pROC） | Ashton 等 2024（JAMA Neurol，ALZpath pTau217）切点 0.40/0.63，本文表 2 引用并比较 |
| 双切点（灰区）提高分类表现（摘要） | 表 2：pTau217 ≥0.85 时 PPV 0.85→0.88、NPV 0.72→0.81；比值 NPV 没有提高 | 无 | — |
| 切点由两成分等方差高斯混合模型得出（结果、方法） | 补充表 1–4：各模型的对数似然、BIC、均值、方差、比例；本技能用 “2 Equal” 行重算出全部印出切点 | 无 | — |
| APOE-ε4、低体重指数、低 eGFR 与较高 pTau217 相关（巴西）；阿根廷还有教育 | 图 4 森林图（β 和 95% CI 只在图里） | 无 | — |
| 非洲血统改变 APOE-ε4 对脑脊液而不是血浆标志物的影响 | 补充图 18、补充表 6 | 无 | — |

摘要和正文：摘要“Classification performance was improved using two-cut-off approaches”，正文表 2 显示对 pTau217 成立，对比值只有 PPV 提高、NPV 下降（讨论部分也这样写）。报告照正文。

补充材料：Supplementary Information PDF（MOESM1，含补充表 1–6、补充图 1–18）、Reporting Summary（MOESM2）、Transparent Peer Review file（MOESM3）都已打开；报告摘要和审稿记录里没有另外的切点或参数。数据需向两个队列的伦理委员会申请，没有公开。
