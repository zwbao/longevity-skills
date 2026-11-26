---
name: insomnia-severity-index
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the Insomnia Severity Index total and published severity band from
  seven completed self-report item scores covering the last two weeks. Use when a person supplies ISI
  responses or asks to score their insomnia questionnaire. Produces a Chinese report with input checks
  and screening limits.
---

# ISI 失眠严重程度指数

采用 Bastien 等发表于 Sleep medicine（2001）的图1患者自评版。

用户命令：`用我的过去两周ISI七项自评分，计算失眠严重程度指数和分档。`

## 输入与运行

将本人已经完成的七项自评分存为 `marker,value,unit` CSV，单位 `score`。
使用原问卷分数，不从睡眠小时数、手环、病历叙述或群体均分推断回答。
全部项目必须齐全且为0至4整数；不接受仅有总分、1至5编码、家属版或医生版的混填。

| 输入键 | 图1位置 | 项目及方向 |
| --- | --- | --- |
| sleep_onset_score | 1a | 入睡困难，0无至4很重 |
| sleep_maintenance_score | 1b | 睡眠维持困难，0无至4很重 |
| early_awakening_score | 1c | 早醒，0无至4很重 |
| sleep_dissatisfaction_score | 2 | 睡眠满意度，0非常满意至4非常不满意 |
| daily_interference_score | 3 | 日间功能干扰，0无至4非常多 |
| noticeability_score | 4 | 本人认为他人能察觉的生活质量损害，0完全不能至4非常多 |
| sleep_distress_score | 5 | 对睡眠问题的担忧或苦恼，0无至4非常多 |

中文说明用于匹配输入，不声称是经验证或授权的中文量表译本。满意度项不再反向计分。
图1的功能干扰项在可察觉项之前；按语义匹配，不能直接套用其他版本的题号。

```bash
python3 scripts/personal_report.py --measurements isi.csv --out out
```

`--age`（岁）和 `--sex` 可选，仅作背景，不进入计分。
本工具为症状计分器，不是可设置干预目标的风险模型，因此没有 `--targets`。
运行不联网，不向用户索要论文、补充表、睡眠日记、PSG或研究数据。

## 输出与边界

成功写出 `out/report.md` 和 `out/result.json`：七项直接相加得到总分及图1四段解释。
输入缺失或错误时退出3，写 `out/problems.json` 与含论文卡片的中文问题报告，不输出结果。

报告必须先放论文卡片，再给个人结果，并原样保留：

边界: 本结果仅量化过去两周自觉失眠严重程度，分档不等于临床诊断，不能判断失眠病因、个人治疗获益或寿命；不能据此开始、停用或调整药物。

不得给药物剂量，不把低分解释为排除疾病，不把分档当作诊断，不把随访均分当作个人获益。
证据和复现范围见 [references/contract.md](references/contract.md) 与 [references/claims.md](references/claims.md)。
