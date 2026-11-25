---
name: nut-intake-mortality-contrast
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Converts a person's recorded total-nut intake difference into the all-cause
  mortality association from the published log-linear dose-response model. Use for comparing nut
  intake records or inspecting a user-supplied scenario; reports an association ratio and uncertainty
  without choosing an intake target.
---

# 坚果摄入差的全因死亡线性关联

用法：

```bash
python3 scripts/personal_report.py --measurements intake.csv --out out
```

`intake.csv` 是 `marker,value,unit` 三列表。必填 `nut_intake_g_d`（总坚果摄入量）和
`reference_intake_g_d`（比较基准摄入量），单位均为 `g/d`，中文名称也可用。
填写本人饮食记录中可食部分的日均克数；比较基准可以是本人此前记录，必须明确提供。
不要把一次摄入量、每周克数、食品总重量或花生酱量直接当成这个输入。
坚果概念包括树坚果、巴西坚果和花生；本技能不区分单品，也不计算花生酱的独立效应。
输入检查范围不表示推荐范围、安全上限或已验证范围。

可选 `--age` 与 `--sex` 作为上下文；年龄若提供须为成年人，二者不进入公式。
适用对象是能提供平均摄入记录的成年人；不用于儿童或疾病个体化营养处方。
可选 `--targets targets.csv`，列格式相同，可只填写希望比较的一个输入。
情景必须来自用户，不由 agent 提议或优化。

模型只用论文总坚果的线性结果，计算输入之差对应的相对关联及置信区间。
论文还报告非线性关系；本计算不能解释平台效应，不能按输出排序推荐摄入量。
`validation=reproduced` 仅指印出的单增量换算，未重新拟合荟萃分析。
年龄、性别、体检与用药不增删或重新加权模型结果。

不向用户索要全文、补充材料、原始队列或公开数据库文件。运行时无需联网。
来源、计算合同及非线性表的口径差异见 `references/`。

输出 `out/report.md`（中文、以论文卡片开头）、`out/result.json` 和 `out/levers.json`。
后者包含公式敏感度、逐项情景变化与共同情景结果。
缺失、单位错误或无效输入时退出码为 3，写 `out/problems.json`，报告不提供数值结果。

每份报告必须保留：

边界: 这只是人群观察性研究的线性关联换算，不是你的绝对死亡风险、寿命预测或改变摄入后的因果收益；不能据此决定摄入量，也不能据此开始或停用药物。
