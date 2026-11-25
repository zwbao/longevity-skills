# 产品合同

1. 用户提供自己的腰围、身高及年龄；性别可选，腰围目标可选。
2. 技能无需用户另找公开数据；计算定义及界值已从正式论文第 284 页核对，运行时不联网。
3. 报告只提供腰围身高比及界值分档，并可给出自定腰围目标下的算术变化；没有绝对风险方程、基线风险或寿命模型，不能输出个人疾病概率、诊断或寿命。

本次为已授权的流水线实现，无需另行批准合同。

## 可行性与出处

Ashwell 等，2012，Obesity Reviews 13(3):275–286，DOI [10.1111/j.1467-789x.2011.00952.x](https://doi.org/10.1111/j.1467-789x.2011.00952.x)。

第 284 页 Biological plausibility 段明确写“WC divided by height”。同页 Practical considerations 段写：

> The mean proposed boundary value (the first cut-off level indicating risk) for WHtR was 0.5.

腰围与身高统一为相同长度单位后相除，无回归系数、截距、权重或查表。唯一筛查常数 0.5 已印出，存于 `scripts/presets.py`。本文沿用并讨论此前研究的界值，明确未对本次所纳入研究重新计算均值界值。按“腰围小于身高一半”的语义，等号归入达到界值一档，分类前不舍入。不实现疾病或性别专属界值。

## 验证缺口

检查了全文正文、Tables 1–3、Figures 1–3 的可读内容。Table 1 是研究特征和结局定义编号；Tables 2–3 是 AUC 及其差值；Figure 1 是纳入流程，Figures 2–3 是 AUC 森林图。未找到配套腰围、身高与个人 WHtR 的印刷示例；图形截图获取失败，未声称核对其图像数字。没有可执行的个人示例复现测试，因此 `validation.status` 和 `inputs_status` 均为 `draft`。测试中的测量值是合成工程输入；只验证比值恒等关系、单位一致性、界值和错误处理，不冒充原文示例。未拟合或反推常数。

## 工程定义

- 规范输入单位为厘米；m ×100、mm ×0.1、in ×2.54，系数为精确单位换算，不是论文参数。英寸值可能落入厘米范围，故普通别名必须带单位。标准键自带单位。
- 腰围 30–300 cm、身高 80–260 cm、年龄 18–120 岁是输入防错范围，不是健康参考区间。年龄只作成人适用性检查；超过正文概述的 100 岁提示外推，未成年人退出 3。
- 论文未固定腰围测量部位。重复测量保持部位与方法一致，不自动在不同部位之间换算。
- 性别可省略，不进入公式。未收集体重，不附加 BMI、体脂率或其他肥胖分类。
- `screening_category` 只取 `below_boundary` 或 `at_or_above_boundary`；低于界值不排除疾病。
- `--targets` 仅接受用户提供的腰围。身高为固定测量值，不能作为成人改变目标。`longevity-levers/1` 的 `ratio_per_unit` 为当前点的解析偏导：腰围为 `1/height_cm`，身高为 `-waist_cm/height_cm**2`。身高标为不可修改，仅解释测量误差。目标、单项变化及联合变化此处相同，因为只有腰围一个目标。
- 对错误当前输入或错误目标均停止计算。清除旧结果，写空输出、中文问题清单及带论文卡片的失败报告，退出 3；成功结果不携带旧问题。

## 材料访问记录

核查日期：2026-11-25。机器未提供图书馆缓存目录，未复制原文进仓库。

- [Wiley 文章页](https://onlinelibrary.wiley.com/doi/10.1111/j.1467-789X.2011.00952.x)：已打开，可见摘要、参考文献和出版信息；未列 Supporting Information 链接。`/doi/full/` 与 `/doi/suppl/` 路径未成功获取。
- [作者 Ashwell 网站正式版 PDF](https://www.ashwell.uk.com/documents/obesityandshape/2012%20Ashwell%20Gunn%20and%20Gibson%20%20Ob%20Revs.pdf)：网页读取工具成功提供完整 12 页的可提取文本；直接下载返回 HTTP 401，PDF 截图请求返回缓存错误。已阅读正文全部章节及三张表的可提取单元格、三幅图的题注和可读内容。
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/22106927/) 与 [Europe PMC API](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:22106927&format=json&resultType=core)：确认出版类型、卷期年及作者；没有 PMC 全文或补充文件记录。
- [OpenAlex](https://api.openalex.org/works/https://doi.org/10.1111/j.1467-789x.2011.00952.x)：未给出开放全文地址；列出 Surrey 机构记录，未列 PDF。作者网站版本由另行检索找到。
- 正文未点名任何 Appendix、eMethods、补充文件或 GitHub、Zenodo、OSF、公开数据下载。Table 1 注明完整诊断定义可向作者索取；未取得，不将其视为已核查。这些定义不参与个人腰高比计算，也不用于生成诊断。
- 浏览器 CDP 连接超时，未使用登录态；不把未取得的材料说成已读取。
