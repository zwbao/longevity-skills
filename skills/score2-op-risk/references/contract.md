# 产品合同与来源

1. 用户提供年龄、模型分层性别、居住国家、既往冠心病/卒中/外周动脉病情况，以及当前吸烟、糖尿病史、收缩压、总胆固醇和 HDL 胆固醇；可另给目标值。
2. 技能内置发表版补充材料印出的十年方程参数和国家分组，不要求用户下载原始队列、论文或附件；运行时不联网。
3. 报告仅给出十年主结局的暂定风险及目标输入变化后的模型比较；地区校准算例未复现，因此 validation=draft，不提供五年连续风险、含心衰的次要结局、治疗效应、用药方案或个人寿命。

本次是已授权的 LONGPI_PIPELINE 任务。数据类型为常规血脂、血压与个人病史。

## 可行性与材料清单（写代码前完成）

- DOI/文章页：<https://academic.oup.com/eurheartj/article/42/25/2455/6297711>。普通页面遇到 Cloudflare，页面工具重定向至期刊公开内容页 <https://oup.silverchair-cdn.com/article-minimal/6297711>；后者成功返回文章及补充包实际下载链接。
- 发表全文：<https://pmc.ncbi.nlm.nih.gov/articles/PMC8248997/>，已读摘要、Methods、Results、Tables 1–2、Discussion、利益冲突、Data availability 和附录。
- 期刊补充包只有一个文件：`ehab312-suppl_data/Supplementary material_20210604_v2.docx`。已解压并读取全部文字、表格及图的说明，Methods Table 3 内四位系数直接可读。期刊实际资源路径：<https://oup.silverchair-cdn.com/oup/backfile/Content_public/Journal/eurheartj/42/25/10.1093_eurheartj_ehab312/3/ehab312_supplementary_data.zip>（下载使用期刊页面提供的完整签名链接）。PMC 镜像链接在 skill.json 中，当前该下载入口触发验证页。
- ZIP SHA-256：`3d83763887832894a6d0b63427f156ee746b9c81a613febface65b32e4ac8481`；DOCX SHA-256：`82e08e8cdb99521ec44c8c25df03731a59a8b580915167603592465228e470ba`。
- 也读过 Cambridge 接收稿和附件：<https://www.repository.cam.ac.uk/handle/1810/329740>；附件 <https://www.repository.cam.ac.uk/bitstreams/9b6ae3ce-c7a3-4cdc-90e2-4222adf48505/download>。其图编号较旧，没有发表版新增的五年图；本实现参数依据发表版，不将接收稿图号混用。
- Europe PMC fullTextXML 返回服务器错误，supplementaryFiles 未返回 ZIP；OpenAlex 元数据用于找到机构副本；Utrecht 存档明确无全文。所有下载材料只留在 `/tmp`，未把整篇论文或附件复制入仓库。
- 文章和附件没有链接 GitHub、Zenodo、OSF 或其他发布模型代码/权重仓库。Data availability 要求向各队列申请个体数据；不冒充已下载或复算队列训练。正文提及的统计软件 R 不是模型代码发布。

## 表格清点与采用范围

| 原文位置 | 实际列名/内容 | 本实现用途 |
|---|---|---|
| Main Table 1 | CONOR、ARIC、CPRD、HYVET、MESA、PROSPER、SPRINT 的基线特征、事件和死亡 | 样本溯源；不作为个人结果 |
| Main Table 2 | Men/Women；Coefficients (95% CI)；Subdistribution hazard ratios | 核对系数方向及中心化；SBP 此表为每 10 mmHg |
| Supplementary Methods Table 1，p.12 | Men/Female，Scale 1、Scale 2；四个地区 | 全部地区变换常数 |
| Supplementary Methods Table 2，p.13 | 逐步 LP、original risk、recalibrated risk；另有含 HF 公式 | 十年主结局公式及中心化值 |
| Supplementary Methods Table 3，p.14 | Individual risk factor levels；Model coefficients (women/men)；Calculation of 10-year CVD event risk | 四位系数、较精确 S10/meanLP、算例；不采用与 Table 1 矛盾的算例校准常数 |
| Supplementary Table 1 | Endpoints included、ICD10-codes | 确定复合结局 |
| Supplementary Table 2 | Countries、Age- and sex-standardized CVD mortality rates (per 100,000 persons)、Year collected | 冻结国家到地区的分组 |
| Supplementary Table 3 | Age group；Low/moderate / High/very high；Men/Women | 死亡到事件转换，用于模型开发；个人计算不需要重新校准 |
| Supplementary Table 4 | Age group 65/70/75/80/85+；Men/Women | 含 HF 的乘数；本实现不输出次要结局 |
| Supplementary Table 5 | Agegroup、Region、Sex、SBP、Smoking、TC、HDL、Diabetes、Expected 10-year cumulative incidence | 地区训练/校准均值；不能当成某个人的验证值 |
| Supplementary Table 6 | ASCVD、SCORE2-OP；各验证队列 C-statistic (95% CI) | 群体验证比较 |
| Supplementary Table 7 | Harrell’s C-statistic、1-year time-dependent ROC、Time-dependent ROC | 群体验证比较 |
| Supplementary Methods Figures 1–2 | 模型开发与校准流程 | 方法背景；Figure 2 示意常数与 Tables 2–3 不一致，未取用 |
| Supplementary Figures S1–S7 | 地区图、年龄交互、内外部校准、死亡和事件率、风险分布 | 背景；不从曲线拟合常数 |
| Supplementary Figures S8–S10 | 五年风险分档图；给定 non-HDL/SBP 的地区风险曲线；十年不确定性分档图 | 五年图不是连续方程的基线生存率；没有把分档图外推为方程 |

