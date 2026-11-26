---
name: frax-uk-risk-lookup
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Matches personal age, sex and a single clinical risk factor to the printed 2008
  UK FRAX Table 2 ten-year major osteoporotic and hip fracture probabilities at BMI 25 without BMD.
  Use for a historical UK fracture-probability lookup when age is exactly 50, 60, 70 or 80 and all
  risk-factor answers are known. Rejects unsupported combinations and never interpolates or
  substitutes for the full FRAX calculator.
---

# 英国 FRAX 骨折概率查表

按 Kanis 等发表于 Osteoporosis International（2008）的表2匹配个人输入。先确认适用条件，再运行；不让用户把年龄或BMI改成表中数字。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 80 --sex female --out out
```

测量文件为 `item,value,unit` 三列表。必须提供以下八项，问卷项填0（否）或1（是），单位为`1`；未知留待补充，不能填0。脚本通过skillkit识别清单中的中英文别名和单位。

| item | 内容 | 接受条件 |
|---|---|---|
| bmi_kg_m2 | 体质指数，kg/m² | 恰为25 |
| parental_hip_fracture | 父母髋部骨折史 | 0/1 |
| current_smoking | 目前吸烟 | 0/1 |
| high_alcohol | 已按论文口径确认的高酒精摄入分类 | 0/1 |
| rheumatoid_arthritis | 类风湿关节炎 | 0/1 |
| oral_glucocorticoids | 曾长期口服糖皮质激素的病史 | 0/1 |
| previous_fragility_fracture | 既往脆性骨折 | 0/1 |
| secondary_osteoporosis | 其他继发性骨质疏松 | 必须明确为0 |

年龄只接受50、60、70、80岁，性别为`male`或`female`。六个表列危险因素最多一项为1。表2没有其他继发性骨质疏松的单列，因此拒绝其阳性输入（论文附录说明完整计算器在无骨密度、无类风湿关节炎时对其套用类风湿关节炎系数，但表2未印出此情形，本技能不作替代）。骨密度、T-score、多因素、其他年龄及BMI不在此技能范围，不接受后忽略。

酒精一行印为“>2 units daily”，方法段写平均每日3个及以上单位。本技能接收已确认的二元分类，论文没有在这里给出克数换算，不把“杯”直接等同于“单位”。长期口服糖皮质激素的时长阈值在本文未明确；需病史确认，不按药名猜测，也不输出剂量。

可用`--targets targets.csv`比较用户明确指定的吸烟或酒精分类目标；文件与测量表同列，可只列改变项。联合情景必须仍落在表2范围。`levers.json`列每项输入的可估算分类差或不可估算原因、联合目标值、单项改变值；单项改变超出表格时为空。病史和用药不能设置为目标。表值差不是行为改变的因果获益。

成功输出`report.md`、`result.json`和`levers.json`。缺项、坏单位、非法值和超出查表条件时退出3，输出`problems.json`及带论文卡片的中文说明；概率为空。用户只提供自己的资料，禁止要求用户寻找论文、系数、补充材料或数据集。运行无需联网。

报告开头保留论文卡片，注明2008年英国、固定BMI、无骨密度、原表四舍五入精度；两项结局不能相加。必须原样保留：

边界: 这是2008年英国模型表2在固定BMI和单一危险因素条件下的查表值，不是完整或现行FRAX，也未经中国人群校准；不能据此诊断、决定治疗、开始或停用药物。情景差异不是改变行为后的因果获益。

范围与来源见[合同](references/contract.md)和[证据核查](references/claims.md)。
