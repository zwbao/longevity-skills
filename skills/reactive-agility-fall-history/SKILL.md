---
name: reactive-agility-fall-history
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Compares one older adult's own SKILLCOURT results (Random Star Run reactive agility
  completion time, simple and choice stepping reaction times) with the exploratory cutoffs printed by
  Giesche et al. (GeroScience 2026, community-dwelling adults aged 60 and over in Germany and
  Luxembourg): 28.6 s, 0.62 s and 0.88 s, and says on which side of each cutoff the person falls. Use
  for SKILLCOURT, Random Star Run, 随机星形跑, 反应敏捷, 踏步反应时, 老人跌倒, 跌倒史, 跌倒风险筛查. States that the cutoffs
  separate people with and without a past-year fall in a cross-sectional sample, are not a personal
  fall probability or a prediction, and apply only to SKILLCOURT results.
---

# SKILLCOURT 反应敏捷成绩与跌倒史切点对照

用户交自己在 SKILLCOURT 设备上测得的成绩，至少一项：随机星形跑完成时间、简单踏步反应时间、选择踏步反应时间（秒）。年龄可选。不要向用户要论文、PDF 或补充表，切点已经在技能里。没有 SKILLCOURT 成绩时直接说明这个技能用不上；不要拿起立行走（TUG）、坐着按键的电脑反应时或别的敏捷测试代替。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements skillcourt.csv --age 72 --out out
```

`skillcourt.csv` 的列是 `item,value,unit`：

- 随机星形跑（Random Star Run、RSR）：3 次取最快一次的总完成时间，s，也接受 ms。
- 简单踏步反应时间（SKILLCOURT SRT）、选择踏步反应时间（SKILLCOURT CRT）：30 次平均，s，也接受 ms。
- 其他叫法见 `skill.json`。

报告给出每一项相对论文切点（28.6、0.62、0.88 秒）落在哪一侧，以及该切点在论文人群里的 AUC（随机星形跑另有灵敏度 55%、特异度 76%）。一项都没有、单位不认识、数值超出范围（例如把毫秒写成秒）时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `random_star_run_side`、`simple_reaction_side`、`choice_reaction_side` 和 `tests_at_or_above_cutoff`。

## 报告里必须保留的话

- 切点来自一次性测量的横断面比较（过去 12 个月自报有没有跌倒），论文称为探索性切点；落在哪一侧不是个人跌倒概率，也不预测将来是否跌倒。
- 只适用于按论文流程在 SKILLCOURT 上测得的成绩。
- 近期跌过倒、走路不稳或担心跌倒时，建议找医生或康复治疗师做跌倒风险评估；不写诊断，不提用药增减。

引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)，论文与补充材料见 [references/claims.md](references/claims.md)。
