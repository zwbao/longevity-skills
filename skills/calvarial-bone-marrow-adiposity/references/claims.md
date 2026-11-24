# 证据和公开材料核查

研究设计：原创影像测量方法研究，使用已有的人群队列横断面影像、重复扫描、双生子及 GWAS，附小鼠单细胞数据再分析；不是随机干预试验。正式发表版为 Kaufmann 等，eLife，2026，13:RP101499，doi:10.7554/elife.101499（版本 DOI .3）。期刊及 PMC 的正式版日期为 2026-11-04；下载 PDF 页脚仍写 2024，属于来源间日期不一致，本技能依正式版页面推荐引文使用 2026。

样本组（按各分析分别列出，不能相加当独立验证人数）：

- HNU/CoRR：30 名健康成年人，男女各半，20–30 岁，均龄 24.4（SD 2.4）；各扫描 10 次，共 300 次。图1d 中 13 次扫描未过质控，其中 11 次位点不足。
- HCP：430 名双生子个体。男性 174 名（114 MZ、60 DZ），22–34 岁；女性 256 名（160 MZ、96 DZ），26–36 岁。原表写 twins，不误写成这些数量的双生子对。
- UKB：开始分析 42,068 个头部扫描，420 无输出，2,234 少于 5,000 位点，剩 39,414；附加定位质控后 39,207。
- GWAS 发现组：33,042 名白人英国人，男性 16,140、女性 16,902（曾用 HRT 6,373、未用 10,529）；附表3年龄范围 45.13–82.06，均值 64.33、SD 7.51。Methods 的 mean 64.9 与表中 mean 不一致，64.94 实为表中中位数，不能混用。
- 跨族群复制组：4,958 名，男性 2,338、女性 2,620（曾用 HRT 874、未用 1,746）；年龄 44.57–81.07，均值 62.89、SD 7.706。
- 骨密度关联：14,262 名男性及 14,831 名女性，共 29,093 名同时有头部 DXA 和 MRI 的人。
- 附录图12病例对照：220 名骨质疏松者（ICD-10 M80–82）对 30,127 名无 M 类诊断的对照；属于 UKB 子样本。
- MICA-MICs：与定量 MP2RAGE T1 图比较，附录图10给出年龄 29.54±5.62；本文对应段落及图注未明确写该比较最终样本量，不从 P 值反推人数。
- 小鼠单细胞再分析：Zhong 等 SCP1017，7,585 个细胞，来自 1 月龄和 1.5 月龄雄性 Col2:Td 小鼠的 endosteal Td+ BM 细胞；不把细胞数写成动物数。

物种：人（human/Homo sapiens）和小鼠（mouse/Mus musculus）。小鼠属于已有数据再分析；仅在引文中提到的长颈鹿等不加入本研究物种。

利益冲突：作者声明 OAA 为 HealthLytix 顾问，收取 Lundbeck 和 Synovion 演讲酬金；SD 收取 Lundbeck 演讲酬金；其他作者声明无竞争利益。没有据此推导个人治疗建议。

| 论文声称什么 | 补充材料实际有什么 | 作者代码实际算什么 | 同名/相近方法区别 |
|---|---|---|---|
| 用 T1 信号作为颅骨 BMA 代理 | 附录图9归一化比较、图10定量T1相关、图11 DXA相关、图12病例对照 | 模型预测六个边界，R 脚本求层内和位点间均值 | 不是 Dixon/PDFF 或 MRS 脂肪分数，不能套用脂肪百分比阈值 |
| 男女年龄轨迹不同且与 HRT 有关联 | 图2为广义加性拟合曲线，表2为 BMD OLS 系数 | 本仓库主要实现定位及汇总，不提供个人年龄百分位曲线参数 | 不是衰老时钟，也不是 HRT 随机试验；不把关联作为用药效果 |
| 41 个联合发现位点、若干性别特异结果 | 表5各SNP效应与误差，表6复制比较；表7–8人鼠基因对应 | release v1.2 附联合 GWAS 汇总统计，FUMA提供群体结果 | SNP效应表不是经验证的个人遗传风险预测器 |
| 与脑/身体性状的遗传相关和重叠 | 表1及附表9 LDSR/MiXeR 群体参数 | LDSC、MiXeR 为群体分析工具，未纳入个人入口 | 不把群体遗传相关换算成个人帕金森病或认知风险 |
| 论文图示50输入、三层各100节点 | 正文和图1、附录训练图 | 发布模型实际150输入，隐藏层300/100/100；推断脚本补100个零 | 使用真实公开模型，不假装另一个结构的权重已提供 |

## 每张表的用途和列

