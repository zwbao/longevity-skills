# 产品合同与可复现性

1. 用户提供施测人员已经评分的原版完整 MoCA 十三个任务得分及正式受教育年数；任务得分尚未加入教育校正。
2. 技能使用已经核对并冻结的原文分值、教育校正与切点；运行时不下载数据，不向用户索要论文、附件或代码。
3. 报告允许给出原始总分、实际教育加分、校正总分与原文切点分档；不从原始答案评分，不诊断 MCI 或 AD，不预测未来风险、寿命、认知年龄或治疗效果。

## 资料查阅与可行性（2026-11-26）

本任务未提供本机全文缓存位置。上一轮 registry 的 B 理由是当前筛查不属于长期衰老风险预测，未记录缺失参数；按修订后的个人读出标准重新核对。

- 已打开 [Wiley 文章页](https://agsjournals.onlinelibrary.wiley.com/doi/full/10.1111/j.1532-5415.2005.53221.x)，其可访问内容重定向到摘要页面，未列出 Supporting Information。不能据此断言受限页面不存在其他内容。
- 已下载并完整阅读 [Concordia 大学作者机构提供的期刊全文](https://www.concordia.ca/content/dam/artsci/research/caplab/docs/Nasreddineetal2005.pdf)，JAGS 53:695–699，共五页，包括 Table 1 和 Figures 1–2。正文未点名任何 supplementary table、appendix、eMethods 或代码、原始数据仓库。全文仅保存在临时目录，不进入仓库。
- 已打开 [PubMed PMID 15817019](https://pubmed.ncbi.nlm.nih.gov/15817019/)，类型为 Evaluation Study，非综述。
- 已访问论文指向的 www.mocatest.org（现转到 [MoCA Cognition](https://mocacognition.com/)），并打开其 [Paper](https://mocacognition.com/paper/)、[FAQ](https://mocacognition.com/faq/) 和 [Reference](https://mocacognition.com/reference/) 页面。现行页面区分多个版本，下载界面需要选择版本和语言；本次没有下载登录后的试题包，不把新版本规则合并进原方法。
- 搜索 DOI 配合 supplementary/code/data，并在 GitHub、Zenodo、OSF 定向检索。命中引用本论文的其他研究及钟表绘图演示，未找到本研究公开发布的计算代码或受试者原始数据；不借用第三方算法。
- 尝试打开 Dementia Research Australia 托管的原始计分说明 `https://dementiaresearch.org.au/wp-content/uploads/2016/01/06_MoCA_Manual.pdf`，curl 和网页读取均为 HTTP 403，未读到其全文。浏览器 CDP 检查连接超时。该文件不是正文点名的补充附件；本实现不依赖其中的答题判分规则，所有计算常数都直接见期刊全文。

可行性结论：对已评分任务进行加和、教育校正与切点比较所需全部数值均在原文，不需要系数推断、参数拟合或未读到的说明文件。

## 冻结计算定义

所有任务满分均来自第 697 页 Montreal Cognitive Assessment 段：

| 输入键 | 任务 | 满分 |
|---|---|---:|
| delayed_recall_score | 延迟回忆 | 5 |
| clock_drawing_score | 画钟 | 3 |
| cube_copy_score | 立方体复制 | 1 |
| alternation_score | 交替连线 | 1 |
| phonemic_fluency_score | 音位流畅性 | 1 |
| abstraction_score | 抽象 | 2 |
| sustained_attention_score | 持续注意 | 1 |
| serial_subtraction_score | 连续减法 | 3 |
| digits_forward_score | 数字顺背 | 1 |
| digits_backward_score | 数字倒背 | 1 |
| naming_score | 命名 | 3 |
| sentence_repetition_score | 句子复述 | 2 |
| orientation_score | 定向 | 6 |

原始总分是十三项之和，最高 30。原文在执行功能和语言段落都提到音位流畅性，本实现仅累计一次。学习试次、提示回忆及后续版本的 Memory Index Score 不作为新增分数输入。连续减法输入的是已经评定的 0–3 分，不是答对次数。

第 697 页 Group Differences and Sensitivity and Specificity 段：正式受教育年数不超过 12 且原始总分不足 30 时加 1 分。已得 30 分时不加，最终最高 30。第 698 页同节：25 分及以下在筛查切点下；26 分及以上不在切点下。采用该明确方法定义，不把讨论中的“over 26”措辞当作新的切点。

输入分数限于各项满分范围内的整数。教育年数 0–40 为实现的合理性检查，不是论文纳入范围；0 只表示确认无正式教育，不表示未知。教育时间没有需要换算的额外单位，`accept` 为空；中文“年”和 years 由 skillkit 的通用单位规范处理。没有为这些字段猜测 LOINC。

## 验证合同

先写 `tests/test_manifest.py::test_printed_task_maxima_sum_to_30`，再实现计分。输入直接取上表印出的各任务满分；期望原始总分为原文印出的 30 分。教育年限取原文 12 年边界，满分不得再加，校正总分仍为 30。`validation.quote` 为第 697 页同段短摘录，省略号表示省略内容，非连续原句；每个不同的满分数值均可在摘录中核对，任务对应关系见上表。

这是印出的逐项分值与总分结构复现，不是声称原文给出一个完整的满分受试者病例。原文没有逐个受试者输入与输出表；队列均值图、散点图、敏感度和特异度也不能用合成数据重现。教育校正的其他组合、25/26 分边界、缺项、单位、范围、重复项和旧输出清理作为工程规则测试，明确不冒充原文病例。分值是整数，复现要求精确相等，不做参数精度修正。

不生成 targets/levers：这是一项已完成测评的计分核对，提高任务分数或改变教育年数不等于健康干预效果。
