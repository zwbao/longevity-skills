# 获取与参数可行性审计

核查日：2026-11-24。本机没有用户指定的图书馆缓存目录。全文及附件只在临时目录阅读，未复制进技能仓库。无未打开的补充附件。

## 一手来源

- [medRxiv版本API](https://api.biorxiv.org/details/medrxiv/10.64898/2026.06.29.26356268)：确认v1（2026-07-09）和v2（2026-11-12）；API摘要可能已更新，不能据此把v1标为v2。
- [v2全文](https://www.medrxiv.org/content/10.64898/2026.06.29.26356268v2.full)及[全文PDF](https://www.medrxiv.org/content/10.64898/2026.06.29.26356268v2.full.pdf)：读取全部正文、表1、表2及图注；PDF Data sharing另列作者GitHub。
- [附件列表](https://www.medrxiv.org/content/10.64898/2026.06.29.26356268v2.supplementary-material)：只列一个Supplementary appendix（356268_file02.pdf）。
- [29页附录](https://www.medrxiv.org/content/medrxiv/early/2026/11/12/2026.06.29.26356268/DC1/embed/media-1.pdf)：已逐页阅读提取文本，S1–S22与附加方法均核查。响应元数据更新时间为2026-11-16。
- [Data/Code页](https://www.medrxiv.org/content/10.64898/2026.06.29.26356268v2.external-links)：列[CDC NHANES](https://www.cdc.gov/nchs/nhanes/index.html)，已打开；没有独立Zenodo/OSF存档链接。
- [作者仓库](https://github.com/fangxin0922/Heavy-metal-exposure-and-all-cause-mortality-in-U.S.-adults)，已克隆并检查，commit `b51882da3c19bccdcfb0c4b80841eeaac126fdc4`。读取主分析README、scripts/README、模型目录、暴露预处理、样条预测、validation/PROTOCOL及tests/VALIDATION，枚举全部受控文件。仓库没有根README、研究参与者数据、原始analytic.rds、主模型拟合对象或结果系数文件；代码明确注明这些缺口。原始数据下载器与NHANES III来源清单不提供缺失的主研究档案。

访问过程：medRxiv直接请求、网页工具和XML入口受Cloudflare或访问错误阻碍，浏览器CDP代理连接超时；随后通过Jina Reader读取同一官方URL的全文、PDF和附件文本成功。HTML全文提取不含表2单元格，因此以全文PDF与附录PDF提取互核；错误的单表URL `/v2/T2`只返回站点导航，未作为证据。未从第三方新闻摘要取系数。

## 已打开的附件内容与列

| 页/表 | 实际列与内容 | 本技能用途 |
|---|---|---|
| p2–3方法、p4–6图S1–S3 | 权重、插补、重复与敏感性设计，DAG和图注 | 界定统计量 |
| p7 S1 | Cohort, Metal, Enrolment, N/deaths, M/iterations, Available cells | 样本与NE核对 |
| p8 S2 | Covariate，四金属N与缺失百分比 | 背景核对 |
| p9 S3 | Metal，10th/25th/50th percentile；每格I1–I5、β、95%CI、p或NE | 唯一计算系数来源，与正文表2相同 |
| p10 S4 | Biomarker/context, Study/design, Evidence | 不作补剂效益解释 |
| p11 S5 | Metal, Biomarker, Enrolment, N, Deaths, Units, P25, P75 | 样本盘点 |
| p12–14 S6–S8 | Metal，三个分位点；P25、P75、IC、p、BH q、finite replicates | 不实现探索交互 |
| p15 S9 | Metal，三个分位点的I1–I5估计/CI/p | 独立队列背景 |
| p16 S10 | Metal/enrolment, N, All deaths, Cancer, Heart disease, Stroke, Cardiovascular, Other causes, Alive | 样本盘点 |
| p17–18 S11–S12 | Metal，三个分位点的I1–I5估计/CI/p或NE | 不输出原因别死亡 |
| p19 S13 | Sensitivity, Metal, N/deaths, Excluded missing/low eGFR, Imputation | 受限队列核对 |
| p20–22 S14–S16 | Metal，三个分位点的I1–I5估计/CI/p或NE | 尤其保留镉调整后关联消失的说明 |
| p23–24 S17–S18 | Sensitivity或Endpoint/metal，三个分位点的估计范围、可估计数、CI排零数 | 解释边界 |
| p25 S19 | Metal，三个分位点I1–I5估计/CI/p或NE | 汞饮食敏感性背景 |
| p26附加方法 | 金属测定、尿砷构成、肌酐标准化方程描述 | 确认血铅无需尿标准化；未印尿肌酐预测系数 |
| p27 S20 | Variable, Source/analysis field, Definition/model coding | 调整集与年龄用途 |
| p28 S21 | Survey cycle, Q1–Q4 min/max/n；饮酒规则 | 非本技能计算切点 |
| p29 S22及讨论 | Source, Participants, Unweighted percentage；bias/uncertainty | 未合并与不确定性边界 |

可行性结论：只计算血铅同协变量条件下的对数线性浓度差，所需全部13个斜率与2个NE均印出；不需要缺失的完整预测参数。没有猜测、拟合或从记忆补常数。正文明确1.57与3.14 µg/dL翻倍例子，足以测试转换和系数使用。代码仓库缺少研究档案不构成本合同的计算阻碍。
