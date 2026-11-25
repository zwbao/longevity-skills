---
name: one-minute-heart-rate-recovery
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Calculates the fall from peak exercise heart rate to one minute of active treadmill
  recovery and applies the Cole 1999 primary cutoff. Use when an adult brings an existing
  symptom-limited exercise-test report with both heart rates and a verified recovery protocol, or asks
  what that heart-rate recovery measurement means.
---

# 运动后1分钟心率恢复

读取既有运动试验记录，不安排用户自行进行极量运动试验。

用户命令：

> 用我的运动试验报告算1分钟心率恢复，核对恢复方案，并解释原文分档。

## 输入和运行

从同一次报告取两项实测心率，写成 UTF-8 CSV，表头为 `marker,value,unit`。
字段为 `peak_hr_bpm`（运动峰值）和 `recovery_hr_1min_bpm`（主动恢复第1分钟）。
单位支持 `/min`、`bpm`、`次/分`、`次/分钟`，数值相同。
不要把“HRR1下降量”填进“恢复1分钟心率”，也不要用年龄预测的最大心率。

先从已有报告或检查人员记录核实原文方案：症状限制性跑台试验，峰值运动结束后慢走主动恢复。
具体速度、坡度和时间见 [contract.md](references/contract.md)。核实后才使用 `--protocol cole-1999`。
坐位、卧位、完全静止恢复、其他运动方式、仅有手环自动摘要或方案未知，均不能直接套用。
如缺字段或方案不符，运行后读取 `out/problems.json`，向用户说明需要核对什么，不代填确认。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 57 --protocol cole-1999 --out out
```

将示例年龄替换为用户年龄。`--sex` 可选，不改变结果。
不用向用户索要全文、队列原始数据、补充表、SPECT图像或代码仓库；本方法所需常数已核实。

## 输出

`out/report.md` 用中文呈现论文卡片、差值、分档和限制；`out/result.json` 提供同一结果。
输入缺失、错误、单位不支持或方案不符时退出码为3，输出 `out/problems.json`，结果值均为 null。
重复运行会更新旧结果，成功时清除旧的输入问题文件。

这是原文主切点的读出，不是 Cox 风险预测器。原文次要敏感性分析切点不并入主分档。
不从图形插值死亡风险，不输出人群风险比作为用户的风险，不将改善指标解释为干预获益。
验证为暂定：没有原文个人输入—输出示例；合成测试不是原文复现。

所有报告须原样保留：

> 边界: 本结果仅按原研究的跑台主动恢复方案计算心率下降量与分档，不是个人死亡概率、寿命预测或疾病诊断；不能由此推断提高心率恢复值会降低死亡风险，不能据此开始、停止或调整药物。

出处和材料核查记录见 [claims.md](references/claims.md) 与 [sources.md](references/sources.md)。
