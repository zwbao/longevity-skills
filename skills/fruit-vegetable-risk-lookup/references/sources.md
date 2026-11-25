# 来源与材料核查记录

核查日期：2026-11-25。用户明确本机无浙大全文缓存，未从缓存复制任何文件进仓库。源PDF、DOCX、全文XML与抽取文本只保存在本次工作临时目录；仓库仅保留所需数值及来源说明。

## 全文与附件

- 出版社文章页：https://academic.oup.com/ije/article/46/3/1029/3039477 。DOI跳转及直接访问均尝试，访问受阻（重定向/403）；浏览器连接亦超时。
- PMC完整正文：https://pmc.ncbi.nlm.nih.gov/articles/PMC5837313/ 。已读方法、结果、正文表、讨论、资助和利益冲突。正文页面列出恰好两个补充文件。
- 完整JATS XML：https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5837313/fullTextXML 。实际成功下载，核对全文及两个 `supplementary-material` 元素，未链接作者代码/数据仓库（GitHub、Zenodo、OSF等）。正文提及从六个研究作者获得补充信息，是本荟萃分析的数据来源，不是另一个公开文件链接。
- 出版类型：https://pubmed.ncbi.nlm.nih.gov/28338764/ ：Meta-Analysis、Systematic Review；卷期2017 Jun 1;46(3):1029–1056。
- `supplementary_materials_dyw319.pdf`：https://pmc.ncbi.nlm.nih.gov/articles/instance/5837313/bin/supplementary_materials_dyw319.pdf 。PMC直接附件下载遇浏览器验证，已由Europe PMC官方接口获取完整文件（见下）。367页，SHA-256 `5f582fe71db42734256e2c4b4148140063fb9589bf628d8869e15d0bdb01d3c9`。
- `supplementary_webappendix_dyw319.docx`：https://pmc.ncbi.nlm.nih.gov/articles/instance/5837313/bin/supplementary_webappendix_dyw319.docx 。实际已通过Europe PMC获取并解压阅读word/document.xml全文，内容为MOOSE报告清单，字段是报告项目和对应页码/表号；没有额外模型系数或数据链接。SHA-256 `46169fb1f302d69162af0063243787529bddac24a289e514a603645bb598936d`。
- 成功获取全部附件的官方接口：https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5837313/supplementaryFiles 。ZIP内有上述两个文件，以及正文图1–6的GIF/JPG；没有额外研究数据或程序包。首次请求超时，延长请求后成功。
- 机构库：https://eprints.whiterose.ac.uk/id/eprint/106013/ 。已打开出版版及Supplemental Material入口。机构库补充PDF SHA-256 `1783c4c168e94335bf16be65364dba4a337fd464d99a44eac616dba771da5727`。其PDF二进制与Europe PMC不同，但两份通过 `pdftotext -layout` 的全部抽取文本经 `cmp` 完全一致，使用的数值表相同。

## Supplementary Materials 的内容

| 位置（PDF物理页） | 实际内容/列 | 本技能处理 |
|---|---|---|
| 第2页 Supplementary Methods | 人群归因死亡的参照摄入量、摄入类别、地区处理 | 已读，非个人模型参数 |
| 表1，第3–4页 | PubMed检索词与组合 | 已查 |
| 表2，第5–20页 | 排除理由、文献 | 已查 |
| 表3–7，第21–157页 | Author/year/country、Study name、Follow-up、Study size/gender/age/number of cases、Dietary assessment、Exposure、Quantity、RR (95% CI)、Adjustment for confounders | 已打开相关表，核对队列定义；不用这些单队列数据重拟合 |
| 表8–11，第158–161页 | 合计/水果/蔬菜；CHD或总卒中；incidence/mortality、incidence、mortality；每列 g/d 和 RR (95% CI) | 全列冻结 |
| 表12–13，第162–163页 | 缺血性/出血性卒中；合计、水果、蔬菜；g/d、RR (95% CI) | 全列冻结，表13合计无RR |
| 表14–17，第164–167页 | CVD或总癌症；合计/水果/蔬菜；incidence/mortality、incidence、mortality；g/d、RR (95% CI) | 全列冻结 |
| 表18，第168页 | 全因死亡；合计、水果、蔬菜；g/d、RR (95% CI) | 全列冻结 |
| 表19–27，第169–177页 | 指定食物亚类；g/d、RR (95% CI)、非线性P值 | 已打开，合同不含亚类 |
| 表28–32，第178–187页 | 分层变量、n、RR (95% CI)、I²、异质性P值 | 已打开，不按个人条件拼接层间结果 |
| 表33，第188页起 | 地区/国家归因比例和死亡数，500与800 g/d参照 | 已打开，非个人输出 |
| 图1–263，后续页至第367页 | 高低比较、线性/非线性剂量反应、漏斗/敏感性及逐一排除分析 | 同一PDF内已核查索引与相关结果，查表不用图像取点 |

## 数据提取

对补充PDF做 `pdftotext -layout`；每张表8–18各占一页。用每页 `g/d` 表头起始位置切开列，从数字行中严格提取 `摄入量 RR (CI低-CI高)` 或参照行 `摄入量 1.00`。按纸面表头手工声明食物组/结局/分析类型的列序。空白、横线及非线性P值不进入数值表；没有生成或推断常数。

`data/lookup.csv` 的列：table、pdf_page、food_group、outcome、endpoint、intake_g_d、rr、ci_low、ci_high。所有数值保留印出精度；CI空字符串代表纸面未印。`data/curves.json` 保存全部45列的身份与参照；唯一全空列的参照为null。44列有651行数值。对表18做了PDF渲染视觉核对，所有11张表的文本数值已检查；测试另外覆盖每张表的代表行和错列高风险处。

来源文章标注 CC BY-NC 4.0；冻结的数据保留该来源归属与非商业限制，不以仓库代码许可证覆盖来源材料。没有把原始PDF、DOCX或全文复制进仓库。
