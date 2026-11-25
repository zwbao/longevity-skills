---
name: alcohol-consumption-thresholds
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Maps a person's reported weekly ethanol mass to the published alcohol-consumption
  categories in Wood et al. (Lancet 2018), converts grams to UK alcohol units, and describes the
  corresponding population life-expectancy differences at age 40. Use when a current drinker asks how
  their weekly alcohol amount compares with this study. Does not estimate personal survival or a safe
  drinking allowance.
---

# 每周饮酒量的研究分档

将用户通常一周的**纯乙醇总质量**放入原文四档。需要三行个人信息：

| marker | value | unit |
|---|---|---|
| alcohol_g_week | 用户一周纯乙醇总质量 | g |
| current_drinker | 1=当前饮酒，0=不饮酒 | 1 |
| cvd_history | 1=有既往心血管病，0=无 | 1 |

单位列 `g` 表示固定一周内的总质量，`kg` 按1000换算。不能把杯数、饮料毫升、饮料质量或每日摄入量直接放进这个字段；不确定时先澄清用户记录，不猜杯量、酒精浓度或乙醇密度。病史未知时先补充，不能按0处理。范围0–3500克是宽松输入防错范围，不是安全范围。

运行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

如用户自己提出另一个一周纯酒精总量，在同样三列表格中只保留 `alcohol_g_week` 一行，通过 `--targets targets.csv` 比较档位。脚本写 `out/levers.json`；不把分档寿命差相减为个人获益，不推荐目标数值。

无需年龄和性别来匹配已发表的合并分档；40岁是论文研究结果的固定起算年龄，不能替换成用户年龄。非当前饮酒者、周总量为零或有既往心血管病时，结果注明不适用主要人群，不输出分档寿命差。输入不是当前习惯（例如已经戒酒前的记录）时不能作为当前量运行。

脚本使用 `skillkit` 处理别名、质量换算和输入校验。缺项、单位错误、数值错误或病史标记不是0/1时退出3，写 `out/problems.json`。正常时写中文 `out/report.md`、`out/result.json` 和 `out/levers.json`。

不要向用户索取论文、附录、原始队列数据、CDC死亡率或Stata程序。这里已冻结所需的切点和单位常数；细节见 [产品合同](references/contract.md) 和 [来源核查](references/claims.md)。

报告必须以论文卡片起始，保留研究结果的群体属性。约6个月、1–2年、4–5年是论文近似描述，不是个人预测或置信区间。“参照档”不能写成“安全”“推荐”“最佳饮酒量”或“没有风险”。不推导任意年龄、性别或每克酒精的寿命变化，不计算心血管绝对风险。

每份报告原样保留：

> 边界：这是高收入国家当前饮酒且无既往心血管病人群的观察性关联；约100克/周不是安全线或建议摄入量，不支持不饮酒者开始饮酒。40岁寿命差是研究人群的模型估计，不是你的寿命损失，也不是改变饮酒量能获得的寿命收益；不据此开始、停止或调整药物。
