# Claims

Simkhada 等, GeroScience 2026, doi:10.1007/s11357-026-02551-x (online 22 September 2026, not yet in an issue). Read from the full text through the Zhejiang University library and from ESM 1 (Supplementary Tables S1–S7, Figure S1, imputation note). Code: https://github.com/bipulsimkhada/mci_progression_ml, commit c67358dbb0960b41c2b1fd775114d000bae13081.

- **研究设计**：回顾性队列（ADNI 公开数据库）的机器学习预测研究。每次就诊算一个样本；以 24 个月内是否由轻度认知障碍转为痴呆（AD）标为 pMCI 或 sMCI。外层五折重复五次的嵌套交叉验证，再加 20% 按受试者分组留出的独立测试集。没有外部队列验证（Discussion 写明 OASIS-3 和 AIBL 做不了）。
- **全部样本组**：动态数据集 2008 个样本、828 名受试者；sMCI 1306 个样本（577 人），pMCI 702 个样本（347 人），96 人两类都有。训练集 1607 个样本、664 人（sMCI 1045，pMCI 562）；独立测试集 401 个样本、164 人（sMCI 261，pMCI 140）。只取基线就诊的对照数据集 690 个样本（sMCI 473，pMCI 217）。补充材料另说有 186 个含缺失值的样本（114 sMCI，72 pMCI）用于选择插补方法。
- **物种**：人（human）。
- **利益冲突**：论文写明作者没有利益冲突（“The authors declare no competing interests.”）。资助来自 NSF、NIA/NIH 和 Ware Foundation。

| 论文声称 | 补充材料实际有什么 | 代码仓库实际算什么 | 同名或相近的另一样东西 |
| --- | --- | --- | --- |
| 主模型：校准后的 XGBoost（SMOTENC），DEM–COG–MRI 334 项特征，独立测试集平衡准确率 81.99%（bootstrap 均值 81.97%，95% CI 78.22%–85.51%），切点 0.37（Results）。 | 表 S7：互信息选 50 项特征（PTEDUCAT、APOE4、MMSE、CDRSB、ADAS11、ADAS13、FAQ 和 43 项磁共振指标），XGBoost 超参数。表 S1：323 项 MRI 特征分五类。 | `models/final_model_all_features.pkl`：需要全部 332 项数值特征和 2 项类别特征进入 KNN 插补，再选 50 项。 | 本技能**不算**主模型：323 项 UCSF FreeSurfer 7 指标个人拿不到。 |
| 消融：只用 COG 模态，测试集平衡准确率比主模型低 4.73%（95% CI 0.94%–8.39%）（Results，Ablation）。 | 无 COG 模型的单独表。 | `models/final_model_cognitive_scores.pkl`：只用 MMSCORE、CDGLOBAL、CDRSB、TOTSCORE（ADAS11）、TOTAL13（ADAS13）、FAQTOTAL 六项；XGBoost 451 棵深度 3 的树 × 5 个校准折，Platt 校准，Youden 切点 0.3204。 | 本技能用的就是它；导出与核对见 contract.md。 |
| COG 模态六项：MMSE、CDR Global、CDR-SB、ADAS11、ADAS13、FAQ（Methods）。 | 表 S2：六项的均值 ± 标准差 [中位数]（动态数据集）。 | `config.py` 的 `cog` 列表同序。 | 摘要把 MMSE 写成 “Mental State Examination”，正文写全名 Mini-Mental State Examination，指同一量表。 |
| 预测窗口严格 24 个月；24 个月后才转化的仍标 sMCI；回到认知正常等波动轨迹排除（Methods）。 | — | `dataset.py` 按 6/12/18/24 个月诊断生成标签。 | 本技能的概率只指 24 个月窗口。 |
| 解释性：FAQ、CDR-SB、ADAS11/13、MMSE、APOE ε4 和海马、侧脑室、顶叶颞叶、杏仁核最重要（SHAP、置换重要性）。 | — | `framework/xai/`。 | 队列层面的排名，不对个人计算。 |
| 研究工具，尚不能用于常规临床（Discussion）。 | — | — | 报告边界句保留这一点。 |

摘要和正文一致的地方：样本数、受试者数、测试集表现。摘要没有提 COG-only 消融；数字以正文 Results 为准。