## 参数和方程

`scripts/presets.py` 是唯一运行时参数表。系数顺序为 age、diabetes、smoker、SBP、TC、HDL，然后五个 age 交互项；按 Methods Table 3 四位值逐项抄录，SBP 使用每 mmHg 系数，不再除以 10。

中心化：年龄减 73，SBP 减 150，TC 减 6，HDL 减 1.4；是否项不中心化。先算 LP，再算：

`p_original = 1 - S10 ** exp(LP - meanLP)`

`p_region = 1 - exp(-exp(scale1 + scale2 * log(-log(1-p_original))))`

S10 男 0.7576、女 0.8082，meanLP 男 0.0929、女 0.229，均直接印于 Methods Table 3。Methods Table 2 中相同数仅印到三位。使用更精确的已印值不是反推。运行时用 log-hazard 的等价形式提高数值稳定性。

所有十年主结局计算所需常数均已印出。五年连续方程不在本产品范围：发表版只新增 S8 的分档图，未见性别分层五年基线生存率，不能从十年风险开平方或减半构造。含 HF 的公式不是本产品范围：表中减去 log(multiplier) 的写法还会令较广结局的风险降低，故没有擅自修正后输出。

## 先写的论文复现测试与未解决缺口

Methods Table 3 两例输入完全相同，性别不同：75 岁，TC 5.5 mmol/L，HDL 1.3 mmol/L，SBP 140 mmHg，无糖尿病，当前吸烟。

| 输出 | 原文印出 | 按印出参数复算 | 结论 |
|---|---:|---:|---|
| 女，未校准风险 % | 24.4 | 24.424117 | 一位小数吻合 |
| 男，未校准风险 % | 29.7 | 29.658848 | 一位小数吻合 |
| 女，低地区风险 % | 14 | 15.158016 | 不吻合 |
| 男，低地区风险 % | 19.3 | 18.562104 | 不吻合 |

复算结果仅用于记录误差，不写作测试的期望值。测试期望值始终为原文的 24.4、29.7、14、19.3；容差为 0.05 个百分点（该算例同时印有四位概率，不能为通过测试而扩宽到整百分点）。原文算例还把 LP 求和写成负号，但其下一步带入的是正的 0.5029/0.3298；逐项求和也是正值。

Methods Table 3 女低地区使用 (-0.85, 0.82)，男低地区使用 (-0.61, 0.89)；Methods Table 1 则分别为 (-0.52, 1.01)、(-0.34, 1.19)。本实现选择明确列出的全地区参数表，不能通过偷偷替换低地区常数来宣称验证通过。Methods Figure 2 还有 0.7669/0.1111 的示意常数，与正式 Tables 2–3 不同，亦未混入。

正文的 75 岁、SBP 150、non-HDL 4.5 示例印出男 16%/37%、女 14%/44%；没有给出 TC 和 HDL 的分别数值，而两者系数不同，不能擅设 HDL 后拿它作独立验证。

测试先于公式实现建立。`test_printed_original_risks` 通过；两个地区输出测试明确为 `unittest.expectedFailure`，用于保留待解决的不一致，**不是两个成功的验证**。因此即使中间步骤已吻合，skill.json 的 validation 仍为 draft。没有推导、拟合或从第三方工具取任何模型常数。

## 输入和输出约定

- 单位：SBP 为 mmHg，kPa 乘 7.500617；TC/HDL 为 mmol/L，胆固醇分子量 386.65 g/mol，mg/dL 乘 10/386.65，mg/L 乘 1/386.65，umol/L 乘 0.001。换算因子只是量纲换算，不是风险参数。使用 skillkit 按 manifest 解析，不另写实验室别名映射；没有写入未经查证的 LOINC。
- 合理范围仅用于录入防错：年龄 70–89 岁，SBP 70–250 mmHg，TC 1–15、HDL 0.2–5 mmol/L。年龄上限是本实现范围，不能标成论文推导队列上限。原文只写推导纳入 65 岁及以上、目标人群 70 岁及以上，故不伪造 population.age_years。
- 吸烟与糖尿病严格 0/1。HDL 必须小于 TC。不填非 HDL 默认值。疾病史及国家不合适、缺项、NaN/Inf、单位错误、目标文件错误均退出 3，写 problems.json，result 中值为 null，并清除先前输出。
- 目标可以调整 SBP、TC、HDL、smoker；糖尿病史不能通过目标“消除”。每个单独目标及全部目标场景均检查 HDL < TC。连续输入敏感度是当前点对风险百分数的偏导，吸烟为 0→1 的离散差值；风险差单位为百分点。
- levers 不建议任何目标、不给治疗 HR、不给剂量；数据是关联型方程的替换值重算。
- 国家沿用 Supplementary Table 2 英文名称和原地区。完整名单在 `presets.py::COUNTRIES`。支持英国、美国、法国、德国、挪威、荷兰等常见名称别名；中国或未列国家退出 3。历史国家命名保留原表，不推定今日重划地区的归属。
