---
name: smoking-burden-of-proof
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. 根据当前吸烟者的每日吸烟支数或累计包年，查询 Burden of Proof
  方法公布的多病种相对风险与不确定区间。适用于询问烟史对应肺癌、慢阻肺、心血管病等疾病关联时；只匹配已发表的暴露点，其他烟史展示相邻参考点，并检查参考年龄与性别限定。
---

# 吸烟烟史与疾病相对风险查表

用户命令：**“按我的吸烟史，查这个疾病在论文里的相对风险。”**

询问当前是否吸烟、实足年龄、关注的疾病及该疾病所需的一种烟史。
按 [结局表](references/outcomes.md) 选择 `--outcome`；不要默认疾病。
仅对乳腺癌、宫颈癌和前列腺癌要求 `--sex`。其余结局不需要性别。

## 输入与运行

从用户自己的烟史建立 CSV（`marker,value,unit`），两种烟史不能互换：

- `pack_years`：累计包年，使用论文或病历中已经明确的包年数，不是吸烟年数。
- `cigarettes_per_day`：平均每日卷烟支数，或已经确认的卷烟当量。

推荐用这些带含义的键，单位列可以留空。明确填单位时，`pack_years` 的机器单位为 `a`（每天一包强度下的等效暴露年），`cigarettes_per_day` 的机器单位为 `1`（每日固定时间窗内的单支计数）。报告始终显示“包年”或“支/日”。不得把包数、实际烟龄或其他烟草支数冒充这些输入；本技能不换算其他烟草产品。

在技能目录运行 `python3 scripts/personal_report.py --measurements smoking.csv --outcome lung_cancer --smoking-status current --age 57 --out out`。
这是调用格式，不是让用户改变真实年龄或烟史。填写其他结局时更换 `--outcome`，所需烟史见结局表。

输入缺项、错单位、超范围、不适用年龄/性别或不是当前吸烟者时，退出码为3，读取 `out/problems.json` 向用户解释。
不要要求用户下载论文、补充材料、作者代码、公开队列或风险曲线；已发表表值随技能冻结，运行不联网。

## 输出解读

- `out/report.md`：中文论文卡片、查表结果与边界。
- `out/result.json`：准确匹配表值时返回RR及95%不确定区间；未匹配时三个值为null。
- `out/lookup.json`：未匹配输入的相邻已发表参考点；这些点不是该人的风险范围。
- `out/levers.json`：离散参考比较；没有局部导数时写null，不能编造敏感度。

5、10、20、40及各结局第85百分位暴露量是表内的点，不是分组切点。不能把区间内的烟史归入最近一档。
心血管结局只在表2的参考年龄内返回结果；不作其他年龄的换算。
骨折为当前吸烟与对照的二元比较，不使用每日支数或包年。

`--targets another_history.csv` 可以比较另一份烟史，使用相同表头与所选结局的同一输入键。只在两处都有已发表RR时计算表值差；不要称为戒烟效果、个人风险减少或行动目标。累计包年无法因戒烟而减少。零暴露的戒烟后预测不受支持。

报告必须原样保留：

> 边界: 这是当前吸烟者对应暴露水平的人群关联，不是个人患病概率、诊断或预期寿命；不能推算减量或戒烟后的获益，也不能据此开始或停止任何药物。

来源核对与范围见 [合同](references/contract.md)、[证据记录](references/claims.md) 和 [材料清单](references/sources.md)。
