---
name: mifflin-st-jeor-ree
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Estimates resting energy expenditure from weight, height, age, and sex using the
  original and simplified Mifflin–St Jeor equations. Use when a healthy adult asks about resting
  calorie expenditure, the Mifflin equation, or how a self-selected weight scenario changes the
  equation's estimate. Reports in Chinese and distinguishes REE from total daily energy needs.
---

# Mifflin–St Jeor 静息能量消耗

用 Mifflin 等发表于 The American Journal of Clinical Nutrition（1990）的方程3及方程7、8，输出静息能量消耗原式与简化式估计，单位 kcal/d。不是生物年龄或寿命模型。

用户命令：

> 用我的体重、身高、年龄和性别，按 Mifflin–St Jeor 方程估算静息能量消耗；如果我提供体重目标，再显示代入后的变化。

收集当前实测体重、身高、年龄和论文方程使用的性别。不要用理想体重、调整体重、默认年龄或推断的性别补缺项。原文仅有 male/female 两类系数；无法对应时说明本方法不能计算。数据类型为家用测量，无需化验或组学数据。

将个人数据整理为 CSV/TSV，表头 `marker,value,unit`。项目可用 `weight_kg`、`height_cm` 或清单中的中英文别名。体重接受 kg/g/lb；身高接受 cm/m/mm/in。别名填写必须带单位；规范键本身表示单位。年龄使用年，可有小数。

运行 `scripts/personal_report.py`，传 `--measurements <个人表格>`、`--age <年龄>`、`--sex male|female`、`--out <输出目录>`。脚本只用Python标准库。总体年龄只接受19–78岁；女性20–76岁之外以及超过原研究分性别身高体重范围会在报告提示外推。输入合理范围只用于发现填写错误，不等于模型验证范围。

只有用户已给出体重情景时才传 `--targets <目标表格>`，表头相同，只接受体重。不得自行推荐体重或热量目标。`levers.json` 始终提供原式及简化式的输入敏感度；提供目标时另列同时及单项代入结果。年龄、身高、性别不是可改变目标。

正常输出 `report.md`、`result.json`、`levers.json`。输入缺失、单位错误、超范围、目标不受支持时退出3，生成 `problems.json` 和带论文卡片的错误报告；不显示旧结果。按问题文件说明缺什么测量，不代填。

不得要求用户寻找论文、补充表、公开数据或代码。系数已冻结在 `scripts/presets.py`，日常运行不联网。出处、表格核对及访问局限见 `references/contract.md` 与 `references/claims.md`。

报告必须以论文卡片开篇。群体均值复现不是个人准确度验证；不要将研究R²解释为个人预测误差。不要乘活动系数、计算减肥热量缺口或给药物剂量。

报告必须保留以下原句：

> 边界：本结果是健康成人静息能量消耗的统计估计，不是实测值、每日总能量消耗或饮食热量处方；不能用于判断代谢疾病、减重效果或寿命，也不能据此开始或停止药物。
