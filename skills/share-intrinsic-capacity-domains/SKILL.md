---
name: share-intrinsic-capacity-domains
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates SHARE intrinsic-capacity cognition, locomotion and sensory domain
  scores from personal test results and questionnaire responses, and optionally compares two
  observations. Use for 内在能力分域、认知计分、行走困难、视听自评或两次功能测量变化。 Accepts any complete supported domain;
  excludes vitality, psychological scores and the composite IC score because their published rules are
  incomplete.
---

# SHARE 内在能力分域计分

用户命令：

> 用我的 SHARE 认知测验、行走困难或视听自评算内在能力分域分数；如果有上次同样的测量，也比较变化，不计算完整总分。

## 输入与运行

使用本技能目录下的 `scripts/personal_report.py`，传入 `--measurements measurements.csv --out out`。
CSV 表头为 `item,value,unit`。列名、中文和英文别名见 `skill.json`。

可提供任意一个或多个完整分域；没有提供的分域输出 `null`。部分提供某分域时必须补齐，不用零填缺项。所有测量输入均为整数，单位 `1` 表示计数或类别编码，没有可换算的其他单位：

| 分域 | 必须同时提供的测量 |
|---|---|
| 认知 | 时间定向正确数（0–4）、动物命名有效词数、连续减七正确数（0–5）、十词延迟回忆正确数（0–10） |
| 行动 | 弯腰跪蹲、穿过房间、步行一百米、爬一层楼梯、爬数层楼梯的困难；每项有困难为 1、无困难为 0 |
| 感官 | 远距离视力、阅读视力、听力的 SHARE 五级自评原编码（1 为 excellent，5 为 poor），眼镜和助听器的使用情况（使用为 1、不使用为 0） |

认知必须是相应 SHARE 测验结果，不能用 MoCA、MMSE 或即时词表回忆替换。技能不自行编造词表、改变测试时序或将其他测验换算进来。原始 SHARE 缺失值编码、yes/no 的其他编码不能直接输入；未知、拒答和未测不是 0。动物命名 200 的录入上限只是防错范围，不是论文的评分切点。

可选 `--baseline baseline.csv` 比较上次测量；上次文件须覆盖本次全部分域，使用同一种测验、语言、编码和辅助器具记录方式。输出本次减上次，不年化，不把论文七年平均下降套到个人。可选 `--age`、`--sex` 仅作背景，均不改变计分。

成功生成中文 `out/report.md` 和 `out/result.json`。缺项、单位错误、非整数、未知项目或读文件失败时退出码为 3，生成 `out/problems.json`，所有数值结果为 `null`。根据 problems 告诉用户需补哪些测量，不猜填。

## 输出范围

每个完整分域按表 1 得到逐项分数、原始分和 0–10 标准化分。计算规则和来源在 `scripts/presets.py` 与 `references/contract.md`。

心理分域需要的 CASP 第 25/75 百分位数值未打印；活力分域的 BMI=30 没有定义归属。两者均不计算，不将三个可算分域加总或放大成 0–50 总分。不得向用户索要 CASP 切点、SHARE 全队列、补充表或作者代码；本技能运行无需联网。

这是描述性计分，不是目标优化或风险预测模型，不生成治疗目标或药物建议。感官项对辅助器具的计分不能被解释为应停用眼镜或助听器。

报告从论文卡片开始，保留以下边界句：

> 边界: 这是 SHARE 人群研究中的探索性分域计分，不是 WHO 统一临床量表；不能据此诊断认知障碍、估计寿命或预测个人未来下降，也不能据此开始或停用药物、眼镜或助听器。未计算心理、活力分域和完整 IC 总分。
