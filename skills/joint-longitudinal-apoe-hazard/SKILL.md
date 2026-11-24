---
name: joint-longitudinal-apoe-hazard
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. 根据已确认的 APOE ε4 拷贝数和明确选择的 HRS 祖源模型，计算相对于零拷贝的失智关联风险比，并区分病前认知水平、认知下降和剩余直接关联。适用于询问 APOE ε4
  与失智风险、认知衰老路径的用户；不计算个人绝对风险或干预收益。
---

# APOE ε4 联合纵向风险路径

使用 Clapp Sullivan 等 medRxiv 2026 的联合纵向风险模型中，公开的 APOE ε4 剂量系数。预印本，未经同行评审。

## 用户命令

“我有 APOE ε4 拷贝数报告，请按明确选择的 HRS 祖源模型解释它与失智的相对风险及认知路径。”

## 输入和运行

只需要用户自己的已确认 ε4 整数拷贝数（0、1、2），以及明确选择的研究模型 EUR、AFR 或 AMR。不能从中文、国籍、自报族群推断研究祖源。东亚或未知祖源没有对应系数，停下说明缺口，不默认用 EUR。

报告若只说“携带 ε4”，并不能区分 1 与 2 拷贝；需先澄清。未知或缺失不填 0。不接受 APOE 蛋白浓度、插补剂量或未经核对的原始 SNP 文件。

将数据整理为 CSV，列为 `marker,value,unit`；指标键为 `apoe_e4_count`，单位 `1` 表示计数。支持清单内中文和英文别名。可选 `--age`（岁）和 `--sex`（female/male/unknown）仅用于上下文，不改变风险比。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --ancestry EUR --out out
```

命令中的 EUR 仅为调用格式示例，运行前必须确认所选模型。读 `out/report.md` 和 `out/result.json`；退出码 3 时读 `out/problems.json`，向用户解释缺项或错误，不能输出旧结果。

## 输出约定

- 中文报告以论文卡片开头，列总关联、经病前认知水平、经认知下降速度和剩余直接关联的 HR；参照均为同模型下 ε4 为 0 拷贝。
- 原文每拷贝的置信区间单独标明为研究估计，不冒充个人区间。总系数单独使用，不把 HR 相加。
- 不估计年限风险、终生风险、认知下降轨迹或其他 PGI；不诊断疾病，不把关联路径称作因果效应。
- 不提供 `--targets` 或遗传“改善目标”：基因拷贝数不是可改变的行为指标。
- 不向用户索要 Supplementary Tables、队列数据或作者代码；所需系数已冻结在 `scripts/presets.py`，来源和限制见 `references/contract.md`。

每份报告必须原样保留：

> 边界: 预印本，未经同行评审；结果是所选研究人群模型中相对于 0 拷贝 APOE ε4 的关联性风险比，不是个人患病概率、诊断或因果效应，不能据此开始或停用药物。未验证东亚人群，不把祖源组别等同于国籍或自报族群。

复现和排除范围见 `references/contract.md`，材料核查见 `references/claims.md`。
