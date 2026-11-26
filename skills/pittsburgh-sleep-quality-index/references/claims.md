# 证据核对

研究设计：原创量表开发和人体临床测量学验证（method），含横断面组间比较及部分受试者重测；非综述、非随机干预试验。PubMed PMID 2748771 用于书目信息；其页面正文/出版类型区及 Europe PMC 页面受访问限制，未据此臆断具体索引标签。全文 Methods、Results 明确报告原创方法和数据。

全部样本：p.197 原池158人，10人未完整回答而排除（其中9人为过度嗜睡患者）；p.195–196 实际分析148人：健康对照52人、抑郁患者34人（门诊24、住院10）、睡眠门诊62人（入睡/维持睡眠障碍45、过度嗜睡17）。重测子集91人：对照43、抑郁22、睡眠障碍26；不是独立验证队列。摘要印成抑郁54人，与正文、Tables 1–3、Fig.2不一致；本技能按正文34人记录并保留这个差异。组别观察年龄：对照24–83、抑郁21–80、入睡/维持障碍20–80、过度嗜睡19–57岁。

物种：人（human；Homo sapiens），没有动物或细胞实验。

利益冲突：已读原文，未见独立 Competing interests/Disclosures 声明，不能写成声明无冲突。p.207 致谢列美国 NIMH 研究资助。作者任职匹兹堡大学精神科；现行大学网站声明问卷版权及使用条件，未据此推定作者个人专利或商业利益。

| 论文声称什么 | 附录/官方材料实际有什么 | 发布代码实际算什么 | 同名或后续项目是什么 |
|---|---|---|---|
| 月度自评形成七个分量和总分 | 文内pp.211–213印出映射、效率公式和等权相加规则 | 原文未点名代码、数据仓库；本实现独立转录计分常数 | 不是其他研究中改题号、改窗口、删项目后的版本 |
| 总分大于5区分研究中的两侧睡眠人群 | p.199和Fig.2给出事后切点及敏感度89.6%、特异度86.5% | 未取得原始个人数据，未重建这些诊断性能指标 | 不是个人疾病概率、失眠诊断或寿命风险模型 |
| 分量睡眠时长及效率按表计分 | 6小时重叠，效率有未覆盖边界，无舍入规则 | 本实现仅计算唯一匹配；其他输入退出3 | 网上常见的≥85%及不同6小时等号规则不能冒充1989原文 |
| 原版完整问卷回答才能计分 | 2005年官方说明增加Q5j缺失置零处理 | 官方Access数据库未取得，不能声称检查了查询实现 | 本实现未混入2005缺失规则；不使用简版B-PSQI或PTSD附加版 |

## 本次材料审计（2026-11-26）

上次登记为B的原因是旧分级要求长期衰老读出，并非已知系数缺失。此次先核对作者当前材料及数据库，再按新版个人睡眠质量标准实现A；没有证据表明本次找到的是上次登记后新发布的资料。

- 本机未提供浙江大学缓存根目录，因此没有可读的缓存文件；没有把缓存或下载的全文带入仓库。
- [DOI/出版社文章页](https://doi.org/10.1016/0165-1781(89)90047-4)和[ScienceDirect](https://www.sciencedirect.com/science/article/pii/0165178189900474)：尝试打开，出版社403，未能审计该页面的附件栏，不能声称出版商没有其他附件。
- [作者所在大学精神科的完整21页PDF](https://www.psychiatry.pitt.edu/sites/default/files/inline-files/PSQI%20Article.pdf)：成功下载至临时目录；全文及pp.209–213文内附录已读，计分页逐页图像核对。大学[睡眠中心副本](https://www.sleep.pitt.edu/sites/default/files/assets/Instrument%20Materials/PSQI-Article.pdf)亦可由网页工具打开。另对照可搜索的同篇论文[PDF文字副本](https://esmotech.com/sites/default/files/Original-Pittsburgh-Sleep-Quality-Index-PSQI-paper-1988.pdf)，OCR中85和10–18等误读以大学PDF图像为准。
- 原文Table 1列component与各组r/p；Table 2列item与各组r/p；Table 3列各组分量和总分的mean、SD、adjusted mean以及ANCOVA比较。Fig.1为分量轮廓，Fig.2为总分分布；均不含个体回答与总分的成套案例。计算不需要这些相关系数或群体均值。正文没有引用单独Supplementary Tables、eMethods或GitHub、Zenodo、OSF仓库。
- [官方现行资料目录](https://www.sleep.pitt.edu/research/measures-and-study-instruments)与[PSQI专页](https://www.sleep.pitt.edu/psqi)：均已打开。原论文、Instrument、Scoring、数据库使用说明、语言列表均已核对；本论文没有引向后来的B-PSQI/PTSD附件，不将它们并入方法。
- [PSQI_AU1.4_eng-USori.pdf](https://www.sleep.pitt.edu/sites/default/files/assets/Instrument%20Materials/PSQI_AU1.4_eng-USori.pdf)：四页正式英文表单，题号及选项核对。目录中的“PSQI Scoring”实际链接到[PSQI-Instrument.pdf](https://www.sleep.pitt.edu/sites/default/files/assets/Instrument%20Materials/PSQI-Instrument.pdf)，也是四页问卷，不把它误称计分算法。
- 专页实际的[Exhibit A-PSQI scoring.pdf](https://www.sleep.pitt.edu/sites/default/files/assets/Instrument%20Materials/Exhibit%20A-PSQI%20scoring.pdf)：两页完整读取。明确2005-05-20 Q5j规则变化；若干文字不等式未包括区间端点，不能修复原版歧义。
- [数据库使用说明](https://www.sleep.pitt.edu/sites/default/files/assets/Instrument%20Materials/PSQI-How-to-Download-and-use.pdf)：六页已读，介绍Microsoft Access表、录入表单和查询；不是系数表。目录当前“PSQI Scoring Database (PSQI Scoring Database.zip)”只有文字、没有可跟随下载链接。另尝试同目录的“PSQI%20Scoring%20Database.zip”和“PSQI-Scoring-Database.zip”路径均不可访问；未打开数据库，不能声称其中没有其他规则。已核对所用的每个常数均独立印在原附录，本实现不依赖该数据库。
- [语言列表](https://www.sleep.pitt.edu/sites/default/files/assets/Instrument%20Materials/PSQI%20TRANSLATION%20LIST%204.2012.pdf)：一页已读，只列语言及MAPI标识，不提供新计分参数。
- 检索作者材料及代码/数据库线索，未发现原论文发布的GitHub、Zenodo或OSF项目；第三方重写程序不是常数来源。

本技能不重新发布整份受版权保护的问卷，也不包装为官方中文量表。实际使用条件见大学官网；“个人自用无需申请”的说明不自动覆盖商业/临床分发。
