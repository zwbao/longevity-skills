---
name: fagerstrom-nicotine-dependence
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes the six-item Fagerström Test for Nicotine Dependence (FTND) from a
  current cigarette smoker's answers, with item scores and the total. Use for FTND、尼古丁依赖、烟瘾评分 or
  comparing changes in questionnaire answers. Uses Heatherton et al. (1991) Table 3; does not assign
  severity bands or predict cessation success.
---

# FTND尼古丁依赖计分

用户命令：`用我的六题吸烟习惯回答计算FTND总分，并列出每题得分。`

先确认本人当前吸卷烟，再询问六题。不要把未知答案填0，不要用电子烟、雪茄、烟斗或尼古丁替代产品换算每日卷烟支数。已戒烟者不套用当前吸烟者量表。

将回答保存为CSV，表头 `marker,value,unit`：

| marker | 需要询问的内容 | value与unit |
|---|---|---|
| current_cigarette_smoker | 目前是否吸卷烟（不计分） | 1=是，0=否；unit=1 |
| time_to_first_cigarette_min | 醒来后多久吸第一支烟？ | 整数分钟；unit=min，可用h按60换算 |
| difficulty_refraining | 在禁止吸烟的地方（如图书馆或电影院），是否觉得难以忍住不吸烟？ | 1=是，0=否；unit=1 |
| morning_cigarette_hardest | 最不愿放弃的是晨起第一支烟，还是其他任何一支？ | 1=晨起第一支，0=其他；unit=1 |
| cigarettes_per_day_count | 每天吸多少支卷烟？ | 每日整数支数；unit=1，不能填包数 |
| smoke_more_after_waking | 醒来最初几小时是否比一天其余时间吸烟更频繁？ | 1=是，0=否；unit=1 |
| smoke_when_ill_in_bed | 病得大部分时间卧床时是否仍吸烟？ | 1=是，0=否；unit=1 |

中文题意是说明性翻译，不声称为经验证中文版。计分常数集中在 `scripts/presets.py`，不另套网络流传的严重度分档。

运行：

```bash
python3 scripts/personal_report.py --measurements answers.csv --out out
```

可选 `--age`（岁）用于研究年龄范围提示，`--sex` 不参与计分。不需要年龄和性别才能得出六题分数。需要比较用户明确指定的回答变化时，增加 `--targets targets.csv`，表头与回答表相同，允许只填改变的题目。不得自动生成吸烟量目标或把问卷变化当治疗效果。

输出 `out/report.md`、`out/result.json` 和 `out/levers.json`。缺项、错单位、非整数分钟或支数、不是0/1的二选一回答均退出3，并写 `out/problems.json`；报告保留论文卡片但不输出个人分数。

公开材料由技能维护者核对并冻结计分；运行时离线。禁止向用户索要论文PDF、补充表、作者数据或代码。来源及核对范围见 [references/contract.md](references/contract.md)，研究设计与局限见 [references/claims.md](references/claims.md)。表3的非研究用途许可说明见合同，未声称已获授权。

每份报告必须保留：

> 边界: 本结果仅按1991年FTND六题规则描述当前卷烟吸烟者的自报依赖表现；不能诊断疾病、推算个人戒烟成功率或寿命，也不能据此开始、停止或调整药物。
