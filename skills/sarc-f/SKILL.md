---
name: sarc-f
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the standard SARC-F symptom screening score from five personal
  questionnaire responses. Use for SARC-F scoring, sarcopenia screening, or questions about lifting,
  walking, rising, stair climbing and falls. Reports component points, total score and screening
  category in Chinese.
---

# SARC-F 肌少症风险筛查

使用 Malmstrom 等在 Journal of Cachexia, Sarcopenia and Muscle（2016）验证的AAH/BLSA问卷计分。输入类型为自报问卷，无需化验、肌肉量测量或现场体能测试。适用于解读社区中老年人的症状筛查；其他人群的适用性未由这项研究确立。

## 执行

```bash
python3 scripts/personal_report.py --measurements my_sarc_f.csv --out out
```

可选 `--age` 和 `--sex` 只记录背景，不改变得分；不需要为了计算补问年龄或性别。输出 `out/report.md` 和 `out/result.json`；缺项或输入错误时退出3，生成 `out/problems.json`，报告不显示计算结果。

## 问清五项再填表

CSV表头为 `marker,value,unit`。分值和计数的单位统一写 `1`（无量纲）；前四项填0、1或2，最后一项填实际次数。

| marker | 向本人询问的内容 | 填写规则 |
|---|---|---|
| strength_score | 提举或搬运10磅物品有多困难？ | 0无困难；1有些困难；2很困难或无法完成 |
| walking_score | 走过一个房间有多困难，是否使用助具或需要他人帮助？ | 0无困难；1有些困难；2很困难、使用助具或无法在无人帮助时完成 |
| chair_score | 从椅子或床起身转移有多困难，是否使用助具或需要他人帮助？ | 0无困难；1有些困难；2很困难、使用助具或无法在无人帮助时完成 |
| stairs_score | 爬一段10级台阶有多困难？ | 0无困难；1有些困难；2很困难或无法完成 |
| falls_past_year_count | 过去一年实际跌倒多少次？ | 非负整数次数，由脚本转换为分值 |

同一项符合多个条件时取相应最高分，尤其不能因使用助具后感觉轻松就填0。不要要求本人现场尝试动作。未知不是0，不从握力、步速、疾病或用药猜答案。不收仅有总分而没有五项答案的表格。

跌倒0次为0分，1–3次为1分，≥4次为2分；五项相加，总分≥4为筛查阳性。完整常数来源见 `references/contract.md`。中文题意仅为说明性翻译，不宣称中文量表已在该论文验证。

## 报告边界

报告开头保留论文卡片，随后逐项说明得分与筛查分层；低分不能写成“没有肌少症”。不把队列关联或死亡率写成个人预测。NHANES用平衡/跌倒问题近似跌倒项，不能拿该版本答案填进此技能。

原样保留：

> 边界: SARC-F是症状筛查，不能确诊或排除肌少症，也不预测个人死亡概率或寿命；不能据此开始、停止或调整药物。

不要向用户索要论文、补充表、AAH/BLSA/NHANES队列数据或代码；评分所需常数已冻结在 `scripts/presets.py`。不提供运动剂量、补剂剂量或药物启停指示，不把减少助具使用当作降分目标。这个症状筛查没有干预效应模型，不提供目标优化。
