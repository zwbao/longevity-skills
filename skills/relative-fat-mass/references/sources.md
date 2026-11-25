# 材料核查清单

核查日期：2026-11-25。机器没有用户所述图书馆缓存目录。全文与补充材料从出版社公开地址读取，仅临时存入 /tmp；未将全文、PDF 或数据文件复制进仓库。

- [出版社全文](https://www.nature.com/articles/s41598-018-29362-1)：完整 Results、Methods、Discussion、图注、参考文献和利益冲突已读。自动网页工具遇到 Nature 身份跳转；公开 HTML 直接下载成功。
- [主表 1](https://www.nature.com/articles/s41598-018-29362-1/tables/1)：列为推导/验证、Women/Men、P value；行含年龄、族群、人体测量、DXA 组成，均为群体统计。
- [主表 2](https://www.nature.com/articles/s41598-018-29362-1/tables/2)：列 All/Mexican-American/European-American/African-American；男女分组，行 Bias、Accuracy、Precision 及 95% CI。
- [主表 3](https://www.nature.com/articles/s41598-018-29362-1/tables/3)：DXA-Negative、DXA-Positive、Total 与 BMI/RFM 分类交叉计数。
- 主图 1–3：分别是样本筛选、RFM/BMI 与 DXA 的散点及统计注释、误分类率；不是个人输入—输出示例。
- [唯一补充文件 41598_2018_29362_MOESM1_ESM.pdf](https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-018-29362-1/MediaObjects/41598_2018_29362_MOESM1_ESM.pdf)：已下载并打开，封面及印刷页 1–45；方法、10 幅图与 16 张表均在此文件，图页另外渲染检查。页面未列其他补充数据文件、GitHub、Zenodo、OSF 或作者发布的程序。
- [Europe PMC 元数据](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41598-018-29362-1&format=json)：PMID 30030479、PMCID PMC6054651、期刊/年份/作者及原创研究类型核对。
- [NHANES 2005–2006 公开数据入口](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2005)：已打开数据与文档入口。论文分析的是公开 NHANES；最终方程不需要训练数据。没有下载全体原始 XPT，也没有重跑多重插补或抽样加权验证。
- 参考文献 39 的 `http://wwwn.cdc.gov/nchs/data/nhanes/dxa/dxa_techdoc.pdf` 与参考文献 40 的 `http://www.cdc.gov/nchs/data/nhanes/nhanes_07_08/manual_an.pdf`：尝试 HTTPS 地址，返回 HTML 而非 PDF，未能读取这两个外部历史手册。它们不是缺失系数来源：所需公式、编码、腰围测量方法、样本排除条件均已在全文和已读补充 PDF 中明确印出。

## 补充表与列名

| 表（印刷页） | 已核对的列与内容 | 个人计算作用 |
|---|---|---|
| S1（14） | Women/Men；Non-imputed data (%)、Imputed data (%)、Total；Ethnicity、Age、BMI | 推导样本及插补比例，无个人预测 |
| S2（15） | 同 S1，验证样本 | 无个人预测 |
| S3（16） | BFP、BMI、WAIST、ARMC、BW、TRI、THIGH、SUB、CALF、ARML、Height；男女相关矩阵 | 人群相关性 |
| S4（17–28） | Women/Men 下各 Anthropometric index、r、P value | 候选指标排序，不是权重表 |
| S5（29–30） | All、Mexican-American、European-American、African-American；R² (95% CI)、RMSE (95% CI)；脚注最终公式 | 最终系数与单位的交叉核对 |
| S6（31） | 20–39、40–59、≥60；R²/RMSE (95% CI) | 人群统计 |
| S7（32） | 每个指数的 Equation for women、Equation for men、Equation for women and men | 原始回归系数；不用于最终 RFM |
| S8（33） | All 与三个族群；男女的 rho_c | 一致性统计 |
| S9（34–35） | All 与三个族群；Bias、Accuracy、Precision (95% CI) | 推导样本性能 |
| S10（36–37） | All 与三个族群；R²/RMSE (95% CI) | 验证样本性能 |
| S11（38–39） | 同 S10，合并样本 | 内部验证统计 |
| S12（40） | 三个年龄组；R²/RMSE (95% CI) | 年龄分层统计 |
| S13（41） | All 与三个族群；Bias、Accuracy、Precision (95% CI) | 合并样本性能 |
| S14（42） | 三个年龄组；Bias、Accuracy、Precision (95% CI) | 年龄分层性能 |
| S15（43） | Whole-body fat percentage、Whole-body fat mass、Trunk fat percentage；R²/RMSE | 其他身体组成拟合比较，未实现其他输出 |
| S16（44） | ROC-AUC、P value (compared with BMI)；女性/男性各模型 | 人群诊断性能，非个人阈值 |

补充图 1–10 已检查：散点、年龄趋势、Bland–Altman、族群/年龄/体脂分层性能、ROC；没有同时标注个人身高和腰围及 RFM 的计算例。S7 为原始公式，最终式应以正文 (1–3) 和 S5 脚注为准。
