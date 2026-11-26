---
name: mini-mental-state
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. 汇总施测者已记录的原版 Mini-Mental State（MMSE）各项得分，生成中文小计与总分报告。适用于用户提供完整 MMSE
  分项记录并要求核算分数；不自动施测、不判读作答，也不作痴呆诊断。
---

# MMSE 得分汇总

按 Folstein 等发表于 Journal of Psychiatric Research（1975）的原版计分规则，核算一次已完成的施测。

用户命令：

> 帮我核算这份 MMSE 分项记录，生成中文得分报告。

读取用户自己的完整分项得分，不向用户索取论文、补充表、数据库或研究人群数据。只有总分时不能反推分项。量表的中文名称只是输入标签，不是经验证的中文施测版本。

运行：

```bash
python3 scripts/personal_report.py --measurements my_mmse.csv --out out
```

CSV/TSV 表头为 `marker,value,unit`，项目键与别名见 `skill.json`。得分单位为 `score`，均为整数。无需年龄或性别参数：本方法没有相应的校正方程。

| marker | 内容 | 范围 |
|---|---|---|
| time_orientation_score | 时间定向 | 0–5 |
| place_orientation_score | 地点定向 | 0–5 |
| registration_score | 首次即刻记忆 | 0–3 |
| attention_score | 一个注意任务 | 0–5 |
| recall_score | 延迟回忆 | 0–3 |
| naming_score | 命名 | 0–2 |
| repetition_score | 复述 | 0–1 |
| command_score | 三步指令 | 0–3 |
| reading_score | 阅读执行 | 0–1 |
| writing_score | 书写 | 0–1 |
| copying_score | 图形复制 | 0–1 |
| registration_learned | 施测者确认记忆材料全部学会 | 0 或 1，单位 `1` |

`registration_learned=1` 表示在原文允许的学习尝试内全部学会；未学会为 0，未知则留缺。后两种情况均不生成总分。这个标志不是得分。后续学习成功也不能将首次即刻记忆得分改为满分。

注意任务采用施测者按原文选定的一项，不把两个任务相加或取较高者。未施测、视听或运动条件导致无法判断、语言版本不相容时，不用零分代替缺项。原文题目及施测材料应由施测者获取和使用；本目录不提供整套问卷或聊天自测。

正常输出 `out/report.md` 与 `out/result.json`。输入问题退出 3，并写 `out/problems.json` 和带论文卡片的说明报告；不保留旧结果。报告必须先呈现论文卡片，再呈现个人得分，保留以下原句：

> 边界: 本报告只汇总已完成施测的认知得分，不能据此诊断或排除痴呆、判断民事行为能力，也不能据此开始或停止药物。

只计算两个小计和总分。不加后来常用的分档、教育校正或患病概率，不把分数提高解释为治疗目标，因此没有 `--targets`。满分端点复现的范围见 `references/contract.md`；研究样本及来源核查见 `references/claims.md`。
