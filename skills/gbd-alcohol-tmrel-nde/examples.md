# 使用示例

在技能目录内创建 `measurements.csv`：

```csv
item,value,unit
平均每日纯酒精摄入量,10,g/d
```

运行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 50 --sex female --region "East Asia" --year 2020 --out out
```

摄入量为演示值，不是建议。对应的论文打印值是附录 2 表 S1 东亚、50–54 岁、女性、2020 年：TMREL 0.505（0.400–0.600）、NDE 1.79（1.00–2.50）标准杯/日。报告还将显示输入与均值的算术差值；这些差值不是论文受试者的实测结果或风险变化。

性别改为 male 时，必须使用该行男列：TMREL 0.459（0.400–0.600）、NDE 1.51（0.800–2.30），不能复制女性结果。`--year` 省略时明确标识参照 2020 年，而非当前年份。

只有当用户主动给出比较情景时，才可另写 `scenario.csv` 并添加 `--targets scenario.csv`。系统不从 TMREL 或 NDE 自动生成目标。

错误示例：`平均每日纯酒精摄入量,1,drinks/day` 不知道每杯含多少纯乙醇，退出 3 并写 `problems.json`；不得默认为 10 g。`--year 2026` 不在原表中，也退出 3，不取最近年份代替。

边界：这是人群阈值比较，不能解释为个人安全饮酒量，不能据此开始或增加饮酒，不能据此开始或停止药物。
