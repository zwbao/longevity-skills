# 产品合同

用户提供自己的年龄、论文分层性别、手持测力计双手最大握力、DXA 四肢去骨瘦体重总和和同次 BMI，测量表包含数值及单位。
技能维护者取得并核对论文正文和补充附录，冻结正文表 3 的切点，运行不需要用户下载文献、队列或公开数据。
报告只计算 ALM/BMI、握力/BMI 并对照按性别区分的推荐和备选标准分别分层；不诊断肌少症、不预测个人失能或死亡、不提供药物剂量或启停建议。

流水线任务已授权实现此范围，无需再次确认合同。

## 可行性与来源

Studenski 等，The journals of gerontology. Series A, Biological sciences and medical sciences，2014 年 69(5):547–558，doi:10.1093/gerona/glu010。同行评审论文。

已读 [PMC 全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC3991146/)（Methods、Results、正文表 1–3、图 1 和 Discussion）及 [出版社官方 CDN 文章页面](https://oup.silverchair-cdn.com/article-minimal/672497)。后者是 DOI 跳转所指向的页面，包含补充材料的完整下载链接。主站 `academic.oup.com/biomedgerontology/article/69/5/547/672497` 及旧 `biomedgerontology.oxfordjournals.org/lookup/suppl/doi:10.1093/gerona/glu010/-/DC1` 返回 403，并不代表文件不存在。

已从上述官方页面中的签名链接下载 `glu010_Supplementary_Data.zip`（HTTP 200），其中仅有 `Appendix_Table_1_4.docx`；已逐表读取全部四张表，完整可用下载地址记录在 `skill.json`。归档路径为 `https://oup.silverchair-cdn.com/oup/backfile/Content_public/Journal/biomedgerontology/69/5/10.1093_gerona_glu010/1/glu010_Supplementary_Data.zip`。附录均不参与计算，因此不把原始文档复制入仓库。

附录表 1 列为 Statement、Agreement（1–5）及 mean，内容为会议调查；附录表 2、3、4 各是建议文字列表，分别为一般建议、项目过程与发现建议、知识空白及后续研究建议，没有个人预测值表或另附参数表。正文点名的会议材料页面 `http://biomarkersconsortium.org/sarcopenia_pdfs.html`（亦尝试 HTTPS）返回 404；它是旧会议议程与演示文稿链接，正文和已取得的附录给出了最终全部计算切点，不依赖该历史页面。文章未链接 GitHub、Zenodo、OSF、计算代码或可下载个体数据。

补充的获取尝试还包括 Europe PMC fullTextXML（超时，随后 503）、supplementaryFiles（503）、NCBI 旧和新 OA 文件查询（404）；web-access 浏览器 CDP 检查失败（WebSocket 连接错误）。这些失败已由成功取得的 PMC/出版社全文和官方 ZIP 解决。未使用本机订阅缓存；本任务注明没有缓存目录。

## 计算定义

Methods / Physical performance and strength：握力取双手测量的最大值。
Methods / Body composition：ALM 为双臂双腿去骨瘦体重之和，缺肢体测量者排除；本工具限定 DXA，不实现文中研究队列特有的 pQCT 推估或 BIA 转换。
Methods / Covariates：BMI = 体重 kg / 身高 m 的平方；接口接收已有 BMI。

表 3（列 Cutpoint、Men、Women）全部计算切点：

| 标准 | 男 | 女 | 判定 |
|---|---:|---:|---|
| 推荐：最大握力 kg | 26 | 16 | < |
| 推荐：ALM/BMI | 0.789 | 0.512 | < |
| 备选：最大握力/BMI | 1.0 | 0.56 | < |
| 备选：ALM kg | 19.75 | 15.02 | < |

ALM/BMI 采用 kg 除以 kg/m²，量纲为 m²；不是 ALM/身高²，也不是百分比。输出清单不把它误标为无量纲。握力单位沿用论文及测力计显示的 kg 约定，不接受牛顿输入。所有计算常数来自表 3；没有拟合、外推或重建系数。

年龄范围 65–120 岁、握力 0–150 kg、ALM 1–80 kg、BMI 10–80 kg/m² 是宽松输入检查范围，其中只有 65 岁下限是论文排除规则；其他界限均为实现层面的单位/异常输入检查，并非研究分布或医学正常范围。年龄不改变切点。g→kg 的 0.001 和 lb→kg 的 0.45359237 为精确单位换算，并由仓库单位表核对。

不合并推荐与备选结果，不添加步速诊断、现有其他学会标准或人群风险值。本方法是四项阈值分类，而非用于个人目标模拟的风险方程或时钟，因此没有 `--targets` 或 levers 输出。

## 验证状态

`validation.status = draft`，`inputs_status = draft`。已检索正文、表 1–3、图 1、补充附录表 1–4：表 1–2 是队列均值和比例，不能把组均值假装成个人例子；表 3 仅给阈值；图 1 是无数值的概念示意；附录是会议调查与建议。没有可独立复现的个人输入与输出示例。

先写 `tests/test_manifest.py`，再实现脚本。`test_table3_constants` 逐项断言论文打印的八个切点；其余测试为明确标记的合成边界/工程检查，包括切点相等及略低、推荐和备选独立、中文别名、单位换算、错误输入退出码 3、论文卡片与边界、清理旧结果。合成边界的 ALM 19.725 kg 和 12.8 kg、BMI 25 等输入不是论文病例，也不用于宣称 reproduced。没有把脚本输出复制为预期结果。

边界: 本报告仅按 FNIH 2014 研究切点描述握力和四肢瘦体重，不诊断肌少症，不估算个人失能或死亡概率，也不能据此开始、停用或调整药物。
