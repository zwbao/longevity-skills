---
name: inflammatory-burden-index
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Calculates the inflammatory burden index (IBI) from C-reactive protein and absolute
  neutrophil and lymphocyte counts, and compares it with the paper's exploratory threshold. Use for
  requests about IBI, 炎症负荷指数, or frailty-related inflammation when these laboratory results are
  available. It does not estimate biological age or clinical risk.
---

# 炎症负荷指数

使用 Wang 等，npj Aging 12:163（2026）的 IBI 公式。人体主分析为横断面研究；“髓系细胞适应失败”是待验证假说。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

输入 CSV 表头为 `marker,value,unit`。需要同一次检查的定量 CRP、中性粒细胞绝对计数、淋巴细胞绝对计数；不混用不同日期。CRP 可用 mg/L 或 mg/dL，细胞计数可用 10^9/L、10^3/uL、/uL。常见中文、英文名称和转换见 skill.json。百分比、低于检测限、缺单位或缺项不作猜测。

可选 `--age` 和 `--sex` 仅作背景，不进入公式；年龄小于研究样本下限时报告提示。无需提供年龄、性别也能完成算术读数。

可选 `--targets targets.csv` 使用相同表头，可只提供部分指标，用于用户指定的假设值对照。`out/levers.json` 包含当前公式对每项输入的局部敏感度、各项单独变化和全部指定值同时变化的结果。这些不是建议达到的化验值或治疗效果。

输出 `out/report.md`、`out/result.json` 和 `out/levers.json`。输入不合格时退出 3，输出 `out/problems.json` 及含论文卡片的中文说明；不留下上次的计算结果。

每份报告保留“仍在验证”的提示、切点尺度的不确定性和以下边界句：

> 边界：这是探索性炎症指标及论文切点的算术对照，不是衰弱诊断、衰老速度、个人患病概率或治疗目标；不能据此开始或停止药物，也不提供剂量。

不向用户索取 NHANES、GEO、GWAS 数据、补充材料、分子表达数据或作者源码。本方法运行无需联网；所需公式和切点已冻结在 presets.py。不要把应用中的 FI/POAM 规则、网络药理候选物或人群回归斜率接入本报告。

出处与尺度限制见 [contract.md](references/contract.md)，完整材料核查和研究组别见 [claims.md](references/claims.md)。未找到可独立复现的个体数值示例；测试中的合成输入不能用于声明已复现论文。