全文和附录来自 [正式文章页](https://elifesciences.org/articles/101499)、[Figures and data](https://elifesciences.org/articles/101499/figures)、[PMC全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC13734677/) 及 Europe PMC 同文 XML；附录内嵌，不是遗漏的独立 xlsx。

| 表 | 已核对列 | 对个人推断的作用 |
|---|---|---|
| Table 1 | Trait；rg/p/Q；Unique to BMA/Overlap/Unique to trait；overlap fraction；effect correlation/SE；AIC best vs min/max | 群体关联，不是神经网络参数 |
| Appendix table 1 | NACE；A/C/E；男性/女性 twin 分类 | 双生子遗传率，不用作个人输出 |
| Appendix table 2 | BMD explanatory variables；男女各模型 Coeff./p-value；Intercept、BMA、Age、Scanner_1/_2、EverHRT、R-squared、N | BMD群体回归，不提供年龄参考曲线；本技能不计算BMD |
| Appendix table 3 | 年龄 Min/1st Q/Median/Mean/3rd Q/Max/SD；Sex；Scanner | 研究人群说明 |
| Appendix table 4 | Total observed scale h2、Lambda GC、Mean chi2、Intercept、Ratio；Statistic/Error | 群体GWAS质控 |
| Appendix table 5 | Locus ID、SNP、CHR、BP、A1、A2、Nearest gene；各样本 BETA/SE/p-value | 41位点统计，无MRI输入输出算例 |
| Appendix table 6 | 男、女、复制组在 p<5e−8 和 p<5e−2 下比例 | 复制分析 |
| Appendix table 7 | Human gene、Mouse gene、Closest | 找到表达的42个人鼠基因对应 |
| Appendix table 8 | Human gene、Mouse gene、Closest、Reason for failure | 12个未找到可靠表达的对应及原因 |
| Appendix table 9 | Trait；各性别rg/p；全样本rg/p/Q；causal partitions/SE；overlap fraction；effect correlation/SE；AIC | LDSR/MiXeR结果，不是个人预测 |

另有且仅有一个独立附加文件：[MDAR checklist](https://cdn.elifesciences.org/articles/101499/elife-101499-mdarchecklist1-v1.docx)，已下载解压阅读；它指回正文伦理、数据、代码和质控章节，不包含隐藏系数或权重表。期刊页面列19图、10表、1附加文件；全文 XML 中还有作者回复图。没有把无法访问的材料当作空内容。

## 代码、数据入口与访问状态

- 已克隆作者 GitHub 全仓库，读取 README.md、000_README.pdf、000_README.docx、模拟 R、训练 ipynb、提取 shell/Matlab、推断 Python、汇总 R；读取并加载 saved_model.pb 及 variables 两文件。模型来源和哈希见合同/manifest。
- 已打开 GitHub Releases v1.2 并下载/解压检查完整公开 GWAS gzip（216,255,951 字节压缩文件）：列为 `SNP CHR BP PVAL A1 A2 N BETA SE Z`。数据只在临时审计目录，不随技能发布；无需把数百MB群体统计当个人输入。
- 已访问 FUMA 153909、153916、153914；公共页面有动态加载，web读取 153916/153914 失败，153909 返回通用界面而未取得具体结果表。没有声称核对其动态结果；附表及GitHub GWAS已可读取，且此处不需要额外个体推断权重。
- 已打开 HNU/CoRR DOI 10.15387/fcp_indi.corr.hnu1（可读研究说明）、MICA-MICs CONP数据页（可读）、UK Biobank官网/访问申请入口（受申请约束）；HCP db.humanconnectome.org 请求超时。未下载这些原始影像或声称获得受控数据。
- 已打开 SCP1017 单细胞入口（显示7585 cells），未下载完整计数矩阵；这部分只解释遗传机制，不参与MRI推断。
- 已访问论文列出的 python_convert、MiXeR、LDSC GitHub 页面，均用于群体遗传分析，不为个体MRI网络提供额外参数。Software Heritage 归档链接读取失败，但 GitHub 中的发布源码和权重可取得。
- 浏览器 CDP 前置检查连接超时，因此使用公开页面读取、curl 和 Europe PMC XML。未操作登录会话。

## 示例查找和边界

逐项检查附录图1–14的文字和表格，另视觉检查 Figure 1、附录图4与图10（带个人示例的图）。这些图未提供完整强度数组及对应个人数值输出；图上散点、颜色和全队列相关系数不能替代输入。完整个人示例缺失意味着 draft，而不是模型权重缺失。

研究只建立了信号代理的生物学相关性。绝对信号受扫描仪和预处理影响；不把较低数值称为更健康，不按性别/年龄补造临床阈值。资料中的群体误差和遗传率不写作个人可靠度或个人风险。
