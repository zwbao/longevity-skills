用户提供九项表型年龄血液指标、实足年龄，以及可选的性别、四项 PHQ-4、现用药和体检。技能使用已经写进脚本的 BioAge 原始表型年龄系数，不会向用户索取 NHANES、GEO、STRING、UK Biobank 或 PDF。报告可以给出表型年龄以及它和实足年龄的差，并写明 KDM 与队列残差没有计算；它不把表3的每个标准差风险比套到这一个人身上，也不建议开始或停止任何药物。

## 核对方式（validation: reproduced_secondary，显示为“已与独立实现核对”）

论文没有印出任何个人输入对应的表型年龄，所以这里不是复现论文的例子，而是与两个独立实现逐例核对，误差都要求在 0.01 岁以内（`tests/test_validation.py`）：

1. **BioAge**（dayoonkwon/BioAge，commit b1f9fc0，0.1.0，GPL-3）：`data/NHANES3.rda`（SHA-256 c1b940fc…0b92）里由 `R/phenoage_calc.R`（orig=TRUE）算好的 `phenoage0`。这是 NHANES III 的真实调查数据（美国联邦公共领域），BioAge 的 CRP 列是 `log(1+crp)`，所以用脚本的 log1p 模式比。全部 8,924 行最大差 6.1e-08 岁；测试里放了每隔 743 行取的 12 行。读法：用 pyreadr 读 rda，只取输入列和 `phenoage0`。
2. **FALCONAge**（bhagesh-h/FALCONAge，commit 86db10d，GPL-3）：`python/src/falconage/models/clinical.py` 的 `phenoage(crp_transform="log", coefficients="bioage")`，在 7 个合成输入（不是真人）上运行，最大差 3.4e-06 岁。本机没有安装这个包：逐行审读了这个函数（第 65–200 行，只有 numpy 算术）后单独运行。还有一个合成输入（84 岁、CRP 2.5 mg/dL、血糖 11.2 mmol/L）死亡风险在浮点下等于 1，本脚本拒算，FALCONAge 截断后给出 120.67，没有放进比对。

没有用作证据的两项：

- pyaging 0.5.7（PyPI）的临床表型年龄用论文表 1 和补充表 S1 印出的四位小数系数（截距 −19.9067，γ=0.0076927），在同样 8 个合成输入上比本脚本高约 0.07 岁（例如 50.549 对 50.475）。这是系数四舍五入造成的差，不是算法差异。
- 论文正文印出“NHANES IV（n=6,209）里表型年龄与实足年龄相关 r=0.94”，但没写清这 6,209 人怎么选的。用 CDC 公开的 NHANES 1999–2000、2001–2002 文件（DEMO、LAB18/L40_B、LAB25/L25_B、LAB11/L11_B），20 岁以上九项齐全的 8,263 人算得 r=0.915，对不上，记在 `gap_zh`。
