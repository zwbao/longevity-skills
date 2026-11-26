# 论文与材料核对

核对日期：2026-11-25。主文：[Razo 等，Nature Medicine 28:2056–2065，2022](https://www.nature.com/articles/s41591-022-01974-1)，doi:10.1038/s41591-022-01974-1。

## 设计、样本、物种和利益冲突

- 研究设计：人体随机试验与观察研究的系统检索、新拟合的剂量反应荟萃分析；不是一项新 RCT，也不是仅汇总已有结论的叙述综述。Europe PMC（PMID 36216934）出版类型为 `research-article`、`Journal Article`、`Research Support, Non-U.S. Gov't`。本仓库没有 meta_analysis 枚举，因此 `evidence: method` 指其原创风险曲线估计方法。
- 全部分析来源：41 项，包括 39 项 RCT、MRFIT 观察性分析、PSC 汇总队列（包含 61 项前瞻性研究）。主文 Results 报告共 1,486,007 名独立参与者、12,628 个 IHD 事件、66 个国家；这些是整项荟萃分析的数据，不能当成该用户的预测准确率或事件数。没有独立的个人预测模型训练/外部验证分组。
- MRFIT 是既往未因心脏病住院的男性，Table 2 年龄 35–57 岁、随访 6 年；PSC 是基线无既往血管病的成人，年龄 40–89 岁。其余 RCT 含不同基础风险人群：37 项为较高心血管风险，12 项有心血管疾病史，5 项糖尿病，2 项肾功能受损，16 项高血压；这些组可能重叠，不作人数相加。RCT 随访平均 3.9 年（1.8–8.4），两观察研究总体平均 6 年；研究平均年龄 66.5（标准差 12.5）岁。
- Table 2 的列为 Study name、Author and year of publication、Population、Average follow-up (years)、Age (years)、Endpoints、Outcome definition、Intervention group、Control group。补充 Table 3 为 Study name、Citation。两表未分别列出每项研究或每个干预/对照臂的样本人数，因此不从总数猜分组人数，也不把 PSC 文献标题的 “one million” 当成精确纳入人数。
- 物种：人（human）；未进行动物或细胞实验。Reporting Summary 第 3 页相关材料项均为 n/a。
- 利益冲突：Anthony Rodgers 是心血管或心脏代谢疾病低固定剂量复方产品相关专利申请的发明人之一，声明对这些申请或投资无直接财务利益；其余作者声明无竞争性利益。资助为 Bill & Melinda Gates Foundation，作者声明资助方未参与设计、数据收集、分析、解释或发表决定。

## 声称、实物和实现的对应

| 论文声称什么 | 补充材料实际有什么 | 作者代码/数据实际有什么 | 同名或相近项目与本技能的区别 |
|---|---|---|---|
| 用非线性贝叶斯正则化样条估计 SBP–IHD 曲线 | Table 4 提供 13 个血压节点的平均 RR 与含研究间异质性的 95% UI | `limetr` 为引擎、`mrtool` 为模型接口、`first_process` 与 `second_process` 为处理流程 | 本技能是冻结表格读出，不是研究级 MR-BRT 重新拟合，也不是个人绝对心血管风险方程 |
| 平均 RR 在高血压区段仍上升但变平 | Table 4 包括 100–200 mmHg，107.5 与 165 标注第 15/85 百分位；190、200 行续于下一页 | VizHub 的 `output_data` 返回 100 点平均曲线与区间，`fixed_effect_data` 另有区间 | 当前在线版本不作为 2022 年印出区间的替代 |
| BPRF 给出保守风险证据概括 | Table 5：Exposure-averaged BPRF 2.01、ROS 0.70、Star rating 5，平均范围 107.5–165，参照 100 | 框架计算 evidence score；并非个人评分器 | 五星不是个人风险等级，Table 4 的 UI 下界不是第 5 分位 BPRF |
| 调整研究特征并检查偏倚 | Table 7 为数据提取模板；Table 8 为协变量定义和完整性，不是个人回归系数 | 第一阶段要读取 IHME 本地路径中的输入和中间模型文件 | 这些模板不要求用户填写，年龄、性别、用药也不被擅自加进 RR 表 |
| 合并 RCT 与队列有方法学依据 | Appendix Section 3 说明分开拟合的敏感性分析，图在 Extended Data 6–9 | 源码提供拟合基础组件，不能声称已运行作者全部计算 | 对用户目标值的比较不等于 RCT 证明的个人治疗获益 |

## 全文与补充材料清单

1. 期刊全文 HTML（含 Results、Methods、Discussion、Data availability、Code availability、Competing interests 与 Extended Data 1–10 图注）及正文 [Table 1](https://www.nature.com/articles/s41591-022-01974-1/tables/1)、[Table 2](https://www.nature.com/articles/s41591-022-01974-1/tables/2) 已打开。Table 1 按 Background、Main findings and limitations、Policy implications 总结本文，包含研究结果概括，不增加本方法运行常数。
2. [Supplementary Information / MOESM1](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-022-01974-1/MediaObjects/41591_2022_1974_MOESM1_ESM.pdf)：下载并打开全部文件，19 个 PDF 页（封面加编号 1–18）。SHA-256 `0518a2e1b0d4680b31dc2e0309f51382aa063f4e0b47b1dd49da56675fe7446b`。
   - Tables 1、2：PRISMA 检查表（Section/Topic、Item #、Checklist item、Location）。
   - Table 3，编号页 5–8：Study name、Citation，全部来源名单。
   - Table 4，编号页 8–9（PDF 页 9–10）：SBP level (mmHg)、RR (95% UI)，为计算数值的唯一来源；主表及续页均已读取并视觉核对。
   - Table 5，编号页 9：SBP level、Relative risk (95% UI)、Exposure-averaged BPRF、ROS、Star rating。
   - Table 6：GATHER 检查表，Item #、Checklist item、Reported on page #。
   - Table 7，编号页 10–15：Category、Variable、Definition，数据抽取模板（不是系数）。
   - Table 8，编号页 16：Domain、Covariate name、Definition、Completeness (%)，研究层协变量。
   - Section 2：数据来源和 PubMed 检索式；Section 3：队列与 RCT 的敏感性分析说明，无额外逐点系数表或隐藏查表附件。
3. [Reporting Summary / MOESM2](https://static-content.springer.com/esm/art%3A10.1038%2Fs41591-022-01974-1/MediaObjects/41591_2022_1974_MOESM2_ESM.pdf)：3 页扫描/图像 PDF，已逐页渲染阅读，纯文本提取为空不代表无内容。SHA-256 `119c3c80e4fd12a7d7add3b4babf2fa70f1461cdc0f6a62ea5e5fff284831824`。包括统计检查、代码、数据可得性、人群/伦理、研究设计及材料清单，没有额外模型常数。
4. 文章页列出的补充文件就是上述两份，均已读取；未发现另列的 xlsx、Zenodo 或 OSF 发布物。PMC 浏览器入口遇到校验，但期刊全文用公开请求成功取得，不存在“只读摘要”的缺口。

## 作者代码与公开数据检查

已克隆 [ihmeuw-msca/burden-of-proof](https://github.com/ihmeuw-msca/burden-of-proof)，核对提交 `c8ad876a579cfd136850c13549aa706cd0fa2437`。读取根 README、first_process README/config.R、second_process README 与 `second_process/src/espipeline/continuous.py` 的 SBP–IHD 专用设置；遍历 risks 目录与 SBP 文本匹配。`first_process/config.R` 的输入、输出及中间模型目录是 IHME 本地路径。源码提供分析流程；本技能不依赖这些拟合资产，没有据此声称作者没有发表可计算结果，因为补充表已完整提供本合同所需值。

访问 [IHME VizHub](https://vizhub.healthdata.org/burden-of-proof/)，读取其前端调用的公开接口，确认 `risk=107` 为 SBP、`cause=493` 为 IHD：

- `api/v1/metadata/risk`、`cause`、`risk_cause`：风险与结局映射。
- `api/v1/output_data?risk=107&cause=493`：100 点；字段包含 risk、log_cause、linear_cause 及其 lower/upper，另有 sex_name、age_group_name、location_name、category_id。
- `api/v1/fixed_effect_data?risk=107&cause=493`：100 点，另一个区间版本。
- `api/v1/study_citations?risk=107&cause=493`：41 条 study_id/citation。
- `api/v1/study_data?risk=107&cause=493`：191 条研究观测，含参照/暴露范围、观测对数 RR/标准误、study_id、collection_method、年份及 outlier 状态。

当前输出在 200 mmHg 的均值约 6.6387，但 `output_data` 的上下界约 5.5899–7.8844，与 2022 补充表的 5.41–8.15 不同；`fixed_effect_data` 也不能替代印出的含异质性区间。本技能固定使用补充表原值；在线曲线不被拿来拟合或更新常数。所有下载临时文件保留在仓库外，运行无网络依赖。

## 原文内部差异与适用边界

- 主文 Results 的人数/事件数为 1,486,007 / 12,628；Reporting Summary 第 2 页写 1,492,452 / 12,210。这里采用主文并保留差异，不自行合并。
- Results “Systematic bias and publication bias” 写漏斗图提示偏倚且 Egger P<0.05；Methods “Evaluation of publication and reporting bias” 写未发现偏倚。故不向用户断言“完全没有发表偏倚”。
- Reporting Summary 提及 Table S5 为数据来源名单，但实际文件名单在 Supplementary Table 3；Table 5 实际是 BPRF 汇总。
- 正文在 Mean RR function 给出 115 和 135 mmHg 数值，表 4 不含这两个节点；保留为独立插值检查，不能声称它们是表格行。
- 作者未进行性别分层个人风险校准，结局定义和人群异质；风险可逆性是合并 RCT 与队列的假设。低端和极高端资料稀疏，原模型右端尾部受约束；家庭单次测量不等于长期暴露，用户的读数不能据此变成个人预后。
