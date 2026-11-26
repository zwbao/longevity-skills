---
name: sarc-f
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates SARC-F component scores, total score, and screening category from
  personal reports of lifting, walking, transfers, stair climbing, and falls. Uses the AAH/BLSA
  questionnaire in Malmstrom et al. (2016). Use for SARC-F, 肌少症筛查, or 肌肉功能风险问卷 when personal
  questionnaire answers are available.
---

# SARC-F 肌少症相关功能风险筛查

依据 Malmstrom 等发表于 Journal of Cachexia, Sarcopenia and Muscle（2016）的
AAH/BLSA 版本。收齐用户自己的五项自述，整理为 `marker,value,unit` CSV 后运行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

## 问卷输入

| marker | 用户的回答与编码 | unit |
| --- | --- | --- |
| strength_response_score | 提举或搬运10磅物品：0无困难，1有些困难，2很困难或无法完成 | score |
| walking_response_score | 走过一个房间：0无困难，1有些困难；很困难、使用辅助器具或需要他人帮助，任一情况为2 | score |
| chair_response_score | 从椅子或床起身转移：0无困难，1有些困难；很困难、使用辅助器具或需要他人帮助，任一情况为2 | score |
| stairs_response_score | 登上10级台阶：0无困难，1有些困难，2很困难或无法完成 | score |
| falls_past_year_count | 过去一年实际跌倒次数，填写整数，不填折算后的单项分 | 1 |

10磅约4.54千克；这只是理解题干的换算，不把原题替换为5千克。
先明确回答类别再编码；遇到辅助器具或他人帮助要按对应题的规则判断。
所有输入均为整数。用户不记得时保留缺失，不默认无困难或无跌倒。
这是日常功能自述，不要求现场尝试提物、登阶或独自起身。
中文题干为解释性翻译，不声称是经语言学验证的中文版。

`--age`（岁）与 `--sex` 可选，不改变计分。问卷不是干预目标预测模型，
不提供 `--targets`；减少回答分数并不等于已证明降低结局风险。
NHANES 的平衡/跌倒问题版本不在本技能输入范围，不能用平衡问题反推跌倒次数。

## 读取报告

读取 `out/report.md` 与 `out/result.json`。报告先显示论文卡片，再显示五项得分、
总分和筛查分档。全部计分常数位于 `scripts/presets.py`。
总分达到4分为筛查阳性，可交给医生进一步评估；低分也不能排除肌少症。
年龄与性别只作背景，群体关联不能转换为个人死亡概率、寿命或干预收益。

退出码3表示输入问题：读取 `out/problems.json`，向用户说明缺哪一项、题干是什么，
或哪项单位/数值有误，补齐后重跑。不输出总分，且清除上次的结果文件。

不得向用户索要全文、补充表、AAH/BLSA/NHANES 队列或公开代码，运行完全离线。
复现的是原文的跌倒次数单项得分，未声称复现一位研究参与者的完整记录。
研究材料及版本差异见 `references/claims.md`，实现范围见 `references/contract.md`。

每份报告必须保留：

> 边界: SARC-F 是肌少症相关功能风险筛查问卷，不能单独确诊或排除肌少症，不能预测个人死亡概率、寿命或干预收益；本研究基于美国社区人群，其他人群的适用性需另行评估；不能据此开始、停止或调整药物。
