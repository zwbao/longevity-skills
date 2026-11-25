# 证据与材料核查

- 研究设计：人体前瞻性队列个体资料整合，用 Fine–Gray 竞争风险模型推导、按地区再校准、在独立队列验证；这是原创风险模型研究，不是随机干预试验或综述。
- 全部样本组：模型推导为 13 国 45 队列（正文写 44 个 ERFC 队列加 UK Biobank），677,684 人，30,121 CVD 事件；地区乘数估计 10,776,466 人（男性 5,256,013，女性 5,520,453），731,265 CVD 事件；外部验证为 15 国 25 队列，1,133,181 人、43,492 CVD 事件。三类数据用途不同，不相加成独立总样本，也不称为病例/对照随机分组。队列名称与描述分别见更新 Tables S1/S2/S4 和 Appendix 1。
- 物种：人（human）。没有动物或细胞实验。推导样本含欧洲外队列，但最终地区校准与主要个人用途是论文定义的欧洲风险地区，不能因此称对全球有效。
- 利益冲突：已读正文完整 Conflict of interest。多位作者披露机构研究资助、咨询/讲课费、顾问委员会和行业合作；包括 A.S.B. 的 AstraZeneca、Bayer、Biogen、Novartis 等机构资助，B.A.F. 的 Novartis/Amgen/Esperion 资助及多家药企咨询讲课关系，J.D. 的 MSD/Novartis/Pfizer/AstraZeneca 关系，N.S. 的 Boehringer Ingelheim 机构资助和多家药企咨询/讲课费，P.M.R. 的 Novartis/Amarin/Pfizer/Kowa 资助与咨询，T.O. 的 Novartis/Abbott/Roche/SomaLogic 支持、咨询及 Granin proteins（PCT/GB0818650）、SgII 专利披露，V.S. 的 Novo Nordisk/Sanofi 咨询及 Bayer 研究合作。不是“无利益冲突”。正文未声明此风险算法的专利或授权收费；不据此否定已披露的其他利益关系。资助还包括 BHF、MRC、NIHR 及 GlaxoSmithKline 非限制性教育资助。全部逐人声明以正文为准。

| 论文声称什么 | 补充表里实际有什么 | 代码仓库实际算什么 | 同名或相近项目区别 |
|---|---|---|---|
| 估计十年首次致死和非致死 CVD | 更新 Methods Table 2 的男女 Log SHR、连续变量变换、基线生存；Table 3 四地区男女 Scale1/2；Table 4 完整示例 | 正文仅说 Stata 代码按请求提供，无公开仓库；本技能独立转录已印方程 | 原 SCORE 只估计致死 CVD，不等同 SCORE2 |
| 适用于 40–69 岁、无既往 CVD 或糖尿病 | Methods Box 1 说明糖尿病在推导时纳入，而个人预测设 0；Methods Table 2 注释再次排除糖尿病用途 | 本地拒绝超范围年龄、既往 CVD、糖尿病；不训练新模型 | SCORE2-OP 面向更老年龄；SCORE2-Diabetes 有不同变量和参数 |
| 按欧洲四地区校准 | Table S6 国家死亡率与分组；Methods Table 3 再校准系数 | 本地用户明确选地区，并确认属于已列国家；无动态更新 | 不使用 SCORE2 Asia-Pacific、SCORE2-LAC、PREVENT 或 China-PAR 参数 |
| 改善群体风险识别 | 外部验证各队列 C-index 约 0.67–0.81；S11/S12 比较 SCORE 与 SCORE2 | 仅计算个体预测风险，不把 C-index 当个人置信区间 | 无证据表明目标情景差就是个人治疗效果 |

## 已打开文件和表格列名

期刊文章页：<https://academic.oup.com/eurheartj/article/42/25/2439/6297709>；其公开正文版本 <https://oup.silverchair-cdn.com/article-minimal/6297709> 成功，获取唯一的 `ehab309_supplementary_data.zip` 正式下载链接。PMC 正文 <https://pmc.ncbi.nlm.nih.gov/articles/PMC8248998/> 已通过直接请求读到，内容用于核对方法、结局、示例和利益冲突。期刊默认页和 DOI 跳转受到网页工具限制，PMC 附件返回下载验证页，Europe PMC 接口返回服务错误；最终采用期刊正式 CDN 的更新 ZIP，未从第三方计算器补参数。

