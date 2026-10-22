# 输入、公式、复现

## 输入

个人自己的测量：56 项血压、脉搏、BMI、血常规、生化、血脂、铁代谢、叶酸、维生素 B12、C 反应蛋白、纤维蛋白原、糖化血红蛋白、NT-proBNP、可替宁，加尿白蛋白肌酐比；22 项既往病史（是/否）；总体健康自评是否「一般」或「差」、和一年前比是否「更好」或「更差」；过去一年看医生的次数（或 NHANES HUQ050 编码）；年龄和性别。单位按 NHANES 的国际单位，常见的其他单位按 `skill.json` 的换算系数换过来（换算系数由 `lsk check` 对照 `schema/units.json` 和摩尔质量核对）。

## 公式和参数的出处

全部来自论文补充材料（CC BY 4.0），没有一个常数是推导或拟合的：

- 61 个参数的男女中位数、MAD、权重，以及年龄权重 β0（每月：男 −0.0183，女 −0.0075）和常数 C1（男 7.46，女 −1.71）：`linAge_Paras.csv`（MOESM11），即补充表 7 的机读版。
- 模型：deltaBioAge = C1 + β0 × chronAge（月）+ Σ βi × (xi − mediani) / MADi；LinAge = chronAge + deltaBioAge：Methods 和 `linAge_XLS` 说明文件（MOESM7）。
- 没有中位数的参数（可替宁分档、嗜碱性粒细胞绝对值、三个问卷指数）不标准化（中位数 0、MAD 1）；C 反应蛋白和 NT-proBNP 取自然对数；可替宁按 <10、10–<100、100–<200、≥200 ng/mL 记 0–3；LDL = TC − TG/5 − HDL（mmol/L，作者代码原样）；尿白蛋白肌酐比 = 尿白蛋白 /（尿肌酐 × 1.1312×10⁻⁴）mg/g；病史和问卷缺答按「没有」；只算 40–84 岁：`linAge.R`（MOESM12）。
- 并存病指数、自评健康指数、就医使用指数的定义：Methods。HUQ050 的编码（0 次、1 次、2–3、4–9、10–12、13 次及以上记 0–5）来自 NHANES 1999–2000 HUQ 问卷说明。
- 缺项：Methods 写「a zero z-score can be substituted for missing values after normalization … The magnitude of error introduced by this substitution (in years) is of the order of the individual weight」。脚本照做，并报告缺项权重绝对值之和。

## 复现

`tests/test_manifest.py` 用补充材料里同一批人的原始化验值（MOESM8）跑脚本，对照作者印出的结果，误差要求 1e-9 岁：

- 算例表格 `linAge_Example.xls`（MOESM6）的 SEQN 10（男，43.1666 岁）：各项之和 7.389850952344081，年龄差 5.370465592344081，LinAge 48.537065592344085。
- 带 LinAge 结果的数据矩阵（MOESM9）的 SEQN 10（男，43 岁）：年龄差 5.40705095234407，LinAge 48.4070509523441；SEQN 24（女，53 岁）：年龄差 3.91880108714463，LinAge 56.9188010871446。

另外在审核时（不进仓库）把 MOESM8 的原始值、MOESM9 的问卷指数和 MOESM10 的性别代进本脚本的公式，对 MOESM10 能读到性别的 2316 人（男 1170、女 1146）逐一比较，和 MOESM9 的 delAge 最大差 6×10⁻¹⁴ 岁。

## 不做的事

不算 PCAge（要用训练集的奇异向量和 Cox 模型，不是个人能算的线性公式）；不给目标值或「改哪一项能年轻几岁」，因为权重是死亡风险模型的统计贡献，有的方向和常识相反。
