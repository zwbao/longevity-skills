# EDISEA：论文、补充材料、代码和本技能各算什么

- **研究设计**：队列研究。推导：美国健康与退休研究（HRS）2013 年饮食问卷与 2016 年静脉血研究（Venous Blood Study）甲基化的横断面关联（弹性网络回归预测 GrimAge2 加速）；验证与结局：HRS、NHANES、英国老龄化纵向研究（ELSA）、英国生物银行（UK Biobank）前瞻随访死亡和疾病。Crossref 类型为 journal-article，原创研究（Article），不是综述。
- **全部样本组**：HRS 饮食分析 7,398 人，其中有甲基化数据的推导样本 1,711 人（再按 7:3 分训练和内部测试）；NHANES 23,830 人，其中甲基化外部验证 2,311 人；ELSA 4,895 人；UK Biobank 187,035 人（另有其中的蛋白组、代谢组、脑影像子样本）。
- **物种**：人（Homo sapiens）。
- **利益冲突**：论文 Competing interests 写“The authors declare no competing interests.”
- **年份**：Nature Communications 17 卷 11146 号，2026 年（2026 年 9 月 25 日在线）。作者 Lai 等。

| 项目 | 论文声称 | 补充材料实际有什么 | 代码仓库实际算什么 | 本技能 |
|---|---|---|---|---|
| 权重 | 正文印十项三位小数权重，按每 2000 千卡每份解释 | Source Data “Figure 2b”：Food groups / Weight 全精度；Supplementary Data 2 “Primary model” 三位小数，并有交叉验证和惩罚参数稳定性 | hrs-ediea.R 第 1200–1247 行：Estimate = −β_z / sd_fg，写成 Figure_2b.csv | 用 Source Data 全精度 Weight |
| 分数 | “weighted reversed sum of the standardized selected food groups” | Supplementary Figure 3b 的 EDISEA 是中心化 z 版本 | 同时算 `ediea`（z 版本）和 `ediea_servday`（份数版本，第 1259 行） | 份数版本；不给中心化分数 |
| 标准化均值和标准差 | NHANES 用 HRS 的均值标准差标准化 | 没有公布 mu_fg、sd_fg | 代码保存进本地 .RData，没提交 | 不需要 sd（已并进权重）；缺 mu 所以不给百分位 |
| 能量校正 | 残差法；权重按每 2000 千卡每份 | Supplementary Figure 10 是校正后的分布直方图 | 生成校正值的脚本不在仓库（读 `h13_fg_servday.RData`） | 比例法换算到每 2000 千卡（见 contract.md） |
| Q1/Q5 摄入 | 正文印十项 Q5 与 Q1 中位份数 | — | 第 1593–1660 行算出 | 照正文抄录作参照 |
| 结局 | 高 EDISEA 与较慢表观衰老（推导 4.17 年、验证 3.77 年，分位比较）和较低死亡（合并 HR 0.80）相关 | Source Data Figure 3–5、Supplementary Data 5–6 | outcomes/ 脚本 | 不用于个人；报告不写成个人预测 |

同名项目：无。EDISEA 与 AHEI、DASH、MIND 等饮食指数不同，论文在 Figure 2e/2f 中并列比较，本技能不算那些指数。
