---
name: emfra-factor-scores
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes separate EMFRA Autonomy and Psychological Distress scores from nine previously
  administered original EMFRA item scores. Use when an older adult provides EMFRA item ratings or asks
  to calculate the two EMFRA factors. Requires the original 0–2 item coding and applies
  factor-specific reversal. Reports in Chinese without a total score or clinical classification.
---

# EMFRA 自主性与心理困扰

用于已有原版 EMFRA 条目评分、年龄至少 65 岁且没有医生确诊痴呆的人。
依据 Fierro-Marrero 等 medRxiv 2026 预印本 v2 的 Reduced Model C。
研究实际年龄为 65–99 岁；超出这个范围时报告会提示适用性未验证。

用户提供同次评估的九项原始整数分数：第 1、2、5、6、7、11、12、15、19 项。
每项只能为 0、1、2，单位写 `score`。先确认这些分数来自原版 EMFRA 的规范评定，
没有提前反向计分，也不是别的问卷分数。中文名称仅用于解释，不是已验证的中文版问卷。
不要从握力公斤数、步速、生活满意度自由描述或其他量表猜出条目分数。
资料不全时，说明需要补充哪项 EMFRA 评定结果；不要默认缺项为 0。

```bash
python3 scripts/personal_report.py --measurements my_emfra.csv --age 75 --dementia-diagnosis no --out out
```

从本技能目录运行。`--age` 换成实际年龄；`--dementia-diagnosis no` 必须由已知病史支持。
已有医生确诊痴呆填 `yes`，程序会说明研究不适用并停止；病史未知时先确认，不代填 `no`。
`--sex` 可选，不进入计算。CSV/TSV 表头为 `marker,value,unit`：

| marker | 原版条目 | unit |
| --- | --- | --- |
| emfra_item1_score | 握力评分 | score |
| emfra_item2_score | 步速评分 | score |
| emfra_item5_score | 疲劳 | score |
| emfra_item6_score | 钱币算术 | score |
| emfra_item7_score | 注意与抑制 | score |
| emfra_item11_score | 孤独感 | score |
| emfra_item12_score | 悲伤 | score |
| emfra_item15_score | 生活满意度 | score |
| emfra_item19_score | 社交娱乐活动 | score |

原始数据列名 `EMFRA_itemN_trait` 可作别名；不接受 `_reverse`、`_retest` 或
`Handgrip_mean` 等原始连续测量列来替代本次原始条目分数。
两因子都用全部九项：自主性只反向第 5 项；心理困扰反向第 1、6、15、19 项。

权重已随技能固定，运行不联网。不得让用户寻找补充表、研究数据库、R 环境或 PDF。
方法、来源和复现范围见 [产品合同](references/contract.md)、[证据核对](references/claims.md)
及 [权重原表摘录](references/scoring.md)。

成功时输出 `out/report.md` 与 `out/result.json`；分数按论文要求仅显示两位小数。
输入缺失、单位错误、非整数、超范围或人群不符时退出码为 3，输出 `out/problems.json`，
结果值为 null，报告说明缺什么或哪里不对。复用输出目录时会覆盖上一份结果。

报告开头保留论文卡片，分别解释两个分数的方向。不得求总分、分正常异常、输出风险概率、
把相关性当作治疗收益或用 SEM/MDC 判定个人改善。该量表未支持个人变化监测，故不提供
`--targets`、敏感度排序或目标优化。

每份报告必须保留：

> 边界：预印本，未经同行评审；仅按 EMFRA 九项原始条目分数计算两个独立因子，不计算总分，不作诊断、临床分档、个人变化判定或治疗建议，不据此开始或停止药物。
