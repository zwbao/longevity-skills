---
name: pooled-cohort-ascvd-risk
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes the original Pooled Cohort Equations ten-year risk of a first hard ASCVD
  event from age, sex, explicitly selected population equation, cholesterol, blood pressure,
  treatment, smoking and diabetes. Use for requests about PCE or the 2013 ACC/AHA risk equation and
  user-specified target scenarios. Produces a Chinese report with applicability limits and structured
  input problems.
---

# PCE 十年首次心血管病风险

使用 Goff 等发表于 JACC 2014 的原始 PCE 方程；这是论文方法复现，不是现行指南的治疗决策工具。

## 输入与适用条件

先从用户已有体检及明确陈述整理 CSV，表头 `item,value,unit`。六项必须齐全，未知不能填零：

| 项目 | 方法单位 | 接受范围或含义 |
|---|---|---|
| 总胆固醇 / TC | mg/dL | 130–320；也接受 mmol/L、mg/L |
| HDL-C / 高密度脂蛋白胆固醇 | mg/dL | 20–100；也接受 mmol/L、mg/L |
| 收缩压 / SBP | mmHg | 90–200；也接受 kPa |
| treated / 降压治疗 | 1 | 0=否，1=是；指测量血压时是否接受降压治疗 |
| smoker / 当前吸烟 | 1 | 0=否，1=是；不是累计吸烟量 |
| diabetes / 糖尿病 | 1 | 0=否，1=是；不能根据单次血糖自行诊断 |

年龄限 40–79 岁。`--sex` 为原研究分层 male/female（也接受 m/f、男/女）。`--race` 必须明确选择原研究的 white 或 african_american；不能从语言、姓名、外貌或国籍推断。中国和其他族群不得自动填 white；原文讨论的白人方程替代策略不等于已在该族群校准。

`--eligible yes` 只能在已明确无心血管症状、无心肌梗死、卒中、心衰、冠脉介入或搭桥、房颤史时填写。已有上述情况或资料未知时，不运行首次事件计算。不能替用户确认病史，也不把这个工具用于急性症状判断。

血脂和血压范围来自论文伴随官方 Excel 的输入范围，不是正常值或治疗目标。超范围返回输入问题，不静默外推。

## 一条用户命令

> 用我提供的年龄、性别、明确的方程族群、血脂、血压和三个是否项，按原始 PCE 估计十年首次心血管病风险；如提供目标值，比较同一模型下的变化。

运行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 55 --sex female --race white --eligible yes --out out
```

这条运行示例使用论文的假想人物，不能把其中的参数当作用户事实。可用输入示例：

```csv
item,value,unit
TC,213,mg/dL
HDL-C,50,mg/dL
SBP,120,mmHg
treated,0,1
smoker,0,1
diabetes,0,1
```

可加 `--targets targets.csv`，表头相同，允许任意非空子集：总胆固醇、HDL-C、收缩压、当前吸烟。目标由用户提供，不自动生成。治疗状态、糖尿病、年龄、性别、族群不能作为目标。切换吸烟状态仅是静态方程情景，不模拟戒烟后的时间进程。不得根据 HDL 或其他项的系数方向建议干预。

## 输出和失败处理

- `out/report.md`：中文，论文卡片在个人结果之前，包含输入、方程组、人群限制和边界。
- `out/result.json`：原方程未截断风险百分数、按论文边缘规则显示的风险、方程组；没有治疗风险分档。
- `out/levers.json`：连续输入和年龄的局部敏感度，二值输入的 0→1 对比；可选单项目标和联合目标结果，变化单位是百分点。不可当作因果效应。
- 资料缺失、单位错误、数值异常、适用范围不符或目标错误：退出 3，写 `out/problems.json`，所有结果置空，不输出敏感度。按问题说明向用户补充测量或资料。

风险低于 1% 或超过 30% 时，报告使用 `<1%` 或 `>30%`，避免假精确；机器文件保留未截断值便于审计，不能据此绕过显示警示。模型不包括心衰结局，也不计算终生风险、寿命、治疗获益或开始/停用药物的判断。

## 证据与复现范围

全部系数和基线常数来自表 A，公式来自表 B，随技能冻结在 `scripts/presets.py`。运行只需要标准库，不下载任何材料。禁止向用户索要论文、补充表、队列或官方 Excel。

通过的复现：表 A 白人女性、非裔美国女性和男性；工作组表 9 一例白人女性。白人男性表 A 和工作组表 8/10/11 的已查格值与印刷常数有差异；没有调整系数迎合表格。详见 `references/contract.md`。`validation` 仅列通过的例子，不声称所有公开数值一致。

每份报告必须原样保留：

> 边界: PCE 是原始美国队列的十年首次动脉粥样硬化性心血管病风险模型估计，不是诊断，不代表中国人群已校准的风险；目标值情景不是治疗效果预测，不能据此开始、停止或调整药物。
