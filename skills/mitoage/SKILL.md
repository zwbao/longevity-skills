---
name: mitoage
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Computes the published MitoAge linear proteomic score from 25 prepared SomaScan 1.3K
  natural-log RFU measurements and sex. Use when someone has matching plasma proteomics and asks about
  MitoAge or a mitochondrial-health-related protein score. Reports a Chinese paper card, the
  uncalibrated score and optional target scenarios; does not report an age in years.
---

# MitoAge

使用者提供本人的25项蛋白数据和论文使用的性别类别；年龄可选，仅作适用范围提示。公开系数已随技能冻结，不要求使用者寻找论文、补充表、代码或队列。

```bash
python3 scripts/personal_report.py --measurements my_proteins.csv --sex female --age 54 --preprocessing somascan-1.3k-ln-qc --out out
```

- 表头为 `marker,value,unit`。`marker` 使用 `skill.json` 的键、名称、SeqId或SomaId，`value` 为 **自然对数RFU**，`unit` 为 `1`（无量纲）。每项蛋白都必须齐全。
- 数据应来自SomaScan 1.3K对应SeqId并完成实验室质控。`--preprocessing` 是对实际数据处理状态的确认，不会帮原始文件完成质控。原始RFU、log2、Olink NPX、质量浓度、z分数均不能直接代入。没有固定换算因子。
- 数据若仍为原始RFU，请先由检测方提供符合论文处理尺度的个人结果；不要仅改单位名，也不要对单人的25项数据作横向z标准化。
- `--sex male` 或 `--sex 男` 采用Table 2的男性项；`female` 或 `女` 为参照。未知性别类别不能用零代替。
- `--age` 可省略；论文样本年龄为22–92岁，超出会提示外推。年龄不是模型预测变量。
- 可加 `--targets targets.csv`，列与测量表相同，只列要改变的蛋白自然对数值。程序输出每项敏感度、每个目标单独变化和全部目标同时达成的数学结果；没有健康目标推荐，也不把性别或年龄当可调目标。

输入错误或缺项时退出码为3，写 `out/problems.json` 和含论文卡片的中文报告，删除旧结果。成功时写 `out/report.md`、`out/result.json`、`out/levers.json`。

## 解读限制

权重来自Supplementary Data 1的 **MitoAge** 工作表，不使用另外两表的回归系数。公式采用Methods所述的自然对数丰度；不重训、不补缺项、不反推中心化参数，不将输出自行指数化。原始线性值可能为负，不截零。

所有计算常数已公开，但没有完整个人输入与对应输出的印出例子。报告必须保留“仍在验证”，不能把程序测试解释成复现论文个人结果。绝对输出尺度尚未核验，不报告实测呼吸率，不换算成岁数、疾病风险、百分位或健康分档。

每份报告保留：

> 边界：MitoAge 仍在验证，是血清作用下细胞呼吸能力相关的研究分值，不是年龄岁数、疾病诊断或干预效果；不能据此开始或停止药物。

细节见 [产品合同](references/contract.md)、[证据核对](references/claims.md) 和 [材料与列名](references/sources.md)。
