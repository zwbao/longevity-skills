---
name: handgrip-asymmetry-weakness-transitions
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Classifies one person's two handgrip measurements (left and right hand, about two years
  apart) with the cut points of Xu et al. (GeroScience 2026, China Health and Retirement Longitudinal
  Study 2011-2013, adults aged 45 and over): handgrip asymmetry (non-dominant/dominant ratio below
  0.90 or above 1.10) and low handgrip strength (AWGS 2025: men 34/28 kg, women 20/18 kg, under/over
  65), each as normal at both, newly abnormal, normalized, or abnormal at both; then reports the
  printed all-cause mortality hazard ratios for those patterns and the Wave 2 joint score. Use for 握力,
  握力不对称, 两手力气不一样, 握力下降, 肌少症, 肌肉健康, 死亡风险. States that hazard ratios are population associations, not a
  personal death probability, and does not diagnose sarcopenia.
---

# 两次握力：左右不对称和握力低的变化模式（CHARLS 队列）

用户交自己前后两次测的左右手握力（每只手测两次取最高），加上第二次测量时的年龄、性别和惯用手。不要向用户要论文或 PDF，切点和风险比已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements grip.csv --age 68 --sex 男 --dominant-hand 右手 --out out
```

`grip.csv` 的列是 `item,value,unit`：

- 必填：第一次左手握力、第一次右手握力、第二次左手握力、第二次右手握力，单位写 kg 或 lb（必须写单位）。
- 可选：第一次测量时年龄（a；不填时第一次的切点按第二次的年龄段取）、第一次体质指数和第二次体质指数（kg/m^2；两次都给才算相对握力下降）。
- `--chronic-conditions N`（可选）：心血管病、高血压、血脂异常、糖尿病、癌症、慢性肺病里确诊了几种，给了就另外列出补充表 S12 的分层风险比。

报告给出两次的左右握力比和最大握力、两种异常各自的四种模式（两次都正常、第二次新出现异常、第二次恢复正常、两次都异常）、第二次的联合异常分（0–2），以及论文表 2 里对应的全因死亡风险比和置信区间；还给出不对称指数变化和相对握力下降在论文人群里的百分位位置。

缺握力、性别、惯用手或年龄，单位不认识，握力超出 1–100 kg，或第一次年龄大于第二次时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `grip_ratio_w1`、`grip_ratio_w2`、`hgsa_pattern`、`hgsa_pattern_hr`、`max_grip_w1_kg`、`max_grip_w2_kg`、`lhgs_pattern`、`lhgs_pattern_hr`、`joint_score_w2`、`joint_score_hr`、`delta_aai`、`loss_rgs`。

## 报告里必须保留的话

- 风险比是论文人群（中国 45 岁及以上，两次测量间隔约 2 年，随访约 5 年）里该模式相对参照组的关联，不是个人死亡概率或预期寿命，也不能说明因果；置信区间跨过 1 的组没有统计学差异。
- 两手一样时，左右握力比用弱手 ÷ 强手（论文敏感性分析的定义），这一点论文主分析没写。
- 不写诊断，不给药物或剂量建议；握力明显下降或两手差别大时，建议请医生评估。

验证状态是草稿：论文没有印出个人算例，测试只核对分型和查表。引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
