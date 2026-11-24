# 材料审计

核查日期：2026-11-25。用户说明本机没有浙大缓存目录，因此直接读取出版社公开资料。下载件仅放临时目录，未将全文或补充附件复制到仓库。

## 全文及依赖来源

- [2018 文章页及全文](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002718)：读取 HTML 和出版社 XML；检查 Methods、Results、Discussion、Tables 1–4、Figures 1–7（图像及图注）、Data Availability、Funding、Competing interests 和所有补充链接。
- [2019 正式更正](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002760)：读取全文和 MathML，确认所有常数、自然对数与分母；更正页没有其他补充文件。
- [本文参考文献 12：原始方法 Table 1](https://www.aging-us.com/article/101414/text)：核对所有血检单位，解决 S1 Table 的白蛋白、CRP 标签冲突。这里只用该表的单位，所有计算常数来自 PLOS 更正；不实现该文的甲基化模型。
- 数据声明的旧 [NHANES 门户](https://www.cdc.gov/nchs/nhanes/index.htm) 返回 404；已打开 [CDC 新版介绍与数据入口](https://www.cdc.gov/nchs/nhanes/about/index.html)。这是原始调查数据库入口，不是本研究冻结的逐人预测结果。没有下载完整 NHANES 队列或声称复现队列统计量。
- 未发现本文链接的 GitHub、Zenodo、OSF、专用代码或冻结个人预测数据。网页页脚的 PLOS thesaurus GitHub 链接是出版主题词库，不是本文分析代码。

## 全部八个补充文件

| 期刊标签 / 文件标识 | 已读取内容 | 下载文件 SHA-256 |
|---|---|---|
| [S1 Appendix / s001](https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=10.1371/journal.pmed.1002718.s001) | DOCX；Methods、Results、References；KDM-BA 的补充比较，未打印完整个人 PhenoAge 算例。 | `9057c2647446b114e7266b1c06ac844f3181919be9b303410f3f4bff44ab9cee` |
| [S1 Fig / s002](https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=10.1371/journal.pmed.1002718.s002) | TIFF；已打开图像。KDM BioAgeAccel 与年龄组和疾病数的组间柱状图。 | `d80fa0c5d20fb7bc9091e8760ab5de01b2739fb8e2bdde293745f87b35d241ec` |
| [S2 Fig / s003](https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=10.1371/journal.pmed.1002718.s003) | TIFF；已打开图像。两个人群 ROC，表头 AUC、SE、Bonferroni P-value；不是个人输入输出表。 | `b818add9a6ba68d2e94dd31baca9b649b0f09877d09c8c8d78a39d6078da1bf4` |
| [S1 STROBE / s004](https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=10.1371/journal.pmed.1002718.s004) | DOC；已读取文件中的 STROBE 清单正文，列为 Item No、Recommendation、Author’s Response，按条目指向主文。 | `caa909a5cf6c313685fae7c74e8e39540af7ce00a343fd8a4926786333910673` |
| [S1 Table / s005](https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=10.1371/journal.pmed.1002718.s005) | DOCX；Characteristics、No. (%) or mean ± SD；包含九项血检的描述均值与单位，非给定输入的预测输出。 | `cf38b36f12e4cee83a33ae9ca99e4d09f8382ed2b497809df475a65c00158a09` |
| [S2 Table / s006](https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=10.1371/journal.pmed.1002718.s006) | DOCX；No. of death、Hazard Ratio (95% CI)、z-score、P value；KDM 死亡关联。 | `243c46837da1874504ff5dc6a50a19f11f1e34a740b1b3f9e59973efbdc48493` |
| [S3 Table / s007](https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=10.1371/journal.pmed.1002718.s007) | DOCX；亚组、Hazard Ratio (95% CI)、z-score、P value；KDM 亚组关联。 | `a45a3aacbb8267e4b1c17ecc044997ab443c202fadadfe67c4d31b27d33db0fa` |
| [S4 Table / s008](https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=10.1371/journal.pmed.1002718.s008) | DOCX；Model、Hazard Ratio (95% CI)、Z score、P value；KDM 最高龄组关联。 | `510bdc8332c51b559f46ff80b81a168ee25af8ae66606c04a65c2b48b513a1cf` |

没有未下载的本文补充文件。来源所需字段已经齐全，故无需写 pending 的 PIPELINE_NOTE.md；缺的是可复现的印刷个人算例，按流水线规则保留 draft。

## 不是算例的已检查数字

引言中的实足 50 岁、表型 55 或 45 岁没有血检输入；Fig 3 的相关系数和残差统计不是个人公式的算例；Fig 6 的寿命按性别和残差五分位建模，未打印构造这些预测所需的完整参数。主文及附件中的风险比、AUC 和 S1 Table 的边际均值均不能冒充本公式的算例。
