# 产品合同与可复现范围

1. 用户提供按全部日历日平均的每日纯乙醇摄入量（g/d）、年龄、论文分层性别、GBD 地区及参考年份；可另提供一个自填摄入量情景。
2. 技能自行提供更正版附录 2 表 S1 的全部分层阈值和不确定区间，离线运行不需要用户下载论文或提供队列。
3. 报告只输出历史人群阈值、输入对应的表格行、摄入量减阈值及所在侧；不估算个人概率、相对风险、因果获益、寿命，也不给安全量或推荐目标。

本次为 LONGPI_PIPELINE 授权的自动构建，按用户的流水线规则直接实现上述范围。

## 可行性核查（实施前完成）

已从 [PMC 正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC9289789/) 读取方法、结果、讨论、数据共享和利益冲突声明，检查页面列出的全部两份补充材料：[附录 1](https://ars.els-cdn.com/content/image/1-s2.0-S0140673622008479-mmc1.pdf) 和 [附录 2](https://ars.els-cdn.com/content/image/1-s2.0-S0140673622008479-mmc2.pdf)。两份封面均标明 2022 年 7 月 19 日更正。Lancet 正文入口受阻、PMC 附件入口返回 HTML 后，由 Elsevier CDN 成功取得 PDF；机器没有用户所述图书馆缓存。所有原始下载留在仓库外，不随技能分发。

附录 1 pp 3–12 有 Location、Super-Region、Region 地理映射；pp 14–17 有研究纳入规则、样条/偏倚协变量、TMREL 与 NDE 定义及敏感性分析；后续为检索式、研究列表、PRISMA 图、风险曲线、GATHER 清单和贡献者。附录 2 表 S1（附录 pp 3–31，PDF pp 4–32）列为 Region、Age Group、Year、Female TMREL、Female NDE、Male TMREL、Male NDE，每格含均值及区间。图 S1 为超阈值人群比例，图 S2–S5 为敏感性分析，表 S2 为不同 GBD 风险曲线的 TMREL 对照，表 S3 为超阈值人群年龄/性别构成；均不是额外的个人系数表。

附录 1 GATHER 清单链接的 [GBD 2019 code/risk-1](https://ghdx.healthdata.org/gbd-2019/code/risk-1) 已打开，现跳转 IHME Data access 说明，不提供该分析的可克隆仓库；[GBD 2019 data-input-sources](https://ghdx.healthdata.org/gbd-2019/data-input-sources) 为来源检索工具。正文 Data sharing 指定本次分析数据需联系 Emmanuela Gakidou。正文与两份附录未发现专属 GitHub/Zenodo/OSF 发布链接。这里没有声称重建作者的 22 个结局风险曲线，因而不需要其样条系数、后验抽样或 DALY 权重；本任务所需的全部阈值已直接印在表 S1，标准杯换算在正文图 1/3 图注。

## 数据与算法

- 表 S1 含 21 地区 × 14 年龄档 × 4 年份 × 男女两列，提取为 2352 条记录。保留原始数值字符串精度，不插值、不拟合、不重估、不用摘要范围填补。
- 年龄档为 15 to 19 至 75 to 79，及 80 plus。连续年龄按下界分档（例如 54.9 属 50 to 54），这是周岁分档的实现约定。120 岁上限仅作录入合理性检查，不表示论文年龄最大值。
- `standard_drinks_day = ethanol_g_day / 10`，10 来自正文图 1 和图 3：“One standard drink is equivalent to 10 g of pure ethanol.”
- 差值 = 输入 g/d − 原表标准杯/日均值 × 10。分别比较 TMREL 与 NDE，严格高于 NDE 才对应原文超均值定义；不是将两个条件合并。浮点相等判断容差 1e-12 标准杯仅防止计算舍入误差，不是临床容差。
- 0–100 g/d 为正文 Methods 中风险曲线的建模暴露范围。本工具对超出此范围的输入退出 3，不截断。只接受 g/d（因子 1），不自动解释 g/week、饮料 mL、ABV 或不同国家的标准杯；标准杯转换仅作为定义明确的输出。
- 原表有非零均值配 `(0–0)` 的格子，照录并提示。区间是 posterior 95% UI，不校正成包含均值的区间，也不计算个人“显著超标”。
- 不将参考年改成当前年份。默认 2020，亦可明确选择另三个原表年份。
- `--targets` 不自动优化或建议摄入量；只改变用户给出的摄入量，保持分层不变。`levers.json` 的敏感度为差值对摄入量的代数斜率 1（g/d 每 g/d），不含任何风险变化或治疗效果。

## 验证证据

先写 `tests/test_manifest.py` 的打印值测试，再提取表格和写运行脚本。用本地 PDF 图像核对列顺序及两组验证行：Central Asia、15 to 19、1990（附录 p 3），以及 East Asia、50 to 54、2020（附录 p 23）。原表逐字数值在 `skill.json.validation` 和测试中。测试通过查表函数复现两性的均值和区间；后一组还通过完整 CLI 运行验证 result.json。预测输入是表格分层条件，演示摄入量不是论文受试者数据。无需从中间值推导常数。

`reproduced` 只说明复现了表 S1 的已发表分层预测值与选择逻辑，不说明从队列重跑得到原论文模型。原始病例级模型再估计不在合同范围。

另验证缺项、非数、单位错误、范围错误、不存在的文件、无效地区/性别/年份、年龄档边界、情景输入，以及复用输出目录时清除旧结果。用完整索引集合审计提取是否覆盖每一个表格组合，并保留每条记录的附录页码和 PDF 页码。

## 来源完整性

数据是署名提取的公开数字事实；文章为 CC BY 4.0，署名 GBD 2020 Alcohol Collaborators，Lancet 2022，DOI 10.1016/s0140-6736(22)00847-9。CSV 是提取、重排及小数中点规范化后的衍生数据，不是 PDF 复制件。

- 附录 1 PDF SHA256：`a951c183ca85d812fbdcdc475291adc41f6b167342e37940d152606c8b0ed102`
- 附录 2 PDF SHA256：`8e32f73f378a644bcd1ff656e2342c4e5cd21bd5fc9bea487980a3662c5a532e`
- table_s1.csv SHA256：`76e76c41fd2056e87553b8d493bbdd66586b8a7f227e6d86f4fc178178123014`

维护者可下载原附录到仓库外，然后运行 `python3 scripts/extract_table.py /tmp/mmc2.pdf /tmp/table_s1.csv` 并比较散列。提取器只依赖外部 `pdftotext`，个人报告使用 Python 标准库与仓库生成的 skillkit/paper_card。
