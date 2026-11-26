# 来源与材料清单

访问核对日期：2026-11-26。无用户指定的图书馆缓存目录。完整PDF与转换文件仅在/tmp，不复制到仓库；计算所需六行表值冻结于scripts/presets.py。

- 正式发表全文：<https://www.thelancet.com/article/S0140673615003402/pdf>，网页工具可读取完整正文（表1–3、图1–4、Methods、Discussion、利益冲突及参考文献）。常规Lancet fulltext及ScienceDirect页面访问403。另下载并用pdftotext核对PMC正式PDF公开副本：<https://rcastoragev2.blob.core.windows.net/2bfbf766822b48a383348459230c679d/PMC4691901.pdf>。
- Supplementary appendix：<https://ars.els-cdn.com/content/image/1-s2.0-S0140673615003402-mmc1.pdf>，curl成功获取10页PDF。逐页文本及图像核对，识别不正确的字体编码时用渲染页确认。未发现其他附录文件或发布代码/数据链接。
- PubMed文章页面及出版类型：<https://pubmed.ncbi.nlm.nih.gov/26466050/>。
- Coventry作者机构条目：<https://pureportal.coventry.ac.uk/en/publications/contrasting-male-and-female-trends-in-tobacco-attributed-mortalit/>，列正式出版PDF；其直接PDF下载受限。
- PMC HTML触发验证码；Europe PMC HTML及REST全文/补充材料接口受限或超时，未用其失败响应作证据。web-access的CDP连接超时，最终使用公开静态PDF完成核对。

| 材料 | 页码 | 已打开的内容、列或轴 | 在技能中的用途 |
|---|---|---|---|
| 正文Table1 |1451|起始吸烟年龄；城乡及年代；CO；四类死亡数、RR及组别特异性CI|范围核对，未实现起始年龄分层|
| 正文Table2 |1453|每日量及组均量；城乡及年代；CO；All causes、Lung cancer、Ischaemic stroke or ischaemic heart disease、COPD，各有死亡数与RR/组别特异性CI|实现CKB六行，列及切点完整|
| 正文Table3 |1455|男性/女性/合计，按年龄列归因及总死亡数|背景，未当成个人输出|
| 附录封面、目录 |1–2|原始提交并经同行评审的附录；材料索引|确认文件身份及完整性|
| Webtable1 |3|Category、ICD-9、ICD-10|确认结局，特别是COPD原文宽口径|
| Webtable2 |4|CPSS men、CKB men、CKB women；Cause of deaths、No of deaths smokers/non-smokers、RR (95%CI)、PAF|核对性别与戒烟排除规则|
| Webtable3 |5|Characteristics、CPSS n、CKB n；基线年龄、教育、烟草类型和数量|核对样本子集及暴露口径|
| Webfigure1 |6|Region、All deaths (N)、RR &95%CI|核对城乡差异，未替代吸烟量表|
| Webfigure2 |7|Years stopped smoking；RR与区间；因病/主动停烟|核对停止原因，未实现戒烟情景|
| Webfigure3 |8|年龄、年度肺癌死亡率，ever/never-smokers，中国两队列与美国比较|背景，未数字化曲线|
| Webtable4（目录称Webfigure4）|9|Age at risk、Person years、Lung ca deaths、Rate/100000；中国男性两期、女性较新期|不是个人基线风险函数|
| Webtable5（目录称Webfigure5）|10|Age at risk；美国男女Person years、Annual lung cancer mortality/100000，Crude/Smoothed|既往比较数据，不是新验证队列|

核对文件SHA-256（仅用于材料溯源）：

- tobacco-published.pdf: `235311f0cd712b5111404fd96a1ff10d6eec36b3236de81a2ac8a99eef8c5ecf`
- tobacco-appendix.pdf: `975f87e644834a050c22b24f4b853dafeb349f79dedca6676c3922496c7363e2`
