# 产品合同与可复现性

用户提供自己的年龄、论文二分类性别、BMI、9项二元病史/吸烟/功能问卷，并确认社区居住；缺项不补零。技能自带从JAMA正文表3、表4抄录的计分与验证队列死亡率，运行时不联网、不要求用户下载HRS。报告允许呈现逐项得分、总分、同分组历史四年死亡率和用户明确提出的目标情境，不估计寿命、因果干预收益或治疗选择。

## 可行性核对（先于代码完成）

- [JAMA全文](https://jamanetwork.com/journals/jama/fullarticle/202375)：读取Methods、Results、Comment、Article Information、References及表1–4。全文页未列Supplement、Appendix、eMethods、发布代码或专属数据包。不是从摘要推断补充材料不存在。
- 表3列为Risk Factor、Adjusted OR (95% CI)、Points。实现仅使用Points，不从OR反推逻辑回归；后者没有完整截距，故不提供连续概率。
- 表4列为Risk Strata、Development Cohort和Validation Cohort各自的No. Who Died/No. at Risk (%)。实现只用Point score部分的Validation Cohort整数百分比；不用Quartile of risk部分，也不把计数自行计算成更精确的百分比。
- [Box原图公开副本](https://abcnews.com/images/GMA/Test_Quiz.pdf)：下载到临时目录并渲染逐项核对问句。其糖尿病错误计2分，使用下述正式勘误修正。出版社Box及表图CDN拒绝获取；表格仍可在出版社HTML全文完整读取，Box在该JAMA原图副本完成视觉核对。
- [JAMA正式勘误](https://jamanetwork.com/journals/jama/fullarticle/202729)，DOI 10.1001/jama.295.16.1900：明确Box糖尿病应为1分，与表3一致。无其他权重改动。
- Europe PMC PMID 16478903的core记录核对文章类型和Erratum in；[ePrognosis作者机构页面](https://eprognosis.ucsf.edu/lee.php)核对问句与方法名称，不使用其计算器输出拟合常数、不引入后续10年版本。
- 本机未配置图书馆缓存。DOI直接获取失败后取得JAMA HTML全文；出版社PDF及SciSpace PDF无法取得，Jina返回验证码，浏览器连接超时。没有把这些失败的页面当作全文，未复制任何全文或PDF进仓库。
- 文中HRS链接为队列设计、采样与受限死亡数据背景引用，没有发布本文训练代码或必需的计算资产。个体查表不需重训或下载队列。

## 常数定位

| 计算项 | 发表位置 | 实现 |
|---|---|---|
| 50–59岁参考档 | Methods / Measures | 0分 |
| 60–64、65–69、70–74、75–79、80–84、≥85岁 | 表3年龄行 | 1、2、3、4、5、7分 |
| 男性、BMI<25 | 表3 | 2、1分 |
| 糖尿病、癌症、肺病、心衰、当前吸烟 | 表3，糖尿病另经勘误确认 | 1、2、2、2、2分 |
| 洗澡、钱财、步行、推拉困难 | 表3 | 2、2、2、1分 |
| 总分0至13、≥14 | 表4验证队列 | 1、2、2、4、6、8、9、15、20、20、28、45、44、59、64% |

所有计算常数位于 `scripts/presets.py`，没有拟合、插值、反推或使用记忆中的常数。年龄85岁按表3的≥85计7分，不按摘要的>85；BMI严格小于25，不对原始BMI四舍五入。功能问句依据Box；方法正文的宽泛肺病/非皮肤癌措辞以实际问卷的限定为执行口径。

## 验证与矛盾

先写 `tests/test_manifest.py`，后写实现。`test_table3_age_points`、`test_table3_terms_and_correction`复现逐项分数；`test_table4_validation_rates`复现全部逐分风险行，整数完全相同，无容差。端到端正常例使用年龄60对应1分、表4总分1对应2%，是两个已打印表值的组合检查，未声称为完整已打印病例。

正文Risk Stratification by Points的示例输入是78岁、不吸烟、女性、BMI 28、糖尿病、管理财务困难，原文写年龄3分、总分6分。按表3年龄应计4分，故合计7分；这不是舍入误差，不能在2%内匹配。已读全文、表3、Box及正式勘误，勘误只修正糖尿病。没有印出的中间值可支持替换年龄权重，故不推导“更精确常数”。

`test_printed_78_year_example_unresolved`仍以印出的6为期望值，标记strict xfail。它证明尚未完成复现；若以后错误地把年龄权重改成3，该测试会unexpected pass并使检查失败。虽然逐项与查表均复现，按流水线关于不一致示例的保守规则，`validation.status=draft`；`inputs_status=verified`只表示输入契约及上述逐项示例已验证，不能读成完整病例已复现。

正文Comment另有75岁男性吸烟且心衰、洗澡/步行/财务困难的16分示例，但未明确BMI等其他输入；不默填这些未知项并冒充完整病例复现。正文和摘要给出的0–5分合并风险与逐分行不同，故只用表4逐分行；摘要<4%与正文4%的差别不混入计算。表4的11分45%、12分44%保持不变。

## 操作约定

软件合理范围为年龄50–120整数岁、BMI 10–80 kg/m²、二元项0/1；上界是数据质量检查，不是研究纳入范围的宣称。研究没有提供足以声明完整最大年龄的资料，因此没有虚构population.age_years上限。BMI单位kg/m2与kg/m^2因子1，years与a因子1；不接收体重替代BMI。未使用不确定的LOINC。

额外community_dwelling只检查适用性、不计分；机构居住直接退出3。目标可含BMI、吸烟或四项功能，不可含诊断史、年龄、性别、居住场景；目标同样经skillkit校验，错误目标不会静默丢弃。离散敏感度中BMI对照25或24.9（表2的一位小数边界），是模型探查值，不是推荐目标；其他二元项翻转，年龄移至下一个已印出的分档。输出所有单项和联合变化，并明确不是因果收益。运行前清除本技能旧结果，输入失败不会留下旧数值。
