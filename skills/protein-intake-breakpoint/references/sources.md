# 材料核查记录

核查日期：2026-11-25。没有指定图书馆缓存，原始下载仅保存在临时目录，未复制进仓库。

- 期刊文章页 https://bjsm.bmj.com/content/52/6/376 和 early/2018/01/18/bjsports-2017-097608 已尝试打开，静态访问 403。浏览器 CDP 前置检查连接超时，因此改走开放存档。
- PMC HTML https://pmc.ncbi.nlm.nih.gov/articles/PMC5867436/ 经 curl 成功读取并核对九条附件链接；网页工具遇到验证页。单文件附件 curl 返回 HTML，没有误当 PDF。
- 全文 XML https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5867436/fullTextXML 成功读取，覆盖 Methods、Results、Discussion、Conclusion、Table 1、所有图注及声明。另视觉读取归档中的 Figure 5 JPG。
- 全部附件通过 https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5867436/supplementaryFiles 成功取得 ZIP；内含九个补充文件和正文图像。以下文件全部打开，未有未下载附件。
- 出版类型及卷期通过 Europe PMC search API（DOI 查询，resultType=core）核对；2018;52(6):376–384。
- 更正全文 https://pmc.ncbi.nlm.nih.gov/articles/PMC7513243/ 和 https://bjsm.bmj.com/content/54/19/e7 已核对：补充作者利益冲突，无数值更正。
- 文章 Data sharing statement 指向正文和附件。全文及附件未指向另行发布的 GitHub、Zenodo、OSF 仓库，故没有代码仓库可克隆。

## 九个补充文件

### Supplementary Appendix 1（bjsports-2017-097608supp001.pdf）

来源：https://pmc.ncbi.nlm.nih.gov/articles/instance/5867436/bin/bjsports-2017-097608supp001.pdf

已读 PDF 2 页；Medline、Embase、CINAHL、SPORTDiscus 检索式及日期。无计算参数表。

SHA-256: `070a39cd376476778d1be1cfe17bfc7b73db0bab8c3216aece1264246c6bc682`

### Supplementary Appendix 2（bjsports-2017-097608supp002.pdf）

来源：https://pmc.ncbi.nlm.nih.gov/articles/instance/5867436/bin/bjsports-2017-097608supp002.pdf

已读 PDF 1 页；行是研究，列为 Allocation concealment、Blinding of participants and personnel、Blinding of outcome assessment、Incomplete Outcome Data、Selective reporting、Other bias，值 L/H/U。

SHA-256: `68f88d16ed749096599006793e3024962b72eb2eb745f2f74571bb4f070ebd05`

### Supplementary Table 1（bjsports-2017-097608supp003.pdf）

来源：https://pmc.ncbi.nlm.nih.gov/articles/instance/5867436/bin/bjsports-2017-097608supp003.pdf

已读 PDF 2 页；Author and Year、Age、Sex、Training Status、Length (wk)、Frequency (d/wk)、Sets x Reps or %RM、1RM、MVC、Mass、FFM、FM、Fibre CSA、Mid-Femur CSA；结局主要用方向箭头。

SHA-256: `15f10cbd624ce5eeee7c3d01b40874a0d92ffe4f1c3e0a2491983d812e5463e2`

### Supplementary Table 2（bjsports-2017-097608supp004.pdf）

来源：https://pmc.ncbi.nlm.nih.gov/articles/instance/5867436/bin/bjsports-2017-097608supp004.pdf

已读 PDF 2 页；Author and Year，Supplement/Dietary Details 的 Composition、Amount、Timing、N，Placebo/Control Details 的 Amount、N。提供干预安排而非个人计算实例。

SHA-256: `de590a6ea8d0551910db2690ae8672dd118ae6ae9d41050e9b18005ef17b3e77`

### Supplementary Figure 1（bjsports-2017-097608supp005.jpg）

来源：https://pmc.ncbi.nlm.nih.gov/articles/instance/5867436/bin/bjsports-2017-097608supp005.jpg

已视觉读取 JPG；1RM 和 FFM 漏斗图及图注，标出排除的研究。

SHA-256: `2dd48ee6aeb784888580ff28c127074299021a73e6d767865b28f1c0973cc18b`

### Supplementary Figure 2（bjsports-2017-097608supp006.jpg）

来源：https://pmc.ncbi.nlm.nih.gov/articles/instance/5867436/bin/bjsports-2017-097608supp006.jpg

已视觉读取 JPG；肌纤维 CSA 与股中部 CSA 森林图及合并效应、CI。

SHA-256: `b31f34fa46a238ebcec9280bef22e3047edf9e05112bd206ad5b87178d9d9432`

### Supplementary Figure 3（bjsports-2017-097608supp007.jpg）

来源：https://pmc.ncbi.nlm.nih.gov/articles/instance/5867436/bin/bjsports-2017-097608supp007.jpg

已视觉读取 JPG；A 全样本、B 老年、C 年轻的基线摄入元回归；D 两年龄组的基线摄入对 FFM 变化的回归；不是总摄入拐点曲线。

SHA-256: `f1fe3a6ff20c12a6acee95828c686b05886ea7157f1861f211137ea86e6f3c9a`

### Supplementary Table 3（bjsports-2017-097608supp008.pdf）

来源：https://pmc.ncbi.nlm.nih.gov/articles/instance/5867436/bin/bjsports-2017-097608supp008.pdf

已读 PDF 1 页；Univariate、N、Coeff. (95% CI)、Adj. R²、I²、p-value，分别针对 1RM 与 Fat Free Mass。没有个人预测截距或完整个体示例。

SHA-256: `2fcd226ce7ddbe55583f43004d66e8e9c70f05d6b2f59ff709e2eb8ae04b3d66`

### Supplementary Figure 4（bjsports-2017-097608supp009.jpg）

来源：https://pmc.ncbi.nlm.nih.gov/articles/instance/5867436/bin/bjsports-2017-097608supp009.jpg

已视觉读取 JPG；1RM、FFM 的平均变化及蛋白补充相对贡献，图注有 9%、27% 和组水平样本量。

SHA-256: `9b0987c02c4a26b5cfc6714322a2606e23a3f783d6e1da804ac5d20d7953e99b`

## 参数可行性结论

位置比较仅需正文 Figure 5 印出的拐点，不需要重建回归截距或每项研究权重。所有运行常数均有定位：拐点、CI、p 在 Figure 5；观察摄入范围在 Discussion / Muscle mass；情境条件在 Methods / Inclusion criteria。无须未公开系数。没有完整个人计算示例，保持 draft，而不是将核对常数称为复现。

原文和补充材料标示 CC BY-NC 4.0。本技能不打包全文或补充图片/PDF，只保留必要事实、短引文及来源定位。
