# 材料核查记录

核查日期：2026-11-24。机器无浙江大学缓存目录；通过出版社公开网页取得全文。下载件只放临时目录，未复制到技能或仓库。

## 出版社材料

| 材料 | 访问/读取情况 |
|---|---|
| Nature article HTML | 全文、Methods、Data/Code availability、Extended Data captions、Competing interests 均已打开 |
| MOESM1 Supplementary Information | 完整 PDF 98,915,852 bytes；已提取并检查 Notes 1–5、Figures 1–60、内嵌技术表（含 Table S1 的标准品 VAF、mCA 检测参数表和优化参数表） |
| MOESM2 Reporting Summary | PDF 已打开；记录样本与盲法/验证人数版本差异 |
| MOESM3 Supplementary Tables | XLSX 全部 12 个 sheet（索引和表 1–11）已打开，表头见下；表 6 与作者 CSV 对读 |
| MOESM4 Peer Review File | 完整 PDF 66,208,244 bytes；已打开审稿意见及回复，含方法验证、数据释放和临床背景讨论，不把修订过程中的旧数当作最终参数 |

以上四个附件的出版社原始 URL 都在 skill.json 的 paper.supplements。

## Supplementary Tables 表头

### Supplementary Table 1

Gene | Transcript | Chromosome | Location | Start | End

### Supplementary Table 2

Chromosome | Number of targeted SNPs | Mean gap between SNPs (kb)

### Supplementary Table 3

Chromosome | Start | End | Targeted SNP IDs

### Supplementary Table 4

Chromosomal rearrangement | Gene | Transcript | Chromosome | Location | Start | End | % missing  due to repetitive regions

### Supplementary Table 5

Input DNA | Fragmentation time (mins) at 32oC | 1st PCR (cycles) | 2nd PCR (cycles) (SNV/ indel panel) | 2nd PCR (cycles) (mCA, chromosomal rearrangement panel)

### Supplementary Table 6

Sample name | Age sample taken | Months to diagnosis (in pre-AML case/ matched pre-AML case for controls) | Age at AML diagnosis (in pre-AML case/ matched pre-AML case in controls) | Matched sample | Chromosome | Start | End | REF | ALT | Total depth | Variant depth | VAF | Intronic or exonic | Variant type | Gene | Transcript | Exon | cdNA | Amino acid change | Exonic function | COSMIC ID | COSMIC total count | COSMIC haem/lymphoid count | COSMIC sites | ExAC frequency (all) | gnomAD frequency (all) | clinvar_allele_id | clinvar_dn | clinvar_disdb | clinvar_rev | clin_sig

### Supplementary Table 7

Sample name | Age sample taken | Months to diagnosis (in pre-AML case/ matched pre-AML case for controls) | Age at AML diagnosis (in pre-AML case/ matched pre-AML case in controls) | Matched sample | mCA caller | mCA type | Chromosome | Start | End | Span (Mb) | Cell fraction | 95% lower cell fraction (phased caller) | 95% upper cell fraction (phased caller) | p-value (phased caller) | Significant (phased caller) | Index timepoint (for phasing) | 

### Supplementary Table 8

Sample name | Clone number | Variants in clone | Highest VAF = 1st single-mutant clone | Pigeon hole principle | Correlated dynamics | High VAF clone already present (+ no discordant dynamics) | Faster growth rates = more likely not single mutant | Variant trajectory cross-over (so not in same clone) (the variant(s) which the final variant in the clone crosses over with are shown in brackets) | Not correlated dynamics (the variant(s) which the final variant in the clone has non-correlated dynamics with are shown in brackets) | Missing driver needed to explain change in growth | Comments

### Supplementary Table 9

Sample name | Clone | Fitness (% per year) | Establishment age (years) | S.D. fitness | S.D. establishment age | 95% range optimizer result: Fitness | 95% range optimizer result: Establishment age

### Supplementary Table 10

AML = acute myeloid leukaemia, CMML = chronic myelomonocytic leukaemia,  ET = essential thrombocythaemia, MDS = myelodysplastic syndrome, MF = myelofibrosis, MPN = myeloproliferative neoplasm, DLBCL = diffuse large B-cell lymphoma, NHL = Non-Hodgkin's lymphoma, NSCLC = Non-small cell lung cancer, CTEPH = Chronic thromboembolic pulmonary hypertension

### Supplementary Table 11

Sample | Group | Metho | B-cells (%) | NK cells (%) | CD4 T-cells (%) | CD8 T-cells (%) | Monocytes (%) | Neutrophils (%) | Eosinophils (%)

## 公开代码与数据

- [preAML_evolutionary_dynamics](https://github.com/the-blundell-lab/preAML_evolutionary_dynamics) 已克隆，commit `5a53fe78c58956e0f2276ba1cac8422d0cfdc60d`；打开 README、Figure_5f.ipynb、Data_files/Somatic_SNV_indel_FLT3_calls.csv，并核对代码/数据目录。此实现独立编写，不复制 GPL 分析程序。
- [TETRIS-seq](https://github.com/the-blundell-lab/TETRIS-seq) 已克隆，commit `f3e3c1291baa966d302406505a5a9cf8e0341b3f`；打开 README 和目录，涵盖 SSCS/DCS、噪声校正、结构变异与 mCA 调用；本技能不执行上游流程。
- [Zenodo 23197961](https://zenodo.org/records/23197961) 分析代码归档：直接请求 403，web 打开超时；GitHub 对应仓库已打开。
- [Zenodo 22963603](https://zenodo.org/records/22963603) TETRIS-seq 归档：403；GitHub 对应仓库已打开。
- [Zenodo 22846473](https://zenodo.org/records/22846473) GRCh37/b37 与 dbSNP 参考文件归档：403，未下载，单条已注释记录的筛查不依赖它。
- [Zenodo 22262497](https://zenodo.org/records/22262497) somatic VCF：403，未取得归档；同一组发表 calls 的表 6 和作者 CSV 已打开，不声称读过 VCF。
- [EGA EGAS50000002168](https://ega-archive.org/studies/EGAS50000002168)、[EGAD50000003110](https://ega-archive.org/datasets/EGAD50000003110)、[EGAD50000003111](https://ega-archive.org/datasets/EGAD50000003111) 三个公开目录页均已打开；原始 reads、germline calls、未过滤 calls、未取整个体资料受 Data Access Committee 管理，未申请或下载。
- UK Biobank Application 58387：作者 Figure_5f.ipynb 明示个体输入不能再分发，缺失的文件名为 `Data_files/CH_double_mutants_AML_anonymised.tsv`。没有将该受控表描述为公开可下载。

## 可行性结论

所需的热点替换查表与两个阈值全部印在最终正文；补充表 6 已给出可复现的计数/VAF 对，故可实现受限的个人记录读出。不可访问的归档和受控数据限制完整研究重现，不构成本计算缺失的常数。无需训练、拟合或从第三方反推参数。
