# 产品合同

1. **用户提供**：十类食物平时每天吃几份（茶、全谷物、水果、炸薯条和炸土豆、烈酒、啤酒、加工肉、含糖饮料、人工甜味剂饮料、人造黄油；不吃填 0），可选每日总能量（千卡）和性别；可选一份目标份数表。
2. **技能自带**：Source Data（41467_2026_77790_MOESM13_ESM.xlsx）工作表 “Figure 2” 的 “Figure 2b” 块里十个全精度权重，正文印出的 Q1/Q5 中位摄入量，Methods 印出的 HRS 能量剔除范围，都写在 `scripts/presets.py`。不向用户要任何论文文件。
3. **报告能说**：这个人的 EDISEA（十项“权重 × 每 2000 千卡份数”的和）、每项贡献、与论文 Q1/Q5 中位数的并列，以及 `levers.json` 里每多一份的变化和达到目标份数后的分数变化。**不能说**：人群百分位或五分位（缺推导训练集各食物组均值 `mu_fg`，论文、补充材料和仓库都没有公布）、预测的 GrimAge2 加速年数、死亡或疾病风险（论文只报告分位间或第 90 与第 10 百分位间的人群比较，没有个人预测方程）。

## 计算

EDISEA = Σ w_i × x_i，其中 w_i 是 Figure 2b 的 Weight，x_i 是第 i 类食物的每 2000 千卡份数。

- 这与作者代码 `construct/hrs-ediea.R` 第 1259 行 `ediea_servday = as.matrix(foods[, sel_fg]) %*% beta_sel_servday` 相同；`beta_sel_servday = -beta_z / sd_fg`（第 1205–1208 行），写进 `SourceData/Figure_2b.csv` 的 `Estimate` 列（第 1210–1247 行），即 Source Data 的 “Weight”。
- 论文正文另一种写法“按推导队列均值和标准差 z 标准化后加权反向求和”（Methods）只比上式多减一个常数 Σ w_i × mu_i；排序相同，但常数没有公布，所以本技能不输出中心化分数，也不给百分位。
- 能量校正（操作定义，论文没有写死到个人可用的程度）：论文 Methods 写“Food-group intakes were energy-adjusted using the residual method”，Results 写权重是“per additional serving per 2000 kcal/day”。残差法需要 HRS 推导队列每个食物组对总能量的回归截距和斜率，没有公布。本技能用比例法：x_i = 每天份数 × 2000 / 每日总能量；没给总能量时 x_i = 每天份数（相当于把一天当作 2000 千卡），报告写明这一点。两种校正对同一个人的分数会有差别。
- 份量：论文没有印每份的克数；Supplementary Data 7 只写了每个食物组在 HRS 问卷（semi-quantitative FFQ）里包括哪些食物。报告请用户按所用问卷或记录的常用份量理解。

## 核对方式（validation: draft）

论文没有印出任何个人饮食输入对应的 EDISEA，所以没有可复现的示例。查过：正文与 Methods、Supplementary Information（补充图 1–10、补充表 1–6）、Supplementary Data 1–8、Source Data 全部工作表、作者 GitHub 仓库（construct/、outcomes/、multiomics/ 全部 R 脚本）。Source Data 的 Supplementary Figure 3b 有 1,711 人的 EDISEA 值，但它是 `data_eaa$ediea`（按训练集均值中心化的 z 版本），没有附各人的食物摄入，无法用来核对。

测试做的是：

- 十个全精度权重四舍五入到三位小数后，等于正文和 Supplementary Data 2 “Primary model” 列印出的 0.003、0.002、0.002、−0.021、−0.013、−0.011、−0.008、−0.002、−0.002、−0.002（核对抄录，不是复现示例）。
- 加权和按作者代码的矩阵乘法实现；单位错、超范围、缺项时退出 3 且报告里没有分数。
