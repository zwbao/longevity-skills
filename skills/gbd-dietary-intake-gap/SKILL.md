---
name: gbd-dietary-intake-gap
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Compares a person's daily food and nutrient records and 24-hour urinary sodium
  with the fifteen printed GBD 2017 dietary reference values. Computes signed intake gaps, reference
  percentages, and positions relative to the reference uncertainty ranges. Use for dietary intake
  comparisons or explicit target scenarios; it does not predict individual disease risk or prescribe a
  diet.
---

# GBD饮食摄入差值

适用于25岁及以上成人，用本人习惯性每日平均记录逐项对照 GBD 2017
参考表（Lancet，2019）。参考表对男女相同，年龄只用于适用范围检查。

```bash
python3 scripts/personal_report.py --measurements intake.csv --age 50 --out out
```

`intake.csv` 使用 `marker,value,unit` 表头。15项都需要，见
[输入合同](references/contract.md) 和 `skill.json`。食物与营养素采用 `g/d`；
Omega-6及反式脂肪用每日总能量的 `%`，也接受无量纲份额 `1`（乘100）。
例如原记录250 mg/d可按明确的SI关系整理为0.250 g/d，并保留原记录；
不要把摄入毫克数直接填入g/d。当前单位注册表不支持mg/d，脚本会拒绝它。

钠必须是完整24小时尿钠排泄质量。不要用膳食钠、盐重、随机尿或尿钠浓度代替。
EPA+DHA不是鱼肉、鱼油总重或ALA；含糖饮料按饮料质量，不是糖质量。
奶与饮料不能假定1 mL = 1 g；食物干重、熟重不自动互换。
习惯性摄入记录的观测天数由记录者说明；论文没有规定个人最低记录天数。

`--sex` 可选，仅为上下文，不改变计算。用户明确提供目标时，可追加
`--targets targets.csv`，列名与摄入表相同，只填要变化的项目。
不主动把论文参考点当成个人目标。输出 `report.md`、`result.json` 和
`levers.json`；后者包含当前比例的逐项敏感度、每个目标单独变化和全部目标
共同变化的结果。没有综合评分、风险权重或食物替代模拟。

缺项、错单位、非有限数、重复冲突、未知项目或超出宽范围时，退出码为3，
输出 `out/problems.json` 和带论文卡片的中文说明，不产生本次数值结果。
应告诉用户具体缺什么或哪行需要核对，不补零、不使用人群均值替代。

不要向用户索要论文、附录、死亡负担、GHDx数据或代码。参考表已经冻结在
`scripts/presets.py`；运行只需标准库且无需联网。本文无独立个人预测代码发布链接。

论文验证仅覆盖全谷物和牛奶的印出比例及表中参考点，容差为0.5个百分点；
并不宣称复现全文人群疾病负担。其他印出比例的舍入差异见
[合同与验证范围](references/contract.md)，材料核查见[来源核查](references/claims.md)。

每份报告开头保留论文卡片，末尾逐字保留：

> 边界: 本报告仅将个人记录与GBD 2017的人群研究参考值作算术对照；不足或超量只表示相对参考点的差值，不诊断营养缺乏，不预测个人患病、死亡风险或寿命，不提供饮食处方、补剂剂量或用药启停建议。参考范围表示模型参考值的不确定性，不是个人安全区间。
