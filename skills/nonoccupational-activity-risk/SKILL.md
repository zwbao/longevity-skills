---
name: nonoccupational-activity-risk
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Converts an adult's usual weekly non-occupational activity durations into
  marginal activity volume and looks up population relative risks for mortality, cardiovascular
  disease and cancer from published dose-response curves. Use for questions about weekly leisure
  activity and chronic-disease associations, or comparisons with a person's own activity targets.
  适用于每周非职业活动量与慢病、死亡风险关联查询。
---

# 非职业活动量与人群相对风险

用户命令：

> 用我通常一周的轻、中、高强度非职业活动时长，查这篇研究对应的相对风险；有我自己给出的目标时再比较目标情景。

先确认对象是一般成年人，活动包含休闲活动并排除工作活动、睡眠与静坐。该方法不适用于专门的二三级预防患者、住院或机构人群，也不是康复运动处方。读取年龄仅用于适用范围检查，不参与风险计算。

## 准备输入

将通常一周内互不重叠的轻、中、高强度活动累计时长写为 `marker,value,unit` CSV：

- `light_min_week`：每周轻强度非职业活动时长。
- `moderate_min_week`：每周中等强度非职业活动时长。
- `vigorous_min_week`：每周高强度非职业活动时长。

三项都必须提供。明确没有某类活动时填0；不知道时报告缺项，不能默认为0。单位用 `min`（分钟），也接受 `h`（小时，乘60）或 `s`（秒，除60）；都是每周累计时长。不要重复统计混合活动，不把日均分钟当周累计分钟。不要根据“偶尔运动”猜次数或时长，也不要自行给不明确的活动指定强度。

本方法用论文的代表强度：轻1.5、中3.5、高7.0 mMET。mMET已扣除静息消耗。不能把手环全天总活动、步数、卡路里或未扣静息/职业活动的MET当作上述输入。

## 运行

在本技能目录中执行：

```bash
python3 scripts/personal_report.py --measurements data/example.csv --age 50 --out out
```

换成用户的CSV和年龄。用户自定目标时加 `--targets targets.csv`；目标表沿用相同列与单位，可以只填要改变的活动项，其他项保持当前值。年龄不是可修改目标。不自行生成目标或运动剂量。

输出 `out/report.md`、`out/result.json` 和 `out/levers.json`。输入不全或错误时退出码3，写 `out/problems.json` 和带论文卡片的中文说明，不留下上次计算结果。把问题转告个人助手，说明需要补记什么时长或核对什么单位。

## 如何解释

- 采用作者总人群主分析的最近网格点法，不插值或重拟合。报告给出输入活动量与每个结局实际查询的网格活动量。
- 22个结局分别报告RR和95%置信区间，参照是零非职业活动量。癌症和心血管病“发生”合并致死及非致死事件，与死亡结局分开。乳腺/子宫内膜癌为女性研究，前列腺癌为男性研究；这些行不是对所有人的个人预测。其余结果也未按个人年龄、性别或体检校准。
- 区间跨1的结果不能写为明确保护或有害，各结局不能相加。超过某结局的已发布活动范围时该项为null，不截断到最大值。
- 更高活动量的证据较少，报告保留相应提示。目标比较只是同一曲线两处估计之差，没有个人因果含义，也不计算差值的置信区间。
- `levers.json` 包括每个输入的邻近网格割线敏感度、每个目标单独达成及全部达成时的结果。该敏感度不是阶梯查询函数的导数；小改变可能仍查询同一行。
- 不输出个人绝对风险、寿命、群体潜在影响分数PIF，不以这项结果诊断疾病或决定用药。

不向用户索要作者数据、系数、补充表或R环境。全部所需风险曲线已冻结在 `data/`，运行只用Python标准库。来源与访问限制见 [references/sources.md](references/sources.md)，计算约定见 [references/contract.md](references/contract.md)，原文数值见 [references/table1.md](references/table1.md)。

报告从论文卡片开始（标题之后），并原样保留：

> 边界: 这是一般成年人人群观察研究的活动量—相对风险关联，不是个人患病概率、寿命或改变活动后的因果获益预测；不能据此开始或停止用药，也不构成运动处方。