ZIP 内恰为以下两份文件，均已打开。访问日期与 SHA-256 见 `sources.json`；原始文件仅在 /tmp，不放入仓库。

1. **SCORE2 Updated Supplementary Material.docx**：目录列 Supplementary Methods、Tables S1–S12、Figures S1–S15、研究者名单；Methods 内还含 Tables 1–4 和两幅方法流程图。全部 Word 表格已提取并检查，参数只来自更新 Methods Tables 2–3。
2. **SCORE2_Appendix_1.docx**：推导队列、乘数数据来源、验证队列介绍与参考文献；表头为 Cohort / Country / Description of study，验证表也用 Study / Country / Study-cohort full name and short description。不是代码附件。

| 位置 | 实际列名/内容 | 个人计算用途 |
|---|---|---|
| Methods Table 1 | Mean or prevalence of risk factor values; Log SHRs from ERFC/UKB fitted model; Calculation of 10-year cumulative incidence；另有 annual CVD/non-CVD mortality 和 multipliers | 说明地区校准过程，是人群均值例子，不作为个人输入 |
| Methods Table 2 | Risk factor (units); Transformation equation; Log SHR Male/Female; SHR Male/Female；末行 Baseline survival | 完整连续模型系数与变换 |
| Methods Table 3 | Risk region; Male Scale1/Scale2; Female Scale1/Scale2 | 四地区校准 |
| Methods Table 4 | Risk factor (units); Risk Factor Value; Transformed value; Log HR×transformed value Male/Female；随后 Linear predictor、un-calibrated risk、Risk region/Male/Female | 独立计算示例 |
| Table S1 | Country; Cohort; No of participants; Ages Mean(SD); Men; Current smoker; Systolic BP; Total cholesterol; HDL cholesterol; Diabetes; Median follow up; CVD; CVD before 10-years; Other death; Other death before 10 years; Median year of recruitment | 推导样本描述 |
| Table S2 | Risk region; Country; Data source; Number of participants; Ages; Men; Median follow-up; CV events; Median year | 乘数样本 |
| Table S3 | Country; Source; Reference; ICD codes included in endpoint，分 Mortality/Incidence data | 验证地区发生率的数据来源 |
| Table S4 | Data sources; Country; Cohort; Risk region; No of participants; Ages; Men; Current smoker; Systolic BP; TC; HDL; Median follow-up; CVD events; Median year | 外部验证组 |
| Table S5 | Endpoints included; ICD10-codes; ICD9-codes，包含 fatal/non-fatal 和排除的卒中终点 | 结局定义；不计算诊断 |
| Table S6 | Country; Age and sex standardised CVD mortality per 100000 person years, ICD chapter 9; Year collected | 冻结国家地区分组 |
| Table S7 | Men / Women；各含 Main effect、Age interaction term | 原始 SHR 摘要，非采用的精确 Log SHR 表 |
| Table S8 | Complete population / Excluding UK Biobank / Excluding cohorts that reported only fatal CVD events；各含 Main effect、Age interaction term | 推导敏感性分析 |
| Table S9 | SCORE derivation population / MORGAM-BiomarCaRE；各含 Main effect、Age interaction term | 效应比较 |
| Table S10 | Age-group; Low/moderate region Men/Women; High/very high region Men/Women | 校准乘数，最终方程运行不再重估 |
| Tables S11/S12 | Algorithm SCORE / SCORE2 / Difference；分层性能行 | CPRD 判别比较与 AUROC 敏感性分析 |

Supplementary Figure S11 标题为 Predicted 10-year risks for an example individual from each region；本技能用正文直接印出的对应数值测试，不凭图像像素估计。其余图示包含样本选择、年龄效应、乘数、地区因子/发生率、校准验证与风险分布，均无需要额外提取的个体方程常数。

## 原文内部计数差异

正文用 44 个 ERFC 队列加 UKB（45 个）及 677,684 人；更新附件 Methods 开头写 43 个 ERFC 加 UKB。Table S7 的组标题仍为男性 292,710/16,339 事件、女性 370,957/11,072 事件，与正文总计不同。这里保留并标出这些材料间的差异，主研究描述按正文，不拼接成一套新计数。它们不进入个体预测；计算全部来自同一更新 Methods Table 2–3，复现来自正文和更新 Table 4。
