---
name: frail-scale
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the FRAIL questionnaire total and screening category from fatigue,
  stair and walking difficulty, specified illnesses, and one-year weight change. Use for FRAIL
  scoring, 衰弱问卷, or 衰弱筛查 when personal questionnaire answers and current and prior-year weights are
  available.
---

# FRAIL 衰弱问卷

使用 Morley 等发表于 The journal of nutrition, health & aging（2012）的 AAH 版本。
先向用户收齐自己的回答和两次体重，生成 `marker,value,unit` 表，再运行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

## 输入

每个键一行。问卷回答必须是整数；不知道时保持缺失，不能用 0 代替。
中文题干是对原文的解释性翻译，不声称经过中文量表的语言学验证。

| marker | 应填写的值 | unit |
| --- | --- | --- |
| fatigue_response_code | 过去4周感到疲劳：1一直，2大部分时间，3有些时候，4少部分时间，5从不 | score |
| resistance_difficulty_binary | 独自、不用辅助器具、不休息走上10级台阶有任何困难：1是，0否 | 1 |
| ambulation_difficulty_binary | 独自、不用辅助器具步行数百码有任何困难：1是，0否 | 1 |
| illnesses_count | 医生曾告知患有下列指定疾病的种数，每类最多计一次 | 1 |
| weight_current_kg | 当前穿衣、不穿鞋的体重 | kg |
| weight_year_ago_kg | 一年前穿衣、不穿鞋的体重 | kg |

指定疾病：高血压、糖尿病、癌症（不含轻微皮肤癌）、慢性肺病、心肌梗死、
充血性心力衰竭、心绞痛、哮喘、关节炎、卒中、肾病。
医生分别告知慢性肺病和哮喘时按原表两个类别计，不由助手自行归并。
疾病不明确时先澄清原有诊断，不根据症状推断。

体重也接受 `lb` 和 `g`；非标准键名的体重必须注明单位。不要用半年前体重替代一年前。
不要将疲劳原回答编码与已折算的单项分混用；步行题保留本文“数百码”的表述。
问卷询问日常功能，不要求用户现场尝试爬楼或步行。

`--age`（岁）、`--sex` 可选，仅作上下文。年龄超出本研究基线范围时报告提示证据外推，
年龄、性别均不改变分数。此问卷没有可用于目标优化的因果模型，不提供 `--targets`。

## 报告

读取 `out/report.md` 和 `out/result.json`。报告先放论文卡片，随后列五项得分、
总分、分层以及一年体重下降百分比。计分规则集中在 `scripts/presets.py`。
体重下降等于切点时按正文定义；正文与附录差异见 `references/contract.md`，报告也会说明。

退出码 3 表示输入有问题：读取 `out/problems.json`，向用户说明缺哪项、哪项值或单位错误，
补齐后重跑。输入错误时不报告总分，旧的结果文件会清除。

不要向用户索要论文、附录、AAH 数据、检验指标、SPPB 或公开代码；运行完全离线。
论文的关联分析仅是群体证据，不据此输出个人死亡概率、寿命、治疗收益或药物剂量。
已复现的是附录的疾病计数单项分，不是论文某位参与者的完整记录或死亡预测。

每份报告必须保留：

> 边界: FRAIL 是衰弱筛查问卷，不能单独确诊衰弱、预测个人死亡概率或预期寿命；本研究在美国社区中晚年非裔成年人中验证，其他人群的适用性需另行评估；不能据此开始、停止或调整药物。

出处和材料核查见 `references/claims.md`，输入、输出及实现取舍见 `references/contract.md`。
