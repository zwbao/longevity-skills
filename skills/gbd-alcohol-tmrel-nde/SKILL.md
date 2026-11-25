---
name: gbd-alcohol-tmrel-nde
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Compares a person's mean daily pure ethanol intake with the GBD alcohol
  theoretical minimum risk exposure level (TMREL) and non-drinker equivalence (NDE) printed for their
  age group, sex, region and reference year. Use for drinking-amount comparisons against this
  published population model. Reports historical thresholds, uncertainty intervals and signed
  differences in Chinese; does not estimate individual disease risk or recommend drinking targets.
---

# GBD 酒精摄入人群阈值比较

运行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 50 --sex female --region "East Asia" --year 2020 --out out
```

`measurements.csv` 使用 `item,value,unit` 表头，输入平均每日**纯乙醇**摄入量，单位 `g/d`：

```csv
item,value,unit
ethanol_g_day,10,g/d
```

这只是演示输入，不是饮酒建议。平均量须覆盖全部日历日，而非只平均饮酒日。不要把饮料体积、酒精度百分比、一次饮酒量或各国的“标准杯”直接填入。只有 `ethanol_g_day` 这个带单位键名可省略单位，普通别名必须带 `g/d`。不自行假定每杯大小或换算酒精密度。

年龄限 15–120 岁，15–79 岁按五岁档、80 岁及以上按原表合并档；120 为输入检查上限。性别用 `male/男/m` 或 `female/女/f`。参考年份只允许 1990、2000、2010、2020，省略时取 2020，必须说明是历史参照。

`--region` 为原表的 GBD 地区，可用 `--list-regions` 或 [地区表](references/regions.md) 查看。中国对应 East Asia；不能因为只知道“亚洲”就选东亚，也不能用全球平均替代缺失地区。用户只提供国家时，技能助手查附录 1 的地域映射，不要求用户找附录。

阈值已经冻结在技能里。禁止向用户索要论文 PDF、补充材料、GBD 原始队列或作者的模型文件。缺少个人输入、单位不符、超范围或文件无法读取时，退出码为 3，解释见 `out/problems.json`；不猜测、不补零。

输出为 `out/report.md`、`out/result.json` 及 `out/levers.json`。可另给 `--targets scenario.csv`（同表头和字段），仅比较用户自填情景与固定阈值的差值，不生成目标、不计算风险改善；敏感度只表示摄入量每变化一单位时算术差值的变化。

每份中文报告以论文卡片开头，然后展示输入和参照分层、TMREL/NDE 均值与区间、摄入量减阈值的差值、所在侧、原表页码。`equal_to_printed_mean` 只表示与打印的四舍五入均值相等，不是生物学意义上的等效保证。区间为人群模型阈值的不确定性，不是此人的风险区间。

必须保留边界原句：

> 这是个人摄入量与历史人群模型阈值的比较，不是个人患病概率、安全饮酒量或饮酒目标；不能据此开始或增加饮酒，也不能据此开始或停止药物。模型未区分集中大量饮酒与分散饮酒，未按个人疾病、用药、妊娠或遗传因素调整。

方法、来源与验证见 [合同](references/contract.md)、[证据核对](references/claims.md) 和 [示例](examples.md)。
