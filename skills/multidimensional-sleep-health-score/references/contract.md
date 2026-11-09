# 六维睡眠健康评分：合同、数值来源与核对

## 产品合同

1. 用户提供自己手环或手表一周的睡眠时长、睡眠效率、睡眠中点、各晚睡眠中点的标准差，以及 PSQI 两道题（总体睡眠质量、白天难以保持清醒）的答案代码；年龄可选。
2. 技能自带论文印出的六条切点，不向用户要论文、补充表或其他数据。
3. 报告给出每个维度有利或不利、合计 0–6 分；可选 `--targets` 给出每个目标单独和全部达成时的分数。不算认知 z 分、痴呆风险或 PSQI 总分（缺 19 道题里其余 17 道）。

## 来源

| 出处 | 用到什么 |
| --- | --- |
| Marent 等，GeroScience 2026，doi:10.1007/s11357-026-02518-y，方法「Multidimensional sleep health score」 | 六条切点和 0–6 分计分 |
| 同文方法「Device-measured sleep–variables」 | 睡眠效率（GGIR 选项 2）、睡眠中点和规律（7 晚中点的标准差）的定义 |
| 同文结果「Sample characteristics」 | 基线总分中位数 5（IQR 4–6），只作人群描述 |

全文从期刊页面读取（浙江大学图书馆订阅）。补充材料 Online Resource 1（ESM 1）已打开：补充表 1A–1B 是 CANTAB 任务和复合分，2 是二次项模型比较，3 是敏感性分析，4A–7D 是各睡眠指标对四个认知领域的混合模型系数；没有睡眠评分的个人算例。代码仓库 github.com/pjmarent/PASOCA-sleep-cognition 只有 README 和 GGIR config.csv。表 1、表 2 的独立表格页本次被人机验证拦下，没有打开。

## 方法（照原文）

> Favourable device-measured domains were defined as follows: sleep duration of 6–8 h per night, sleep efficiency ≥ 85%, sleep timing with sleep midpoint between 02:00 and 04:00, and sleep regularity based on night-to-night variability in sleep midpoint < 60 min.

- 主观睡眠质量（满意度）：PSQI「During the past month, how would you rate your sleep quality overall?」答 very good 或 fairly good 为有利。
- 白天清醒度：PSQI「During the past month, how often have you had trouble staying awake while driving, eating meals, or engaging in social activity?」答 not during the past month 或 less than once a week 为有利。
- 「Domain scores were summed to yield a total score ranging from 0 to 6」。

## 论文没写死、这里的做法

- 6–8 h 和 02:00–04:00 两端都算有利（「of 6–8 h」「between」没有说开闭）。85% 照 ≥，60 min 照 <。
- PSQI 答案代码 0–3 照 PSQI 原表的计分顺序（0 最好），与论文列出答案的顺序一致；有利 = 代码 0 或 1，和论文的文字分档等价。
- 睡眠中点大于 24 时按 24 取模（GGIR 从前一晚零点起算，27.5 即 03:30）。
- 睡眠时长是睡眠期内检测到的睡眠时间（论文用 total sleep duration），不是在床时间。

## 核对

论文没有印出任何个人的输入和对应分数，所以没有可复现的算例，`validation` 保持 `draft`。测试核对：常数与方法段印出的切点逐字一致；各切点边界；分钟、小数效率、小时标准差的换算；错单位、超范围、非整数答案代码和缺项时退出 3 且不写结果；`--targets` 的单独和合计分数变化。

## 没有做的

- 不用补充表 6B 的睡眠效率系数（1.274，95% CI 0.283–2.264）推个人执行功能：结局是相对 PASOCA 基线的 CANTAB z 分，论文也没写效率进模型时是百分数还是比例。
- 不把队列中位数 5 分当作正常值。
