# 产品合同与可行性核对

1. 用户提供本人 LDL-C 的绝对下降量及维持该下降量的年数；也可明确提供假设下降量及未来持续年数，并可给目标文件作情景比较。
2. 技能内置原文表2脚注的全部计算常数，无运行时网络或队列下载，不向用户要任何研究文件。
3. 报告仅给出这组输入下的相对风险与相对风险下降比例；不计算绝对发病概率、ARR、NNT、寿命、药物剂量或用药决策，也不将长期外推当成个人疗效保证。

用户已在流水线任务中授权创建此个人计算技能；无需额外批准产品合同。

## 检索材料（2026-11-26）

- 本机没有用户指定的图书馆缓存路径，未从缓存复制文件。
- [DOI](https://doi.org/10.1093/eurheartj/ehx144) 与 [OUP 文章页](https://academic.oup.com/eurheartj/article/38/32/2459/3745109)：已尝试，网页工具重定向到不可读取的 Silverchair minimal 页面，直接请求遇验证页，浏览器 CDP 前置连接超时。未声称读取到了出版社页面的附件列表。
- [PMC 正式发表全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC5837225/)：已读全文、表1–4、Box 1、图注、Funding、Conflict of interest 和参考文献。不是只读摘要或替代预印本。
- [Europe PMC 全文 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5837225/fullTextXML)：已取到完整 XML 并核对表2–4、所有外链与附件标签；没有 supplementary-material/media 附件条目，也未点名 Supplementary Table、Appendix、eMethods 或 GitHub、Zenodo、OSF 计算代码/数据。本计算所需全部参数均在正文。没有未下载的已列出补充文件。
- [Europe PMC 元数据](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1093/eurheartj/ehx144&format=json&resultType=core)：核对 PMID 28444290、PMCID PMC5837225、Review / Consensus Statement / Journal Article 类型及正式发表信息。
- 元数据列出的 [eScholarship 开放副本](https://escholarship.org/uc/item/00c5w2j6) 也尝试过，返回 JavaScript 验证页；已用 PMC 和 Europe PMC 正式全文完成方法核对。

全文原始下载仅留临时目录；技能不保存整篇全文或其他研究的缓存。

## 打开的表与列

| 表 | 已检查的列 | 用途 |
|---|---|---|
| 1 | Criterion、Evidence grade、Summary of the evidence | 因果证据背景，不作个体评分 |
| 2 | Baseline LDL-C、Absolute reduction LDL-C、5/10/20/30/40 years expected proportional risk reduction、Guideline recommended treatment | 仅计算相对风险；不用指南推荐列 |
| 3 | 10-year absolute risk、Baseline LDL-C、LDL-C after 50% reduction、Proportional risk reduction、10-year risk after reduction、ARR、NNT、Guideline recommended treatment | 核对后排除，表值与脚注不一致 |
| 4 | 30-year absolute risk、Baseline LDL-C、LDL-C after reduction、Proportional risk reduction、30-year risk after reduction、ARR、NNT、Guideline recommended treatment | 核对后排除，表值、脚注和时间窗不一致 |

## 方程与常数逐项来源

设 d 为 LDL-C 绝对下降量（mmol/L），t 为持续年数。

表2脚注给每下降1 mmol/L在任意指定时间的对数相对风险 `b(t) = -0.249 + (t - 5) × (-0.0152)`。同一脚注在5年与40年分别给出 `1 - 0.78^d` 与 `1 - 0.46^d`，说明降幅在相对风险对数尺度上线性进入。因此将任意时间的每单位公式按同一降幅关系扩展，使用 `RR = exp(d × b(t))`，`RRR(%) = 100 × (1 - RR)`。这是表2脚注的代数合并；未拟合任何系数。脚本始终使用印出的 -0.249、-0.0152、5，不将5年与40年另切成0.78与0.46的特殊分支，以免人为引入不连续。

表中持续时间从5到40年，最大下降量3.5 mmol/L。本实现将这两个范围作为支持边界，而非生理切点；时间允许连续小数，遵循脚注任意指定时间的公式。零降幅是公式的无变化恒等情景。不实现1–3年的近似叙述为独立算法，不外推到5年以下或40年以上。基线浓度本身不进入方程，故不要求它，也不复制基线对应的用药推荐。

输入单位只做 SI 前缀的精确转换：umol/L × 0.001 = mmol/L。没有采用表3、4约40 mg/dL对应1 mmol/L的粗略展示值，也不另猜分子量或转换常数。输入是差值而非一个可用单项 LOINC 表示的检测量，故不贴单次 LDL-C 检测的 LOINC。别名明确带“下降量/reduction”，不将 LDL-C 本身设为别名。

## 复现与已知不一致

先写 `tests/test_manifest.py::test_table2_printed_examples`，再写计算脚本。测试期望数逐个抄表2：基线7、下降3.5的行在5/10/20/30/40年为58/68/81/89/93%；基线3、下降0.5的行为12/15/21/27/32%。十个单元格都以整数百分比显示，测试容许最多0.51个百分点，未由脚本输出生成期望值。最初按纯整数舍入的0.5个百分点容差检验，3.5 mmol/L、40年的计算结果约93.50086%，刚超过93%的半点舍入区间。脚注对数系数本身只印到三位/四位小数，足以跨越这一区间边缘；额外容许0.01个百分点并明确记录，而不修改论文期望值或模型常数。基线是定位行的说明，不是公式输入。

`validation.status = reproduced` **仅指以上所选示例**，不声称整篇所有表格都可复现。具体差异保留如下：

- 表2：下降1.0、30年印46%，脚注方程得到约46.69%；下降2.0、30年印71%，方程约71.58%。差异超过通常的半个百分点整数舍入误差。没有放宽复现测试容差以掩盖这些单元格，也没有据此修正常数。
- 表3：下降1.0时表内比例为20%，脚注 `1−0.78^1` 为22%；表头又将5年治疗对应的比例应用于10年基线风险。不能称已按脚注复现表3。
- 表4：下降1.0时表内比例为50%，脚注 `1−0.46^1` 为54%；表头标30年而脚注写40年。表2时间方程的30年值约46.69%，同样不是表4的50%。

没有将表3或4反推得到的常数当作发表参数，也没有利用它们制作第二个算法。本技能的产品合同限于表2脚注相对风险方程；绝对风险输出因上述未解决的不一致而不实现。

## 敏感度与目标

解析导数：`∂RRR/∂d = -100 × RR × b(t)`；`∂RRR/∂t = -100 × RR × d × (-0.0152)`。单位分别为百分点/(mmol/L)、百分点/年。这是原公式的导数，不是新增拟合系数。`levers.json` 逐项只改变一个输入，再计算全部目标共同达成的结果；不给定默认目标。不把“多持续若干年”写成可立即实施的个人行为。独立有限差分测试核对导数。

## 输出边界

报告与失败报告均由 paper_card 模块生成论文卡片。年龄、性别、用药与其他化验不进入本方程。公式不判断药物副作用、不验证 LDL-C 与颗粒数是否一致，也不从两次化验推断真实长期暴露。相对风险不是概率；没有可靠的个体同时间窗基线风险，本技能也不引入外部风险算法补齐。
