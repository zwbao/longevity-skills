# 握力切点与死亡风险比：合同、数值来源与核对

## 产品合同

1. 用户提供自己测的握力（优势手两次中的最大值）和性别，身高、年龄可选。
2. 技能自带论文方法里印出的 EWGSOP2、FNIH 切点和补充表 S3 的风险比，不向用户要论文、PDF 或其他数据。
3. 报告给出按两个切点的分档、低于切点时该性别低握力组相对达到切点者的全因死亡风险比（补充表 S3 模型 2 为主，同时列模型 1），以及身高校正握力数值。不按四分位分组（界值在没能打开的正文表 2、表 3），不算标准化分数（标准差在表 1），不做 Tomkinson 常模分组（百分位表在另一篇论文），不估算个人死亡概率，不诊断肌少症。

## 来源

| 代号 | 出处 | 用到什么 |
| --- | --- | --- |
| [P] | Pérez-Sousa 等. Sex-specific associations between handgrip strength and all-cause mortality in older Mexican adults. GeroScience 2026. doi:10.1007/s11357-026-02639-4 | 方法“Assessment of muscle strength”（测量、身高校正握力定义）、“Statistical analysis”（EWGSOP2、FNIH 切点）；结果里的人群数和 HR |
| [S3] | 同上，Supplementary Material 2（11357_2026_2639_MOESM2_ESM.pdf），补充表 S3 | 低握力组人数、死亡数、模型 1/2 HR |

全文读自浙江大学图书馆订阅的期刊页面文本。补充材料 1–3 从 static-content.springer.com 下载打开。正文表 1–4 的表格页被期刊站的人机验证拦住。

## 方法（照原文）

- 握力：“Participants performed two trials for each hand, and the maximum value obtained from the dominant hand (in kg) was used as the primary predictor.”
- 身高校正：“allometric HGS (HGS divided by height squared, kg/m2)”。
- 切点：“low absolute HGS defined by EWGSOP2 (< 27 kg in men and < 16 kg in women) and FNIH (< 26 kg in men and < 16 kg in women), using participants at or above each cut-off as the reference group.” 所以正好 27 kg 的男性按 EWGSOP2 算达到切点。

## 风险比（补充表 S3，照印出的数）

| 标准与性别 | 低握力 n | 死亡 | 模型 1 HR (95% CI) | p | 模型 2 HR (95% CI) | p |
| --- | --- | --- | --- | --- | --- | --- |
| EWGSOP2 男 (<27 kg) | 190 | 84 | 2.112 (1.537–2.901) | <0.001 | 2.302 (1.653–3.206) | <0.001 |
| FNIH 男 (<26 kg) | 155 | 72 | 2.002 (1.449–2.766) | <0.001 | 2.237 (1.596–3.136) | <0.001 |
| EWGSOP2/FNIH 女 (<16 kg) | 157 | 49 | 1.531 (1.093–2.144) | 0.013 | 1.268 (0.893–1.799) | 0.185 |

正文结果把这些数四舍五入到两位小数（2.30、2.23、1.53、1.26；正文写 “HR 1.26, 95% CI 0.89–1.79”），与 S3 一致。

## 核对

论文没有印出某个人握力对应的结果，所以没有可复现的个人算例；`validation` 保持 `draft`。测试核对：常数与方法和补充表 S3 印出的一致；切点边界（严格小于才算低）；分档查回的 HR；磅换算；单位缺失、超范围、缺性别时退出码 3。

## 没有做的

- 四分位分组和每标准差 HR 的个人换算：需要表 1–3 的界值和标准差，本次没能打开。下次拿到正文表格后可以补上。
- 不加 `--targets` 和 levers：这是两档切点的查表，不是可以连续对着定目标的风险方程。
- 补充表 S1、S2 是抽样加权模型，死亡数是加权数、没有四分位界值，不用于个人读出。
