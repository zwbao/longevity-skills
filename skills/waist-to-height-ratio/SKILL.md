---
name: waist-to-height-ratio
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Calculates adult waist-to-height ratio from waist circumference and height, compares it
  with the screening boundary discussed by Ashwell et al. (2012), and evaluates a user-supplied waist
  target. Use for 腰高比、腰围身高比、WHtR or adult abdominal cardiometabolic screening questions.
---

# 成人腰围身高比

用成人的腰围和身高计算无单位比值，报告筛查界值分档。依据 Ashwell 等，Obesity Reviews，2012，DOI: 10.1111/j.1467-789x.2011.00952.x。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 40 --out out
```

测量文件为 CSV 或 TSV，列名 `item,value,unit`，腰围和身高各一行。支持中文、英文别名及带单位的标准键 `waist_cm`、`height_cm`；支持 cm、m、mm、in。普通名称必须写单位，标准键可以省略单位并按厘米读取。年龄必填，用于确认成人适用性，不进入计算。`--sex` 可省略，不改变计算或界值。

用户提供腰围目标时加 `--targets targets.csv`，格式相同，只填腰围。身高保持当前值；目标不是脚本推荐值。每次有效运行生成当前敏感度，提供目标后再生成目标比值和差值。不得将算术变化解释成患病概率下降或干预获益。

缺项、单位错误、超范围或文件不可读时退出码为 3；读取 `out/problems.json` 告诉用户需补测或改正什么。失败报告保留论文卡片，结果为空，不用猜测值补齐。成功时读取 `out/report.md`、`out/result.json`、`out/levers.json`。

不能向用户索要原文、补充表、数据库或代码仓库。本方法无需运行时下载。腰围测量部位应记录并在重复测量中保持一致；论文未规定唯一部位。不要沿用其他方法的肥胖等级、年龄分层或疾病专属切点。本文讨论的通用界值并不是本次荟萃分析重新求得的最优切点。

验证状态仍为草案：没有印出的配套个人输入和输出示例。程序测试只验证单位、分档、错误处理和算术一致性，不得称为已复现论文个人示例。

每份报告保留以下原句：

> 边界: 腰围身高比仅用于成人心代谢风险初筛，不是诊断、个人患病概率或寿命预测；不能据此开始、停止或调整药物。

来源及范围见 [references/contract.md](references/contract.md) 和 [references/claims.md](references/claims.md)。
