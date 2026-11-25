---
name: strength-training-diabetes-association
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example.
  根据成人每周力量训练总时长，换算队列荟萃分析中糖尿病的线性相对关联和置信区间；提供目标时长时比较目标与当前。适用于询问力量训练时长与糖尿病关联、或比较两个自定时长情景，不用于绝对风险预测或训练处方。
---

# 每周力量训练与糖尿病关联

读取个人每周力量训练总时长，采用 Momma 等，British Journal of Sports Medicine，2022，表 1 的糖尿病线性估计。只需训练日志或回忆问卷，不需要化验、组学或公开研究原始数据。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 45 --targets targets.csv --out out
```

`measurements.csv` 使用 `marker,value,unit` 三列，项目为 `strength_min_week` 或「每周力量训练时长」。值是每周总时长；单位为 min，也接受 h（乘 60）或 s（除 60）。不要把每日时长、训练次数、有氧运动或负重工作混进来。中文别名必须标单位；带单位含义的规范键可省略单位。

`--age` 必填，用于成人适用性核对，不进入计算。`--sex` 可省略；提供时接受 female、male、other、unknown，不改变结果。

只有用户已提供自己的目标时才传 `--targets`，表头和项目相同；没有目标就省略，不替用户选目标。该模式可比较任意两个已提供时长，减少时长时也会正确反转区间端点。

报告首先显示论文卡片，随后输出相对零时长的线性 RR；有目标时增加目标相对当前的 RR。`result.json` 是结构化结果；`levers.json` 给出当前敏感度、目标结果及单项变化。RR 之差不是风险百分点变化。只有一个可改变的输入，因此单项目标与全部目标一致。

缺失、格式错误、错单位、非有限值或超范围会退出 3，输出 `problems.json` 和没有个人计算值的报告；不补零。每次运行清理本工具上次输出，避免误读旧结果。

不要向用户索取论文、附录、回归系数或训练队列。计算常数已在 `scripts/presets.py` 固定，运行不联网。材料及适用范围见 `references/contract.md`、`references/claims.md`。

必须保留以下边界原句：

> 边界: 这是成人观察性队列荟萃分析的群体线性关联换算，不是你的糖尿病发病概率、因果效果或训练处方。论文同时观察到非线性关系，不能据此推断训练越多越好；不能据此开始、停止或调整药物。

不得输出最佳时长、运动强度、频率或药物剂量。输入上限只做错误检查，不代表论文支持在整个输入范围外推；所有结果都要保留非线性关系的说明。
