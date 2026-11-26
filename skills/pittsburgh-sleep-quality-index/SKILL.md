---
name: pittsburgh-sleep-quality-index
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the original Pittsburgh Sleep Quality Index (PSQI) components, global
  score and sleep-quality screening category from a person's past-month questionnaire responses. Use
  for 匹兹堡睡眠质量指数、PSQI、睡眠质量评分 or monthly sleep questionnaire interpretation. Stops on missing answers
  and ambiguous printed scoring boundaries.
---

# PSQI 匹兹堡睡眠质量指数

用 Buysse 等发表于 Psychiatry research（1989）的原版方法读取过去一个月的问卷回答，输出七个分量、总分和是否超过论文筛查切点。

```bash
python3 scripts/personal_report.py --measurements my_psqi.csv --out out
```

CSV 列名是 `marker,value,unit`。可追加 `--age`（岁）和 `--sex`（男/女/其他/未知或英文），仅作上下文，不改变计分。输出 `out/report.md`、`out/result.json`；无法计分时退出码 3 并写 `out/problems.json`，告知缺哪项、哪行单位错误或哪里存在来源歧义。

使用用户已经填写的[官方问卷](https://www.sleep.pitt.edu/psqi)。不要拿手环、昨晚或近一周数据代替月度自评。中文字段是数据映射，不是经过验证的中文量表；翻译问卷按官方指向的 MAPI 版本取得。仓库不再分发完整问卷或论文，个人以外的部署应核对官方使用条件。

## 输入

全部采用原论文题号。部分其他版本把质量题移到 Q9，不可只按题号直接混用；先核对问题含义。

| 字段 | 内容 | 单位与编码 |
|---|---|---|
| bedtime_min、rise_time_min | Q1、Q3 通常上床及起床时刻 | 自午夜起整数分钟，min；23:00填1380、07:00填420，不能填23、7或23.30 |
| sleep_latency_min | Q2 通常多久入睡 | 整数min；也接受s和h精确换算 |
| sleep_duration_h | Q4 通常实际睡多久 | h；接受min换算，不能填卧床时长 |
| q5a_code 至 q5j_code | Q5十项睡眠干扰的原回答 | score；按原四个选项顺序编码0–3 |
| q6_code | 主观质量 | score；原四档依次0–3 |
| q7_code | 助眠药频度 | score；原四档依次0–3 |
| q8_code | 白天清醒困难频度 | score；原四档依次0–3 |
| q9_code | 做事精力困难程度 | score；原四档依次0–3 |

频度编码是选项顺序，不是每周的实际次数。Q5j没有其他原因时明确填0；空白仍为缺失。同伴情况及同伴观察题不进入计分，不要求提供。禁止向用户索要论文、队列数据、代码仓库或补充表。

## 原文歧义与报告

原附录在恰好6小时有重叠，效率(74,75)%及(84,85]%有空档，未印出舍入办法。脚本停止这些输入，不自动改成其他常见版本；保留真实回答，说明需要计分人员核对版本。这些不是异常睡眠值。详情见 [contract.md](references/contract.md)。

总分越高表示自评困难越多。严格大于5提示睡眠质量较差；等于5不超过切点，也不排除疾病。报告以论文卡片开始，不把样本敏感度或特异度当成个人患病概率。不生成药物目标、不把分数降低解释为延寿。

每份报告保留：

> 边界: 本结果只描述过去一个月的自评睡眠质量，不能诊断失眠或其他疾病，不能换算生物年龄、寿命或死亡风险；不能据此开始、调整或停止药物。
