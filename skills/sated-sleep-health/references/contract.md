# 产品合同与来源核对

用户提供自己的五项频率回答，助手按原图编码为 CSV，不接受原始小时、分钟或设备评分替代频率回答。技能不需要联网运行，所需计分常数已经从原始 Figure S1 核对并固定到 presets.py。报告只给五项分值、加总和可选回答变化情景，不给诊断、风险或寿命预测，不把计算复现解释成量表验证。

## 可行性核对（2026-11-25）

- 本机未提供图书馆缓存路径，未复制任何缓存文件入库。
- DOI 与 Oxford Academic 文章页 `https://academic.oup.com/sleep/article/37/1/9/2454038` 重定向到不可访问的 Silverchair 页面。
- 已完整读取 [PMC 文章](https://pmc.ncbi.nlm.nih.gov/articles/PMC3902880/)，包括内嵌补充正文、图注、披露和参考文献。
- PMC Figure S1 单独文件 `aasm.37.1.9s1.tif` 返回验证码，不能声称下载成功。浏览器 CDP 检查连接失败；Europe PMC HTML/PDF 受限，fullTextXML 返回服务器错误。NCBI OA 接口尝试返回 404。
- 最终从 [Penn CBT-I 文章库](https://www.med.upenn.edu/cbti/sleep_health.html) 的 Buysse 2014 下载入口取得 [原论文 PDF](https://www.med.upenn.edu/cbti/assets/user-content/uploads/PMF%202024/Buysse%202014%20Sleep%20Health%20Can%20we%20Define%20it.pdf)。读完全部 12 页：正文 9–17，补充 17A–17C；将 PDF 第 11 页渲染后直接查看 Figure S1。下载失败的 TIFF 内容由此处原始论文中的同一图核对，非第三方重建。
- Table 1（印刷页 12）的列名为 Sleep Measure、Associated Health Outcomes、Sample References；它是关联与参考文献清单，不是个人风险系数。Figure 1 为概念路径图，不用于计算。补充材料仅列补充正文和 Figure S1，未点名计算所需的其他补表、代码仓库或数据发布，无 GitHub/Zenodo/OSF 链接需要补取。

## 计分来源

Figure S1（17B）五行顺序为满意度、清醒度、时间安排、效率、时长；三列回答对应的分值为 0、1、2，所有行使用同一映射。输入已经是明确回答的数值编码，脚本仍通过同一映射计算单项，再将五项相加；没有加权、插补或反向计分。原图总分范围为 0–10。

原图题面含凌晨 2:00–4:00、夜间清醒总计少于 30 分钟（含入睡与睡后觉醒）、每天睡眠 6–8 小时。这些只用于询问频率，不是从一晚记录自动分类的切点；原文没有给出一周多少天算某档、回忆周期或数值观测到频率档位的算法，因此不实现这种换算。

没有从后来的 RU-SATED 或其他 SATED 版本移入题目、规律性维度、时长范围或阈值。中文是工作译文。可选年龄的 18–120 范围是成人使用及录入错误检查，不是模型参数，不进总分；性别也不进总分。分数单位没有可换算的物理单位，不填不确定的 LOINC。

## 验证合同

首先编写 `tests/test_manifest.py::test_figure_s1_printed_item_scores`，期望分值直接来自 Figure S1 的三个列标题，manifest 保留短逐字引文。其验证范围是逐项分值对应关系，属于流水线允许的 per-term scores；全文、Table 1、Figure 1、补充 17A–17C 未印出已填答的个人病例及总分。总分端点另作算术检查，不冒充独立的病例复现。整数精确相等，无常数拟合、推导或第三方输出。

目标模式只替换明确指定的回答档位并重新加总；敏感度列举同一项目另两档的分数差，不对离散量表求导。改变回答造成的分差不是已验证的健康改善量，原论文也没有最小临床重要差异。
