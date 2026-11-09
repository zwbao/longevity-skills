# Contract

1. **用户提供**：同一次就诊的六项量表成绩——MMSE、CDR 全局分、CDR-SB、ADAS-Cog 11、ADAS-Cog 13、FAQ；可选现用药和体检（只照录，不进模型）。
2. **技能自带**：`data/cog_model.json`，从作者仓库 `models/final_model_cognitive_scores.pkl`（commit c67358dbb0960b41c2b1fd775114d000bae13081，SHA-256 45bb95fd…daa27）导出。不向用户要 ADNI 数据、磁共振或论文文件。
3. **报告能说**：24 个月内转化的校准概率（五个校准折的平均）、它在模型自身切点 0.3204 的哪一侧、五折的范围、哪几项分数离训练人群均值超过 2 个标准差（表 S2）。**不能说**：主模型（DEM–COG–MRI）的概率——缺 323 项 FreeSurfer 指标、APOE ε4 和受教育年限；个人的 SHAP 解释；对认知正常或已诊断痴呆的人的任何数字；用药建议。

## 导出（怎样从 pkl 得到 cog_model.json）

- 只在隔离目录里处理下载文件。先用 `pickletools` 列出 pkl 引用的全部类（sklearn、xgboost、numpy、imblearn 和仓库自己的 `KNNImputerWithScaling`、`CorrelationFilter`、`CustomSMOTE`），读过这三个自定义类的源码，再用只放行这些模块的 Unpickler 载入。
- 结构：`CalibratedClassifierCV(method="sigmoid")`，5 个 `_CalibratedClassifier`。每个的管线是 ColumnTransformer（数值列：KNN 插补 → 方差过滤 → 相关过滤 0.98）→ SMOTENC → XGBClassifier。五折的方差和相关过滤都保留全部六列，没有特征选择步。
- 六项都有时，KNN 插补只做 `scaler.inverse_transform(scaler.transform(x))`，数值不变（浮点差在 float32 取整后消失）；SMOTENC 只在拟合时起作用。所以预测 = 五折平均的 `1 / (1 + exp(a·p + b))`，`p` 是该折 XGBoost 的 `binary:logistic` 概率（base_score 0.5，五折都是 451 棵树）。
- 导出内容：每棵树的 split_indices、split_conditions（叶节点存叶值）、左右子节点、default_left；每折的 a、b、base_score；`final_model.threshold`（0.32039103389120177）。**不导出** KNN 插补器里存的 ADNI 训练行（`_fit_X`）——它们是 ADNI 个人数据。
- 计算：`scripts/cog_model.py` 只用标准库；输入和分裂值都按 float32 比较，`x < split` 走左。

## 核对

- **与原 pkl 逐例**：在 scikit-learn 1.8.0（pkl 保存时的版本）、xgboost 3.2.0、imbalanced-learn 0.14.2 下，原 pkl 的 `predict_proba` 与本脚本在 1,568 个合成输入（ADAS13−ADAS11 在 0–15 内）上最大差 1.3e-7，切点两侧分类全部一致；在测试集 401 行上最大差 1.0e-7。8 个合成输入的 pkl 输出写进 `tests/test_manifest.py::test_export_matches_published_pickle`（容差 1e-6）。这是导出的核对，不是论文的复现。
- **与论文印出的数（离线，不在仓库测试里）**：用作者仓库的 `dataset/final_dataset.csv` 和 `create_train_test_split`（`StratifiedGroupKFold(5, shuffle=True, random_state=11)` 的第一折，scikit-learn 1.8.0），得到训练 1607（1045/562，664 人）、测试 401（261/140，164 人），与论文 Methods 印出的人数完全一致（scikit-learn 1.5.2 会分成 1608/400，不一致）。在这 401 例上，本导出模型按切点 0.3204 的平衡准确率 77.24%（灵敏度 77.86%，特异度 76.63%）；用仓库的 `bootstrap_metrics`（2000 次，random_state=42）得 bootstrap 均值 77.24%（95% CI 73.04%–81.37%）。论文印出主模型 bootstrap 均值 81.97%、只用 COG 时低 4.73%：81.97 − 77.24 = 4.73，一致。
- 这项核对要用 ADNI 个人数据。ADNI 数据使用协议不允许再分发，所以没有放进本仓库，也没有写成仓库测试；`validation` 因此是 `draft`，`gap_zh` 写明了这一点。论文没有印出任何个人输入对应的概率。

## 许可

作者仓库没有 LICENSE 文件。`data/cog_model.json` 只含模型参数，在 `skill.json` 的 `data_files` 里标为 `redistributable: unknown`，合并前由维护者决定。
