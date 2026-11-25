---
name: medas-mediterranean-diet-adherence
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the original 2011 MEDAS Mediterranean diet adherence score from
  fourteen personal dietary questionnaire answers, with item scores and user-specified target
  comparisons. Use for MEDAS、地中海饮食评分、饮食依从性问卷 or repeated adherence measurements. Preserves the
  original food definitions and reports in Chinese; does not estimate personal cardiovascular risk.
---

# MEDAS 地中海饮食依从性

按 Schröder 等发表于 The Journal of Nutrition（2011）的 Table 2 计算。用户提供自己日常饮食的 14 项回答，技能计算每项 0/1 分和总分。完整规则已随技能保存，运行时不联网。

用户命令：“用我的14项饮食回答算原版MEDAS，列出每项得分和总分。”

执行：

```bash
python3 scripts/personal_report.py --measurements my_medas.csv --out out
```

CSV/TSV 表头为 `item,value,unit`。`unit` 填 `1`，表示题目指定周期内的计数或是/否编码；数值不是得分。中文项目名、英文别名和规范键在 `skill.json` 中。示例：

```csv
item,value,unit
olive_oil_main_yes,1,1
olive_oil_tbsp_day,4,1
vegetables_servings_day,2,1
fruit_pieces_day,3,1
red_meat_servings_day,1,1
butter_margarine_cream_servings_day,1,1
sweet_carbonated_drinks_cups_day,1,1
wine_cups_week,7,1
pulses_servings_week,3,1
fish_seafood_servings_week,3,1
commercial_pastry_times_week,2,1
nuts_servings_week,3,1
white_meat_preferred_yes,1,1
sofrito_times_week,2,1
```

这是表中边界输入的技术示例，不是一份推荐食谱或真人记录。

## 收集回答

| 键 | 原问卷的计数方式 |
| --- | --- |
| olive_oil_main_yes | 橄榄油是否为主要烹调用油；是=1，否=0 |
| olive_oil_tbsp_day | 每天橄榄油汤匙数，含烹调、沙拉和外食；每汤匙13.5 g |
| vegetables_servings_day | 每天蔬菜份数；每完整份200 g，配菜按半份计入 |
| fruit_pieces_day | 每天水果个数，原题包含鲜榨果汁；无统一果汁毫升换算 |
| red_meat_servings_day | 每天红肉、汉堡、香肠合计份数；每份100–150 g |
| butter_margarine_cream_servings_day | 每天黄油、人造黄油、奶油合计份数；每份12 g |
| sweet_carbonated_drinks_cups_day | 每天碳酸和/或含糖饮料杯数；按正文每杯100 mL |
| wine_cups_week | 每周葡萄酒杯数；按Table 2每杯100 mL，不折算其他酒 |
| pulses_servings_week | 每周豆类份数；每份150 g |
| fish_seafood_servings_week | 每周鱼/海鲜份数；鱼100–150 g，海鲜4–5个或200 g |
| commercial_pastry_times_week | 每周商业制作、非自制的饼干或蛋糕等次数 |
| nuts_servings_week | 每周坚果份数；每份30 g |
| white_meat_preferred_yes | 是否更偏好鸡、火鸡、兔肉而非牛肉、猪肉、汉堡、香肠；是=1，否=0 |
| sofrito_times_week | 每周食用配有橄榄油炒制番茄、蒜、洋葱或韭葱酱汁的菜肴次数 |

各题按同一段日常饮食习惯回答；论文未规定统一回顾天数，不自行宣称为某个固定回顾窗口。每天和每周不要混填，可使用小数表示平均频次。果汁及不明确的份量必须先向本人核实问卷回答，不能取区间中点、猜果汁杯量或把未知当零。配菜半份作用于蔬菜摄入量，不产生半分。

采用 Table 2 原题，含碳酸和/或含糖饮料；葡萄酒题正文写红葡萄酒而表格写葡萄酒，此差异记录在合同中。不要加入后续版本的糕点、坚果阈值或“必须一份生蔬菜”等额外条件。

## 参数与结果

- `--age`、`--sex` 可选，不参与计分；年龄用于提示是否超出正文的55–80岁范围，性别接受`male`或`female`。
- 用户自己给出目标时加 `--targets targets.csv`，列同输入表，只列要改变的项目。脚本写出各项目跨越计分条件的离散敏感度、单项目变化和全部目标同时成立时的分数。不要自动生成目标，尤其不得为了得分建议饮酒。
- 成功输出中文 `out/report.md`、逐项及总分 `out/result.json`、`out/levers.json`。
- 缺项、单位错误、异常范围、非数值或非法二元回答时退出3，并写 `out/problems.json`；报告开头仍有论文卡片，不给部分总分。

不要向用户索要论文PDF、FFQ、补充表、队列数据或代码。问卷是可直接提供的个人数据；规则已核对原文 Table 2，并非依赖未公开模型权重。

报告必须保留原句：

> 边界：本报告只按该论文的问卷规则计算饮食依从性，不诊断疾病、不预测个人冠心病风险或寿命，不据此开始或停止药物。酒类得分仅用于忠实记录原量表，不建议为了得分开始或增加饮酒。

不从本文回归系数推算个人疾病风险或减重效果，不把两种问卷间的人群误差当作这个人的误差条，不添加本文未印的总分分档。

来源、完整定义、可复现范围和材料访问记录见 [references/contract.md](references/contract.md)；研究证据边界见 [references/claims.md](references/claims.md)。
