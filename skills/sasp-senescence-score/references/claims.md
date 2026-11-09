# 论文与代码对照

Zhao 等，Aging Cell 2026（25 卷 10 期，e70737）。doi:10.1111/acel.70737。PMC13615172。

- **研究设计**：队列研究（UK Biobank 前瞻队列，UKB-PPP 蛋白组；基线评分与随访死亡和慢病的 Cox 模型），外加一个随机试验（MEDEX，NCT02665481）的二次分析做外部验证和 18 个月轨迹。PubMed 出版类型：Journal Article / research-article。
- **全部样本组**：UKB-PPP 纳入分析 50,997 人，随机分为训练集 43,358 人（85%）和测试集 7,639 人（15%）；关联和预测分析都在测试集。外部验证 MEDEX 585 人（65–84 岁），运动组 282 人、非运动组 303 人（Table S4 标题）。注：Table S3 标题写训练 30,184 与测试 12,935，和正文 43,358 / 7,639 不一致，这里按正文。
- **物种**：人（Homo sapiens）。
- **利益冲突**：正文 XML 未含 Conflict of Interest 段落，未核对。资助：NIH P30AG067988、R01AG072694。

| 论文声称 | 补充材料实际有 | 代码仓库实际算 | 同名的其他项目 |
|---|---|---|---|
| 38 个 SASP 蛋白（Methods 2.3，印作 SERPIN1） | Data S1 只有方法描述 | `protein_list` 38 项，SERPINE1 | 其他“SASP 指数”多用 PCA 或单个蛋白相加，不是本模型 |
| GAET：Transformer 编码器 + 解码器 + 年龄引导的线性头（Figure 1、Data S1） | Data S1：损失 λL_recon + (1−λ)L_pred；不加位置编码；均值池化后投到 L 维瓶颈 | `tgae.py`：d_model 128、8 头、2 层、瓶颈 6 维；`predict` 只走编码器和 regressor | — |
| 评分高者死亡、慢病风险高（aHR 1.41，95% CI 1.25–1.60 每 1 SD，测试集） | Figure S1–S23 未完整取得 | 仓库不含 Cox 分析 | — |
| 高分组切点 > 65（训练样本中基线无主要慢病者的第 90 百分位） | — | 仓库未写切点 | — |
| 可跨平台使用 | MEDEX 用 Luminex，先 Cycloess 标准化、mice 插补，再用 MEDEX 数据微调 | `match_ukb_dist` 用整组样本的均值和 SD 把数据拉到 UKB 分布；`fine_tune.py` 用年龄微调 | — |
| 个人示例 | 无 | `example.ipynb` 无保存输出 | — |

摘要与正文一致的地方：38 个蛋白、UKB-PPP 开发、MEDEX 18 个月。摘要说运动“significantly changed the SASP Score trajectory”，正文结果是交互作用不显著、只在组内比较里非运动组上升；报告按正文写。

打开过的材料：Europe PMC 全文 XML（PMC13615172）；Data S1 补充方法（docx，从 Europe PMC 补充材料压缩包取出）；GitHub shangshuzhao/sasp 全部文件（README、tgae.py、proteins_info.py、get_index.py、utils.py、fine_tune.py、example.ipynb、tgae_pre_trained.pth）。没打开：Figure S1–S23 文件（压缩包下载不完整）、Table S1–S4 文件（PMC 与 Wiley 下载被人机验证拦住）；它们按标题是字段号、基线特征和图，不含模型权重。
