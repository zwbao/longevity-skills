---
name: jurca-nonexercise-crf
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Estimates cardiorespiratory fitness in METs with the Jurca NASA non-exercise worksheet
  using age, sex, BMI, resting heart rate, and a five-level physical activity category. Use when an
  adult asks to estimate fitness without an exercise test or compare user-supplied input targets.
  Reports in Chinese and preserves the unresolved published worked-example discrepancy.
---

# 非运动测试心肺适能估计

接收20–70岁成年人的年龄、论文性别编码、BMI、静息心率和日常活动等级，按 Jurca 等（2005）表5 NASA列及图1计算表估计最大心肺适能。论文示例无法复现，当前结果必须注明暂定。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 45 --sex male --out out
```

测量文件采用 `marker,value,unit` 三列表头，必需项目为 `bmi_kg_m2`（kg/m^2）、`resting_hr_bpm`（/min，可用bpm或次/分钟）和 `activity_level`（score）。年龄单位为岁，性别参数接受 male/男/1、female/女/0。不要猜测缺少的输入。BMI可从用户自己的身高体重按kg/m²计算；不要求用户提供PDF、补充表或队列数据。

按图1选择最符合平时活动情况的一档，涵盖家务、交通、工作及休闲活动：

| 档位 | 图1活动描述的中文释义 |
| --- | --- |
| 1 | 除日常生活活动外，很少活动或不活动 |
| 2 | 每周至少5天低强度活动，每次至少10分钟，呼吸和心率略增 |
| 3 | 快走、慢跑、骑车、游泳或相近强度有氧活动，每周20–60分钟 |
| 4 | 快走、慢跑或相近强度有氧活动，每周1–3小时 |
| 5 | 快走、慢跑或相近强度有氧活动，每周超过3小时 |

图1第3、4档在每周60分钟处重叠，且第2档和有氧档位不是互斥时间阈值。保留原文表述，让用户选择最符合其通常活动的一档；不要凭步数或分钟数自动分档。不要将表1的SR-PA-0至4编码直接当成1–5档。

静息心率按研究测法为平卧或半卧休息5分钟后的记录；全天平均、运动中、站立时心率不能直接替代。原研究NASA推导样本未使用影响心率的药物，且运动心电图无异常。外推局限应保留，不能据此改变用药。

有用户自行提供的目标时，添加 `--targets targets.csv`，表头与测量表相同，仅接受BMI、静息心率和活动等级，可只填部分项目。目标不得由模型推荐；年龄和性别不是目标。每次成功运行写 `out/report.md`、`out/result.json`、`out/levers.json`，后者含当前输入敏感度、活动类别的有限差值、每项目标单独变化及全部目标的结果。

错误或缺项退出3，写 `out/problems.json` 和带论文卡片的中文报告，清除旧数值结果。请按问题列表向用户说明应补充或纠正什么。

报告先显示论文卡片，再显示估计结果，必须保留暂定验证说明。仅实现作者选入图1的NASA模型，不能把其他队列的系数混进来；不输出风险档位、药物剂量、运动处方或寿命。

必须原样保留：

> 边界: 这是非运动测试回归模型的心肺适能估计，不等于实测心肺适能，不用于诊断、寿命或死亡风险预测；目标情景只是公式变化，不能证明个人干预效果，也不能据此开始或停止药物。

原始常数、材料访问记录及示例不一致的分析见 [产品合同](references/contract.md) 和 [证据核对](references/claims.md)。
