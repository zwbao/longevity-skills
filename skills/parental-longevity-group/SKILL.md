---
name: parental-longevity-group
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Groups a person's parental longevity as high (both parents reached 85), medium (one
  parent) or low (neither) from each parent's age at death or current age, with the cut-off and the
  exclusion rule (a parent who died before 41) printed by Seidu et al. (GeroScience 2026, Gothenburg
  H70 Birth Cohort, 70-year-olds), and restates how that group differed from the low group in the
  cohort. Use for 父母长寿, 父母活到多少岁, 家族长寿, 长寿家族史, parental longevity, parents' age at death. Does not
  compute the polygenic longevity score and does not predict a personal lifespan.
---

# 父母长寿分组（哥德堡 H70 队列）

用户交父亲、母亲各自的年龄：已去世写去世时年龄，在世写目前年龄。性别和本人年龄可选。不要向用户要论文、PDF、基因数据或补充表，分组规则已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements parents.csv --sex female --age 70 --out out
```

`parents.csv` 的列是 `item,value,unit`，每位父母只填一行：

- 父亲去世时年龄 或 父亲目前年龄（岁）
- 母亲去世时年龄 或 母亲目前年龄（岁）
- 名称也认 父亲享年、mother age at death、father current age 等，`skill.json` 列出全部。

报告给出分组（高、中、低）、活到 85 岁的父母人数、父母年龄均值，并转述论文里该组与低组相比的群体差别（只写方向，不写数值）。在世的父母还不到 85 岁时，分组写“未定”，并给出目前至少的分档；有一方父母在 41 岁前去世时，照论文不分组。

缺一方父母的年龄、同一方既填去世年龄又填目前年龄、单位不认识、数值超出范围或性别写错时不计算：报告写明原因，脚本退出码 3。`out/result.json` 给出 `pl_group`、`pl_status`、`pl_group_floor`、`parents_reached_85` 和 `parents_mean_age_a`。

## 报告里必须保留的话

- 分组只是按父母活到的年龄分档；论文里的差别是瑞典 70 岁人群的群体关联，不是个人寿命预测，也不是诊断。
- 不算多基因长寿评分：论文用的位点权重没有公布。
- 不写剂量，不建议开始或停止任何药物；只建议把常规体检项目和医生一起解读。

验证状态是草稿：论文没有印出个人算例，测试只核对分组规则。引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
