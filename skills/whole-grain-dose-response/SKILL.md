---
name: whole-grain-dose-response
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example.
  按个人日均全谷物食品摄入量匹配人体队列荟萃分析中的群体相对风险及置信区间。当用户询问全谷物摄入与心血管疾病、癌症死亡或全因死亡的关系，或希望比较自己提供的摄入情景时使用。保留原表参照量与各结局的支持范围，不把群体关联解释为个人死亡概率。
---

# 全谷物摄入量与群体相对风险查表

用户命令：

> 用我的饮食记录 intake.csv，把每日全谷物食品摄入量放到论文查表中，生成中文报告；如果我提供 targets.csv，也比较那个摄入情景。

运行：

```bash
python3 scripts/personal_report.py --measurements intake.csv --out out
```

CSV 表头为 `marker,value,unit`。例如一行 `全谷物食品摄入量,90,g/d`；这是论文验证用输入，不是推荐摄入量。只接受 `g/d`，精确换算系数为 1。用日均全谷物食品/产品重量；先核实记录是否为该口径。纯全谷物原料干重、膳食纤维克数、生熟重量和不确定的“份”均不能直接混用或自行转换。不要从包装“全谷物百分比”反推本文统一暴露量，研究中的定义并不一致。

用户已提供目标情景时加 `--targets targets.csv`，格式相同；不自行设置目标。`--age`、`--sex` 仅为调用兼容参数，不参与计算，也不会产生年龄或性别分层结论。

技能自带从附录1 S13、S14 提取的 144 行数值；不要向用户索要论文、补充表、模型系数或研究队列。运行只使用标准库，无需联网。缺失、错单位、无效或超出合理范围的输入会退出 3，写出 `out/problems.json`，不计算结果。

输出 `out/report.md`、`out/result.json`、`out/levers.json`。报告先放论文卡片，再放输入和原表行。精确点返回原表 RR 与 95% CI；非精确点返回相邻摄入量对应的两行，绝不把两行当作个人风险区间。不同结局的可查范围不同，超出时明确留空，不夹到边界、不插值、不外推。参照行未印的置信区间保留空值。

S13 冠心病、卒中、心血管病属于发病或死亡合并结局；“Total cancer”按正文标为癌症死亡。S14 前四项以 4.8 g/日为参照，其余六项以 0 g/日为参照。输出中的 `lower`、`upper` 指较低、较高的原表摄入量，不是风险大小或个人置信区间。

目标比较只在当前与目标均为精确表点时提供同一结局的 RR 差值，其余差值为 null，同时保留相邻行供阅读。无连续曲线系数，不提供梯度；`sensitivity` 为空。这不是个人获益或饮食处方。

每份报告必须保留：

> 边界：这是前瞻性队列荟萃分析的群体关联查表，不是个人死亡概率、寿命预测或增加摄入后的因果收益；不能据此开始或停止药物，也不提供用药剂量或饮食处方。

方法、来源、支持范围与核对记录见 [references/contract.md](references/contract.md)、[references/claims.md](references/claims.md)、[references/sources.md](references/sources.md)。
