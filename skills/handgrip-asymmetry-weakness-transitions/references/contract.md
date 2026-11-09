# 两次握力模式与全因死亡：合同、数值来源与核对

## 产品合同

1. 用户提供自己前后两次测的左右手握力（每只手测两次取最高），第二次测量时的年龄、性别和惯用手；第一次测量时的年龄、两次体质指数和确诊慢病数可选。
2. 技能自带论文印出的切点和风险比（正文方法、结果和补充表 S11、S12、S14），不向用户要论文、PDF 或其他数据。
3. 报告给出两次的左右握力比、最大握力、两种异常各自的两次模式、第二次的联合异常分，以及论文里对应模式相对参照组的全因死亡风险比；给了慢病数时加补充表 S12 分层；给出两项连续变化在论文人群里的百分位位置。不估算个人死亡概率或预期寿命，不诊断肌少症，不给治疗或用药建议。

## 来源

| 代号 | 出处 | 用到什么 |
| --- | --- | --- |
| [P] | Xu D, Lin B, Ran Z. Two-wave status patterns of handgrip strength asymmetry and low handgrip strength in relation to all-cause mortality in middle-aged and older Chinese adults. GeroScience (2026). doi:10.1007/s11357-026-02558-4 | 方法“Assessment of muscle phenotypes and two-wave status patterns”的测量、切点和分型；结果段落里表 2 的风险比 |
| [S] | 同文 Supplementary Material ESM1（PDF，30 页，补充表 S1–S26），https://static-content.springer.com/esm/art%3A10.1007%2Fs11357-026-02558-4/MediaObjects/11357_2026_2558_MOESM1_ESM.pdf | S10 各模式死亡数；S11 连续变化的风险比和百分位节点；S12 慢病分层风险比；S14 未加权列（与表 2 相同）；S16 强手定义 |

全文从浙江大学图书馆订阅的期刊页面读取。表 2 在页面上是图片，数值取自结果段落的逐项文字，并与补充表 S14 的“Unweighted HR (95% CI)”列逐项对上（两处一致）。

## 方法（照原文）

- 握力：“Handgrip strength (HGS) was measured twice for each hand using a Yuejian WL-1000 dynamometer, and the maximum value recorded for each hand was used in the analysis.”
- 左右不对称：“HGSA was defined using the ratio of non-dominant to dominant HGS. In the primary analysis, HGSA was classified as a ratio < 0.90 or > 1.10”。
- 握力低：“< 34.0 kg for men and < 20.0 kg for women aged < 65 years, and < 28.0 kg for men and < 18.0 kg for women aged ≥ 65 years”，每次按当时年龄判断。用的是最大握力（两手的较高者；补充表 S2 写作 “Maximum HGS”）。
- 四种模式：两次都正常、第二次新出现异常（第一次正常、第二次异常）、第二次恢复正常（第一次异常、第二次正常）、两次都异常（补充表 S10 的注释）。
- 联合异常分：第二次有不对称记 1 分，有握力低记 1 分，0–2 分。
- 连续变化：AAI = |握力比 − 1|，ΔAAI = 第二次 − 第一次；RGS = 最大握力 ÷ 体质指数，Loss RGS = 第一次 − 第二次。

## 风险比（照印出的数）

| 模式 | 不对称（HGSA） | 握力低（LHGS） |
| --- | --- | --- |
| 两次都正常 | 1（参照） | 1（参照） |
| 第二次新出现异常 | 1.07 (0.86–1.33) | 1.91 (1.54–2.37) |
| 第二次恢复正常 | 0.97 (0.78–1.22) | 1.54 (1.21–1.97) |
| 两次都异常 | 1.32 (1.07–1.61) | 2.35 (1.88–2.94) |

联合异常分：0 分参照；1 分 1.22 (1.02–1.46)；2 分 2.30 (1.84–2.87)。
连续：ΔAAI 每 1 单位 1.66 (1.14–2.42)，节点 −0.133949、0.000734、0.142560；Loss RGS 每 1 单位 2.39 (1.86–3.08)，节点 −0.398013、0.049102、0.476531（补充表 S11）。
慢病分层全部抄在 `scripts/presets.py` 的 `S12_HGSA`、`S12_LHGS`、`S12_JOINT`。

## 操作定义（论文没写死，这里的约定）

- 自报“两手一样”：论文主分析没写这时的分母。本技能用补充表 S16 Panel B 的强手定义（weaker/stronger ratio），这时比值不会大于 1。报告写明。
- 惯用手只问一次，两次测量都用它；论文按每一轮的自报惯用手。
- 没给第一次测量时年龄：第一次的握力低切点按第二次的年龄段取，并在 65 岁及以上时提示补上。补充表 S17 显示按第一次年龄段判断第二次时风险比几乎不变，但这不是同一件事，所以只作提示。
- 慢病数 ≥ 2 归入“≥2 chronic conditions”层；慢病清单照补充表 S12 注释。

## 核对

论文没有印出某个人两次握力对应的结果，所以没有可复现的个人算例；`validation` 保持 `draft`。测试核对：常数与正文和补充表 S11、S12、S14 印出的一致；切点边界（比值正好 0.90、1.10 不算不对称；握力正好等于切点不算低；正好 65 岁用 65 岁及以上切点）；四种模式和联合分查回的风险比；单位错、缺值、性别或惯用手写错时退出码 3。

## 没有做的

- 不把每单位风险比（ΔAAI 1.66、Loss RGS 2.39）外推成个人风险比：只到两位小数，样条显示 Loss RGS 有接近显著的非线性（P = 0.057），而且模型还调整了基线值。只报告百分位位置。
- 不估算个人死亡概率：论文没有给基线生存函数。
- 不按两次测量的实际间隔调整。
