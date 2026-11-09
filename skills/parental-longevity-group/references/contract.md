# 父母长寿分组：合同、规则来源与核对

## 产品合同

1. 用户提供父亲、母亲各自的年龄（已去世写去世时年龄，在世写目前年龄），性别和本人年龄可选。
2. 技能自带论文印出的分组切点和排除规则，不向用户要论文、PDF、基因数据或补充表。
3. 报告给出父母长寿分组（高、中、低）、活到 85 岁的父母人数、父母年龄均值，并转述论文正文里该组与低组相比的差别方向。不能算的：多基因长寿评分（PRS-CS 后验位点权重没有公布）；各组差别的数值（正文表 3、表 5 本次没有读到，见下文）。不预测个人寿命，不诊断，不给剂量或用药建议。

## 来源

| 代号 | 出处 | 用到什么 | 许可 |
| --- | --- | --- | --- |
| [P] | Seidu NM, Rydén L, Skoog J 等. GeroScience (2026). doi:10.1007/s11357-026-02501-7 | 方法“Study population”的排除规则；“Definition of the PL groups”的切点和父母年龄均值规则；结果正文的各组差别方向和人数；补充表 S1、S4 | 开放获取（CC BY 4.0），只摘规则和方向 |

材料：出版社全文页（文本，开放获取）；ESM 1（docx，补充表 S1–S6）。正文表 1–5 的单独页面（`/tables/1`–`/tables/5`）和 PDF 在本次抓取时都返回出版社的人机验证页，没有读到；Europe PMC 只有摘要（PMID 42726198，没有 PMC 全文）。论文没有代码仓库，数据按 GDPR 需申请（Data Availability）。

## 规则（照原文）

- 切点：“Participants with both parents surviving to age 85 were classified as “high-PL”, participants with one parent surviving to age 85 were classified as “medium-PL”, and participants where both parents died before age 85 were classified as “low-PL”.”
- 父母年龄是“at death or current”；“70 participants whose parents were still alive and classified as long-lived, as all were above age 85”——在世且已过 85 岁算活到 85 岁。
- 排除：“Thirty-four participants had missing data on one parent. We chose not to impute these parents’ ages”；“We excluded another 44 individuals where at least one parent died before age 41 years”。
- 均值：“The mean age of parents was calculated as a single continuous variable … in case of missing data for one parent’s age, the other was used”。论文只把均值当连续变量做补充分析（表 S2），没有给切点。

## 操作约定（论文没写死的地方）

- “活到 85 岁”按年龄 ≥ 85 计（85 岁去世算活到）。论文写“surviving to age 85”，没有说 85 岁整当年去世怎么算；本技能按“到达 85 岁”处理。
- 在世、还不到 85 岁的父母：论文人群的父母在世者都已超过 85 岁，没有这种情况。本技能把这位父母记为“未定”，`pl_group` 为空，`pl_status = provisional`，`pl_group_floor` 是按已活到 85 岁的人数得出的最低分档。
- 41 岁前去世：照论文排除，`pl_group` 和 `pl_group_floor` 为空，`pl_status = excluded`；父母年龄均值仍照算，仅供参考。
- 缺一方年龄：论文不补值、不分组；本技能当输入缺失，退出码 3，请用户补上。论文“缺一方就用另一方”的均值规则因此不会用到。
- 输入范围：去世年龄 0–120 岁，在世年龄 18–120 岁；单位为岁（years、yr、岁 都认）。

## 核对

论文没有印出某个人父母年龄对应分组的算例，正文表格本次也没有读到，所以没有可复现的印出示例；`validation` 保持 `draft`。测试核对：切点 85 和排除界 41 与方法一致；84/85、40/41 的边界；在世超过 85 岁算活到；在世未满 85 岁为未定；人数与结果正文印出的 194/488/444、17.2%/43.3%/39.4% 一致（只核对常数，不是复现）；缺值、重复、超范围、性别写错时退出码 3，报告里没有分组。

## 没有做的

- 多基因长寿评分：PRS-CS（默认设置）在 GWAS catalogue GCST008598（Deelen 等）和 1000 Genomes 欧洲 LD 参考上算出后验权重，论文和补充材料都没有公布权重；重新跑 PRS-CS 得到的权重和论文不一定相同，不做。
- 各组差别的数值（β、OR）：在正文表 3、表 5，本次没读到；报告只写结果正文里的方向。
- 性别：补充表 S4 显示中等组与 CRP、NfL 的关系有性别交互（P = 0.015、0.028），只在女性中出现；报告对女性中等组加一句，不改分组。
