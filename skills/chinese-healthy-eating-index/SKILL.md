---
name: chinese-healthy-eating-index
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the 2017 Chinese Healthy Eating Index (CHEI) from confirmed daily
  standard portions and nutrient intake, with 17 component scores and a total. Use for
  中国健康膳食指数、CHEI、饮食质量评分 or comparing the same person's dietary records. Requires age, sex,
  pregnancy/lactation status and complete intake data; supports user-supplied targets.
---

# 中国健康膳食指数 CHEI

按 Yuan 等，Nutrients 2017（DOI: 10.3390/nu9090977）计算，固定对应《中国居民膳食指南（2016）》。

```bash
python3 scripts/personal_report.py --intake intake.csv --age 40 --sex female --out out
```

用户提供自己的饮食记录；推荐按研究的连续三天记录整理同一时段的每日平均量。不是将每天分数分别计算后取平均。记录须覆盖在家和外出吃的食物，以及分配到个人的油、盐及调味品。缺项不填零；确认没有摄入才填零。

CSV 表头 `marker,value,unit`。必填项和范围见 `skill.json`；输入范围用于抓录入错误，不是健康目标。

| marker | 内容 | unit |
| --- | --- | --- |
| total_grains_sp_d | 总谷物每日 SP | 1 |
| whole_grains_mixed_beans_sp_d | 全谷物和杂豆每日 SP | 1 |
| tubers_sp_d | 薯类每日 SP | 1 |
| total_vegetables_sp_d | 总蔬菜每日 SP，包含深色蔬菜 | 1 |
| dark_vegetables_sp_d | 深色蔬菜每日 SP | 1 |
| fruits_sp_d | 水果每日 SP，核对原文新鲜水果口径 | 1 |
| dairy_sp_d | 奶类每日 SP | 1 |
| soybeans_sp_d | 大豆及制品每日 SP | 1 |
| fish_seafood_sp_d | 鱼和水产品每日 SP | 1 |
| poultry_sp_d | 禽肉每日 SP | 1 |
| eggs_sp_d | 蛋类每日 SP | 1 |
| seeds_nuts_sp_d | 种子和坚果每日 SP | 1 |
| red_meat_sp_d | 红肉每日 SP | 1 |
| cooking_oils_g_d | 烹调植物油及动物脂肪每日克数 | g/d |
| sodium_g_d | 食盐及高钠食品中的钠每日克数，不是食盐重量 | g/d |
| added_sugars_energy_pct | 添加糖占总能量百分比，不是总糖 | % |
| alcohol_g_d | 纯乙醇每日克数，不是酒液量 | g/d |
| energy_kcal_d | 每日总千卡数，不是千焦数 | 1 |
| pregnant_lactating_yes | 孕期或哺乳期=1，否或不适用=0 | 1 |

`1` 是数值计数的机器单位；SP/d 和 kcal/d 的意义由键名和说明固定，不能混用。添加糖若是0–1比例，可填单位 `1`，脚本精确乘100。钠若以毫克记录，先精确除1000再填 g/d。其他单位不猜测。

`--age` 为岁，至少2岁；`--sex male|female` 仅用于原论文酒精分组。孕哺期状态必填，不默认“否”。

标准份不等于一碗或一个通用克数。先读 [标准份示例](references/portions.md)，只对表中明确、匹配食品和状态的份量换算。区间不能擅取中点，没列出的食品不能类推。原文的1289种食物完整换算未公布，本技能合同接受已确认的SP记录；只有菜名、照片、普通份数或不能确认换算的克数时，先补全饮食资料，不能声称已算出CHEI。不要让用户找论文、CHNS原始数据、补充材料或代码库。

用户主动提出目标时，加 `--targets targets.csv`（相同表头，可只写改变的饮食项）；不生成目标、不修改年龄性别或孕哺期。输出 `report.md`、`result.json` 和 `levers.json`。目标全部成立和每项单独变化分别计算；食物和能量的联动要同时确认。错误或缺项返回3并写 `problems.json`，不保留旧结果。

报告开头必须保留论文卡片，说明酒精按正文规则、标准份资料有限，以及三日记录和特殊人群的局限。不将队列均分当成个人百分位，不附加“健康/不健康”或疾病风险分档。核对范围见 [方法合同](references/contract.md) 和 [来源核查](references/claims.md)。

每份报告保留：

> 边界：本报告只计算与《中国居民膳食指南（2016）》相符程度，不预测疾病、寿命或干预效果；短期饮食记录不能代表长期饮食。酒精得分不代表安全饮酒量，不据此开始或增加饮酒；不提供药物剂量，也不能据此开始或停止用药。
