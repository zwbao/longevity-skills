# 获取与参数审计

检索日期：2026-11-25。用户注明本机无图书馆缓存，未复制缓存文件进仓库。

- [出版社全文](https://link.springer.com/article/10.1186/s12916-016-0730-3)：已打开正文、Table 1、图题和数据声明。
- [Europe PMC 全文 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5137221/fullTextXML)：完整阅读 Methods、Results、Discussion、结论与声明，核对 supplementary media 和外部链接。
- [Europe PMC 文献记录](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1186/s12916-016-0730-3&format=json)：核对 publication types。
- [Additional file 1](https://static-content.springer.com/esm/art%3A10.1186%2Fs12916-016-0730-3/MediaObjects/12916_2016_730_MOESM1_ESM.pdf)：唯一补充文件，104 页，S1–S23 和 S1–S74 图；已下载、打开、提取全文并核对逐页目录；重点读取 S7、S14–S17、S22、S23 及全因死亡图；第 41 页另以渲染图核对。

没有其它 Appendix、eMethods、单独数据文件或 GitHub/Zenodo/OSF 成品链接。正文声明没有更多可用数据。不把引用文献的方法或软件 Stata 12.0 当作作者发布的模型代码。

补充 PDF SHA-256：`78ab5d89e2025830672c2f2557a39045438fa4a402a97055f896f7d669250a13`。原文件仅保存在临时目录，仓库只保存必要的来源记录与常数。

## 表索引（页码为 PDF 印出页码）

- p.2: Supplementary Table 1. Search strategy in PubMed
- p.4: Supplementary Table 2. List of excluded studies and reason for exclusion
- p.8: Supplementary table 3. Nut consumption and coronary heart disease
- p.12: Supplementary table 4. Nut consumption and stroke
- p.18: Supplementary table 5. Nut consumption and cardiovascular disease
- p.22: Supplementary table 6. Nut consumption and total cancer
- p.26: Supplementary table 7. Nut consumption and all-cause mortality
- p.32: Supplementary table 8. Nut consumption and respiratory disease mortality
- p.34: Supplementary table 9. Nut consumption and diabetes mortality
- p.36: Supplementary table 10. Nut consumption and neurodegenerative disease mortality
- p.38: Supplementary table 11. Nut consumption and infectious disease mortality
- p.39: Supplementary table 12. Nut consumption and kidney disease mortality
- p.40: Supplementary table 13. Nut consumption and inflammatory disease mortality
- p.41: Supplementary Table 14. Relative risks from nonlinear dose-response analysis of peanuts and coronary heart disease, stroke, cardiovascular
- p.41: Supplementary Table 15. Relative risks from nonlinear dose-response analysis of peanuts and mortality from total cancer, all causes, respiratory
- p.42: Supplementary table 16: Subgroup analyses of nuts and coronary heart disease, stroke, and cardiovascular disease, per 28 grams per day
- p.44: Supplementary table 17: Subgroup analyses of nuts and total cancer and all-cause mortality, per 28 grams per day
- p.46: Supplementary Table 18. Newcastle-Ottawa score for studies included in the dose-response analysis of nut consumption and coronary heart
- p.47: Supplementary Table 19. Newcastle-Ottawa score for studies included in the dose-response analysis of nut consumption and stroke
- p.48: Supplementary Table 20. Newcastle-Ottawa score for studies included in the dose-response analysis of nut consumption and cardiovascular
- p.49: Supplementary Table 21. Newcastle-Ottawa score for studies included in the dose-response analysis of nut consumption and total cancer
- p.50: Supplementary Table 22. Newcastle-Ottawa score for studies included in the dose-response analysis of nut consumption and all-cause mortality
- p.52: Supplementary Table 23. Attributable fractions and number of deaths due to coronary heart disease, cancer, respiratory disease, diabetes, and

## 列结构与可计算性

- S1：检索序号与检索词/组合；S2：排除理由、参考文献号及清单。
- S3–S13：Author/publication year/country、Study name、Study period、Number of participants/gender/age/number of cases or deaths、Dietary assessment、Exposure and subgroup、Nut consumption frequency or amount、Relative risks (95% confidence intervals)、Adjustment for confounding factors。
- S14：g/d；冠心病、卒中、心血管病各自 incidence/mortality、incidence、mortality 的 RR (95% CI)，及 pnonlinearity。
- S15：g/d；Total cancer、All-cause mortality、Respiratory disease、Diabetes、Neurodegenerative disease 的 RR (95% CI)，及 pnonlinearity。是离散表，没有完整样条系数/协方差列。
- S16–S17：亚组、结局、n、RR (95% CI)、I²、Ph1、Ph2。不是个人风险校正系数。
- S18–S22：作者年份、代表性、非暴露组选择、暴露测量、基线无结局、年龄校正、其它校正、结局评估、随访长度/完整性、总质量分。
- S23：Region、Country、各死因的 % 和 N（共同参照摄入）；人口归因结果不适合个人计算。
- 图 S1–S10：高低摄入组；S11–S34：树坚果/花生心血管与癌症；S35：漏斗图；S36–S43：树坚果、花生、花生酱全因死亡；S44–S69：其它死因；S70–S74：逐项排除敏感性。

Table 1 的 All-cause mortality / Total nuts 的 Dose-response RR 及脚注 b 提供本技能全部参数。没有把补充表的其它 RR 加入公式。
