---
name: alcohol-mortality-risk-lookup
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example.
  按日均纯乙醇摄入量和饮酒史匹配全因死亡人群相对风险，提供总体或男性、女性分层的完全调整估计及置信区间。用于询问饮酒量与死亡风险关系、低量饮酒是否有保护关联，或比较用户指定的两个饮酒量分档；不估计个人死亡概率或停止饮酒后的风险变化。
---

# 日均饮酒量与全因死亡关联查表

使用 Zhao 等，JAMA Network Open（2023），DOI: 10.1001/jamanetworkopen.2023.6185。
全部计算使用正文表 2、表 4 的 Fully adjusted 列，参照始终为终身不饮酒者。

用户命令：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --sex female --out out
```

测量文件表头为 `item,value,unit`，一行 `ethanol_g_day,25,g/d`。
这是通常日均纯乙醇量，平均时包含不饮酒的日子，不是酒液体积、每个饮酒日的量或单次饮酒量。
接受 `g/d`，换算因子为 1。其他写法需先明确规范为此单位。不能猜测杯量、酒度或用国家标准杯替代用户的真实杯量。
别名行须提供单位；规范键名已含单位时可省略单位。

- `--sex male/female`：用表 4；省略则用表 2 总体。没有其他性别分层，不能猜测。
- `--drinking-status current/former/lifetime_abstainer`：正值通常自动判为 current。零摄入必须说明是既往饮酒、现在完全不饮酒，还是终身不饮酒；不能只凭零值选参照。
- `--age`：可选成人年龄背景，不改变查表值。表 3 的队列中位年龄不能套到个人年龄。
- `--targets`：可选相同格式文件；只比较当前饮酒者的两个正值日均量分档。零摄入目标、从不饮酒者的状态转换不属于本方法的风险预测，返回输入问题说明。不能把停止饮酒后的未来状态视为终身不饮酒。

输入错误或缺失时退出 3，读取 `out/problems.json` 向用户说明需要补充什么。
正常输出 `out/report.md`、`out/result.json`、`out/levers.json`；levers 仅列相邻分档与用户指定情景的表值差，没有连续导数或因果获益。
年龄 18–120 和日均量 0–300 g/d 是工具的输入检查范围，不是论文拟合范围或安全界限；最高分档本身没有上限。

无需向用户索取论文、原始队列、补充 PDF、OSF 或 SAS 文件。已将所需查表值冻结在 `scripts/presets.py`，运行无需联网。

每份报告必须先呈现论文卡片，区分人群关联与个人风险，说明未显著不等于无风险。
既往饮酒者的较高 RR 不能解释为停止饮酒有害。禁止把 RR 最低的档位称作最佳或推荐饮酒量。
报告保留以下原文：

> 边界: 这是观察性队列荟萃分析的人群关联查表，不是个人死亡概率、寿命预测或改变饮酒后的因果效应；未显著不等于无风险，不能据此建议开始饮酒，也不提供药物剂量或启停药建议。

核查范围及来源差异见 `references/contract.md`、`references/claims.md` 和 `references/sources.md`。
