# 研究与实现核对

研究设计：前瞻性社区队列的模型推导和内部性能评价，男女分别用 Cox 回归；原始研究，不是综述，也不是随机干预试验。PubMed PMID 18212285 的出版类型含 Journal Article，卷期为 Circulation 2008;117(6):743–753。

样本：合计 8491 人，女性 4522、男性 3969，年龄 30–74 岁，入组时无 CVD。来自 Framingham 原始队列第11次检查（1968–1971）和子代队列第1或第3次检查（1971–1975、1984–1987）。表1只给原始队列在女性和男性中的比例（28%、22%），未给两个来源的精确人数，不能用舍入比例反推人数。最长随访12年，首次事件共1174例（女性456、男性718）；内部 bootstrap 评估乐观偏差，没有独立外部验证组，也没有单列病例对照组。分项事件见表3/4：女性 CHD 216、卒中84、CHF 44、IC 66；男性425、93、67、105；这些不是额外队列人数。

物种：人（human；Homo sapiens），没有动物或细胞实验。

利益冲突：正文 p.752 Disclosures：D’Agostino 担任 Sanofi、Pfizer 顾问或顾问委员会成员；Cobain 持有 Milife.com 权益；Kannel 参加 BMS/Sanofi 演讲者项目并获酬金；其余作者报告无冲突。资助包括 NIH/NHLBI，Kannel 的 AstraZeneca 访问科学家项目，Cobain 和 Massaro 的 Unilever Research 支持；Vasan 另有 NHLBI 支持。随附更正 DOI 10.1161/circulationaha.108.190154 补充 NIH 5R01-NS17950，未修改模型参数。

| 论文声称什么 | 补充表里实际有什么 | 公开代码/工作簿实际算什么 | 同名其他方法 |
| --- | --- | --- | --- |
| 表2和内附录给血脂版男女系数、生存率及中心化常数 | 不依赖在线补充表 | 官网 gencardio_lipids.xls 含相同系数、正常/最优参考风险和连续心脏年龄 | 不是1998年 CHD积分，也不是 Pooled Cohort Equations |
| p.747 说明 BMI 替换两项血脂，在线表I给参数 | 原在线文件未打开；表I及IIA–IIC、IIIA–IIIC仅由正文获知，不能声称读过 | 官网公开表和 gencardio_bmi.xls 已读取：完整男女系数、中心化值、生存率、参考 BMI 22.5 | 不是用BMI随意填补总胆固醇/HDL |
| 表5–10给整数积分、风险和心脏年龄查表，表11/12演示 | 全在正文，已核对 | 本技能选连续方程；没有实现整数积分 | 同名“心脏年龄”可能是积分查表、连续反解或其他模型，不能互换 |
| 表3/4给 CHD、卒中、CHF、IC 的校准因子 | 原在线补充不参与此部分 | 本技能只算总体 CVD；不提供单项疾病风险 | 不是单独死亡风险或硬ASCVD风险 |
| 风险因子与首次CVD相关，可用作风险表达 | 没有随机干预疗效估计 | --targets 仅算替换数值的模型差异 | 不能据此预测药物/生活方式干预的因果收益 |

测量定义：两次医生测量的坐位左臂收缩压均值；当前吸烟自报；降压药使用由医生询问并自报。研究的糖尿病标准是子代空腹血糖≥126 mg/dL、原始队列≥140 mg/dL，或使用胰岛素/口服降糖药；实现要求已有诊断状态，未从用户血糖自行下诊断。

适用性：原文承认主要白人人群的可迁移性有待评价，可能需要重新校准。不能把研究中的 C 统计量、内部校准或样本事件率解释为个人测量误差或个人事件概率。

来源：

- [PubMed](https://pubmed.ncbi.nlm.nih.gov/18212285/)
- [完整期刊PDF公开教学副本](https://www.biostat.umn.edu/~greg-g/PH5420/743.full.pdf)
- [Framingham 研究官网](https://www.framinghamheartstudy.org/fhs-for-researchers/fhs-risk-functions/cardiovascular-disease-10-year-risk/)
