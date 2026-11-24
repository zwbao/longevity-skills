# 材料核对记录

核对日期：2026-11-24。本机未提供图书馆缓存目录；材料从公开期刊来源读取，全文及补充文件保留于临时目录，没有复制到仓库。仓库只保存所需的派生系数表。

| 已打开材料 | 实际内容/列名 |
|---|---|
| [期刊HTML全文](https://www.nature.com/articles/s41514-026-00449-8) | Results、Methods、Data availability、Competing interests和全部补充下载链接；无其他Zenodo、OSF或本文专用代码链接 |
| [期刊PDF全文](https://www.nature.com/articles/s41514-026-00449-8.pdf) | 10页；Table 1: Seq ID, Gene ID, UniProt ID, Target, Beta, SE, P value；Table 2: Seq ID, Gene ID, UniProt ID, Target, Weight，含Intercept和Sex (Male)；Table 3: Estimate, 95% CI, p value；Table 4: MitoAge unadjusted与Bioenergetics的R、P。Figure 4也进行图像检查 |
| [Heimler et al Supplemental Figures and Tables](https://static-content.springer.com/esm/art%3A10.1038%2Fs41514-026-00449-8/MediaObjects/41514_2026_449_MOESM1_ESM.pdf) | 1页；Supplementary Figure 1与Supplementary Table 1。后者列Unadjusted R、Unadjusted P-value、Adjusted R、Adjusted P-value；没有个人公式示例 |
| [Supplementary Data 1](https://static-content.springer.com/esm/art%3A10.1038%2Fs41514-026-00449-8/MediaObjects/41514_2026_449_MOESM2_ESM.xlsx) | 三张工作表全部解包读取（含所有行），无隐藏工作表、批注或外部链接；详见下表 |
| [eNetXplorer GitHub](https://github.com/juliancandia/eNetXplorer) | 已克隆，检查README、R实现、man和vignettes；为通用包，示例数据是Leukemia_miR、H1N1_Flow、breastCancerSurv、QuickStartEx等，不是GESTALT输入输出 |

| XLSX工作表 | 数据行数 | 列名 |
|---|---:|---|
| Univariate Results | 1305 | SeqId, SomaId, Target, UniProt, EntrezGeneID, EntrezGeneSymbol, beta_coefficient, std_error, p_value, logp, fdr, Organism, Units, Type, Dilution |
| eNetXplorer Results | 1306 | SeqId, SomaId, Target, UniProt, EntrezGeneID, EntrezGeneSymbol, Coefficient, p_Value, Organism, Units, Type, Dilution |
| MitoAge | 27（25蛋白+截距+性别） | SeqId, SomaId, Target, UniProt, EntrezGeneID, EntrezGeneSymbol, Weight, Organism, Units, Type, Dilution |

表格网页工具曾无法读取独立Table页面，所需表均已在正式PDF完整打开，没有把下载失败当作材料未发表。后续PDF还纠正了初查XLSX时性别编码不明的疑问。Data availability说额外数据可能需向作者索取；没有公开链接的个人数据不假装已经取得。

查询补充编码/实现时还检查公开搜索“MitoAge sex01”及本DOI加code/data的结果；PubMed、ResearchGate和二手报道只作发现入口，未将二手参数用于计算。

## 来源校验

eNetXplorer检查提交：`2d4e9527330ae3d5a5c6143add4656e09bf987bb`。论文使用版本1.1.3；当前仓库只用于材料审计，不作为本技能运行依赖。

- `mitoage-main.pdf` SHA-256：`af6bb3ff48bfeb3d42b73012908a1f1f556c4fa2f4fc1231d3977160db6f87ae`。
- `mitoage-supp.pdf` SHA-256：`7108db2708301f6675e77d00b1c69f9c64362900f24ab02912eddf04ab5c4b70`。
- `mitoage-data.xlsx` SHA-256：`638a1d5d135afa6c30ec879ab35c9017ea2a4b4911daeb746b26b1b38c526ec3`。

期刊全文和附件采用CC BY 4.0；派生系数归属Heimler等（2026），由本技能从MitoAge工作表抽取，未重估系数。
