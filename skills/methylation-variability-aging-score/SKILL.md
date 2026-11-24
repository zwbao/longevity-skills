---
name: methylation-variability-aging-score
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes the integrated DMP-DVP epigenetic score of Vishnyakova et al., J
  Gerontol A 2026 (CLSA and BLSA), from a person's blood methylation beta values: CpGs whose mean
  level or whose variability tracks frailty, cognitive and physical function are combined through
  elastic-net health scores and Cox mortality weights, then put on CLSA's age scale. Uses the 789-CpG
  EPIC model printed in Supplementary Table S15 and the 598-CpG 450K-restricted model from the
  authors' repository; each is computed only when all its sites are supplied. Use when the user
  mentions methylation variability, a DMP/DVP score or the CLSA epigenetic biomarker, or wants an
  aging score from 450K or EPIC data. It does not compute the paper's epigenetic age deviation
  (regression constants unpublished) or a mortality risk. Medicines and checkup labs are context; the
  report never says what to start or stop.
---

# 甲基化水平与变异性整合评分

你交血液甲基化芯片（Illumina 450K 或 EPIC）的 β 值，可另给年龄、现用药和体检。报告按论文补充表 S15 的 EPIC 模型（789 个位点）和作者代码仓库的 450K 限定模型（598 个位点）各算一个整合 DMP-DVP 评分；哪个模型的位点交齐就算哪个。缺位点不补 0。β 值不在 0 到 1 之间、写成百分比或 M 值、等于 0 或 1，或两个模型都没交齐，报告只列原因、不计算，命令返回 3，out/problems.json 列出缺的位点。

分数是年的刻度，但不是生物年龄；论文的“表观年龄偏差”需要的年龄回归常数没有公布，报告不算它，也不给死亡风险。

不要向用户要补充表、GEO、CLSA 数据或论文 PDF；权重已冻在 `data/`。IDAT 读不了，请用户先导出 β 值表。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python "$SKILL/scripts/personal_report.py" \
  --measurements betas.csv \
  --age 60 \
  --medications meds.txt \
  --labs checkup.csv \
  --out out
```

`--measurements` 用 `item,value,unit`，`item` 是 cg 号，`value` 是 β 值，单位列可以空着。用户给的是一行一个样本的宽表时，先转成这三列，一个人一份。`--age` 只在报告里对照显示。`out/result.json` 写 `dmp_dvp_score`（EPIC 模型）和 `dmp_dvp_450k_score`（450K 模型），没算的写 null。

报告最后一行是固定边界，原样保留。

方法说明见 [references/claims.md](references/claims.md) 和 [references/contract.md](references/contract.md)。
