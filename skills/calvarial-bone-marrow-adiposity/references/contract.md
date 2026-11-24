# 方法合同与可行性

1. 用户提供本人头部 T1 加权 MRI 经作者 FreeSurfer 流程处理后提取的 50 层强度矩阵；年龄、性别可选，只作背景。
2. 技能内置作者公开发布的完整 SavedModel 和权重，不要求用户寻找模型、队列或补充表。原始影像预处理说明指向作者公开脚本，由 agent 获取；当前计算入口从个人矩阵开始。
3. 仅报告颅骨骨髓信号代理指标、外板信号与质控；不报告脂肪百分比、生物年龄、百分位、疾病风险或药物调整。

流水线已授权完成实现，无额外合同审批步骤。数据类型为影像。方法不是可用生活方式指标设定目标的风险方程，未提供 targets/levers。

## 来源冻结

论文：Kaufmann 等，eLife，2026，doi:10.7554/elife.101499，正式版页面及 PMC13734677 / Europe PMC fullTextXML。核查日期 2026-11-24。

源码：[boneMarrowLocalisationT1wMRI v1.2](https://github.com/comgen/boneMarrowLocalisationT1wMRI/releases/tag/v1.2)，提交 `d33e4009afb47dedba73de94fb34d55b4fdb770c`。模型目录 `000_simulateAndTrainNN/NNmodels/2021-02-11` 的三个二进制文件原样保存于 `data/model`，SHA-256 逐一记录在 skill.json，运行前校验。当前 main `8446a33865e4937b202e6d73d7e630ab30ce86ac` 的模型与该版本逐字节相同。MIT 授权随文件保留。`upstream-run_predBM.py` 与 `upstream-computeAuxiliaryFiles.r` 是 v1.2 的源代码快照，仅作核对。

## 计算约定

| 项目 | 使用值/做法 | 来源 |
|---|---|---|
| 层数、距离 | 50 层；0.5 mm 步长；共 25 mm | Methods: FreeSurfer preprocessing；Appendix 1 workflow |
| 输入尺度 | 0–255；推断前除以 255 | Appendix 1 figure 9；run_predBM.py |
| 网络输入 | 50 个强度 + 100 个零上下文，占位零不是缺测值填补 | run_predBM.py 的 norm_pad_inputs |
| 发布模型结构 | 150→300→100→100→6；前三层 ReLU；末层线性 | 实际 SavedModel graph 和 checkpoint 张量形状 |
| 输出边界 | 输出乘 50、截到 [1,50]、按最近偶数舍入为整数 | run_predBM.py 的 clip 与 savetxt `%1.0f` |
| 颅顶部位点筛选 | 50 层强度之和严格 >1000 | computeAuxiliaryFiles.r，vertexIntSumCutoff |
| 位点骨髓/外板均值 | 按预测首末层取闭区间，先层内均值 | computeAuxiliaryFiles.r 的 R `a:b` |
| 全头骨髓指标 | 对筛选后的全部颅顶部位点均值再求均值 | Results: Locating calvarial BM；README step 5 |
| 最少位点 | 5000，等于时通过 | Methods: ANN quality control measures |
| 外板标准差 | 位点外板均值间样本标准差，最大 30 | 同上；R `sd`（分母 n−1） |
| 马氏量 | 骨髓首层及骨髓均值的二维样本协方差，使用距离平方 | 同上；R `mahalanobis` 返回平方距离 |
| 马氏超限 | 平方距离 >25 的位点占比不得 >0.005 | Methods: ANN quality control measures |

全部所需权重、缩放和阈值均已找到；不重新训练、不拟合或补造常数。`presets.py` 是常数唯一实现源。协方差不可逆时停止，不加入未经来源支持的岭参数。

发布的 R 脚本额外导出“MD 四舍五入至一位小数后 <25”的去异常点统计，本文入口采用论文正文定义的全部位点均值和未舍入 MD >25 的扫描质控，不将那个额外输出冒充论文主指标。恰等于阈值的边界按正文严格不等号处理。R 的闭区间也允许倒序；层均值采用同一端点集合，没有另造修正边界。

## 架构差异和执行兼容

正文/图1示意 50→100→100→100→6，而发布模型实际为 150→300→100→100→6。公开推断脚本明确填充 100 个零，训练笔记本也保留了该结构，因此遵循发布权重，而不根据示意图重建另一模型。笔记本中的学习率/epoch设置也与正文描述不同，均不用于重新训练。无法仅凭材料确认每张论文图究竟使用哪次训练，保留 draft。

SavedModel 元数据为 TensorFlow 2.4.1。TensorFlow 2.16.2 的对象式 `saved_model.load` 遇到旧优化器 add_slot 不兼容；已实测使用 `tf.compat.v1.saved_model.loader.load` 可恢复原图、原权重和 serving signature。未删除节点或修改权重。运行时固定 TensorFlow 2.16.2；测试另用 checkpoint 中的四组 kernel/bias 做独立矩阵乘法核对推断，属于工程核对。

## 验证缺口

已读全文、表1、附录图1–14及表1–9、MDAR、作者 README（PDF/DOCX）、训练笔记本、模拟脚本、推断脚本、发布权重与 v1.2 GWAS 文件。Figure 1d 显示个人散点，Appendix figure 4 显示七个扫描的热图，figure 10 显示一个人的图像及群体相关系数，但均未给出可精确复算的个人 50 层强度数组及对应输出。不能把图上读数或群体相关系数当个人算例。公开 GWAS 列是 SNP 统计，也不是对应 MRI 输入输出。

因此 `validation.status=draft`、`inputs_status=draft`。先写的 tests/test_manifest.py 检查输入失败、正文质控阈值和独立权重计算；人工合成输入只用于工程测试，不是论文验证数据。未运行原始 MRI 的完整 FreeSurfer/FSL/Matlab 流程，也未在 HNU、HCP、UKB、MICA-MICs 原始扫描上重现群体结果；不会声称完成这些验证。
