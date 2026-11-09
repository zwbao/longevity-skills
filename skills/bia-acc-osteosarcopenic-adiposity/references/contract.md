# BIA-ACC 骨肌减少性肥胖表型：合同、数值来源与核对

## 产品合同

1. 用户提供自己 BIA-ACC（BioTekna）体成分报告上的骨量 T 值、肌量 S 值、体脂率，以及性别；年龄可选。
2. 技能自带论文方法部分印出的切点，不需要下载任何公开数据（论文没有补充材料，原始数据不公开）。
3. 报告给出：骨量三档、肌量是否降低、脂肪是否偏多、达到几项、是否符合 BIA-ACC 操作性 OSA 表型。不能算的：T 值和 S 值本身（厂商专有方程和参考库，论文写明不公开）；个人的年龄拐点（论文只给人群 LOESS 曲线图，没有印出曲线数值）；肌内脂肪（IMAT）没有切点，不分档。

## 切点（照印出的原文）

论文 Methods，"Anthropometric and bioimpedance measurements" 一节：

> The BIA-ACC T-score ≥ − 1.0 indicated estimated bone mass within the reference range, a score < − 1.0 and > − 2.5 as moderately reduced estimated bone mass, and a score ≤ − 2.5 as markedly reduced estimated bone mass. ... An S-score ≤ − 1.0 was used as the prespecified operational threshold for reduced BIA-ACC-estimated skeletal muscle mass ... Adiposity was defined as total fat mass ≥ 25% of body weight in men and ≥ 32% in women [19]. The operational BIA-ACC-based OSA phenotype was defined as the concurrent presence of reduced estimated bone mass, reduced estimated skeletal muscle mass, and adiposity according to these prespecified thresholds, indicated above.

> The complete prediction equations, coefficients, and analytical characteristics of the reference databases are part of the manufacturer's proprietary technical documentation and are not publicly disclosed.

注意边界：T = −1.0 恰好算「在参考范围内」（≥ −1.0），所以「骨量降低」是 T < −1.0；肌量是 S ≤ −1.0（含 −1.0）。分流程提示里写的「T ≤ −1」与原文不同，以原文为准。「骨量降低」包含中度和明显降低两档，OSA 判定用的是「reduced estimated bone mass」，即 T < −1.0。

三项是分别的判断，OSA 要求三项同时成立；没有把它们合成一个综合分。

## 复现情况（draft）

- 正文、图注、Data availability 都没有印出任何个人的 T 值、S 值、体脂率及其判定结果，没有可复现的计算示例。
- 论文页面没有列出补充材料（缓存 meta.json 的 supplement_links 为空），没有代码或数据链接；Data availability 写 "The original data are not available for public use."
- 表 1、表 2（按 OSA 分组的年龄、人体测量和体成分均值及参考值）在缓存全文里只有标题；出版社表格页（/tables/1、/tables/2）本周被人机验证拦住，未能打开。它们是组均值，也不是个人示例。
- 因此测试只核对切点边界与原文一致，`validation.status` 为 `draft`。

## 输入的取舍

- T 值别名不含泛称「T值」「骨密度T值」，避免把 DXA 骨密度 T 值误当 BIA-ACC T 值（论文 Limitations："its classifications are device-specific and not interchangeable with DXA-based clinical diagnostic criteria"）。
- 体脂率只接受百分数；写成小数（0.36）会因超出 3–75 的合理范围而停下。
- 年龄只用于提示是否在研究的 20–90 岁之内，不参与判定。
