---
name: modifiable-risk-factor-score
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Counts one person's modifiable risk factors for all-cause mortality (0-11: low
  education, depression, smoking, alcohol, physical inactivity, unhealthy diet, short or long sleep,
  BMI outside 18.5-28, diabetes, hypertension, dyslipidemia) with the binary cutoffs of Chen et al.
  2026 (three Chinese cohorts, ages 30 to centenarians), splits it into socioeconomic, behavioral and
  metabolic scores, and looks up the per-point mortality hazard ratio for the person's age group
  (Supplementary Table S11). Use for 可改变危险因素, 死亡风险因素有几项, 生活方式评分, 长寿风险, or what-if goals for activity,
  sleep, weight, blood pressure, glucose and lipids.
---

# 可改变危险因素得分（Chen 等 2026）

## 这个方法算什么

论文汇总中国嘉道理生物库海南子队列、海南百岁老人队列和广州生物库队列（共 61,048 人，30–116 岁），按补充方法 S1 把 11 项可改变危险因素各定成有（1）或无（0），等权相加得 0–11 分，再分成社会经济与心理（教育、抑郁）、行为（吸烟、饮酒、体力活动、饮食、睡眠）、代谢（体质指数、糖尿病、高血压、血脂异常）三组。补充表 S11 给出五个年龄段每多一分的全因死亡风险比。

## 输入

- 测量表（`--measurements`，列 item,value,unit）：每周体力活动量（MET-小时/周）、10 项健康饮食得分（0–10）、每晚睡眠时长（小时）、体质指数（或体重和身高）、收缩压和舒张压、空腹血糖（或随机血糖）、总胆固醇、低密度和高密度脂蛋白胆固醇、甘油三酯（mmol/L 或 mg/dL）；可选老年抑郁量表 GDS-15 得分。
- 档案：实足年龄（`--age`，30 岁及以上）；`--sex` 可给，不进得分。
- 是否项（yes 或 no）：`--education-junior-middle`（读完初中或以上）、`--depressive-symptoms`（过去一年有两周以上的抑郁症状；有 GDS-15 得分时可不填）、`--ever-smoked`、`--ever-drank`、`--diabetes-diagnosed`、`--glucose-lowering-medication`、`--hypertension-diagnosed`、`--antihypertensive-medication`、`--hyperlipidemia-diagnosed`、`--lipid-lowering-medication`。
- 可选 `--targets`：目标值表（同样的列），脚本另写 `out/levers.json`：每一项目标单独达成和一起达成时得分少几项、按每分风险比推算的相对风险变化。

```bash
python3 scripts/personal_report.py --measurements m.csv --age 55 \
  --education-junior-middle yes --depressive-symptoms no --ever-smoked yes --ever-drank no \
  --diabetes-diagnosed no --glucose-lowering-medication no --hypertension-diagnosed no \
  --antihypertensive-medication no --hyperlipidemia-diagnosed no --lipid-lowering-medication no --out out
```

哪一项定不下来（例如没有血脂四项、又没诊断过高血脂），脚本退出 3，`out/problems.json` 写明缺什么；不要用别的数代替。某一项已经由诊断或用药判定为“有”时，相应化验可以不给。

不要向用户要论文、补充材料或队列数据；需要的切点和风险比都在 `scripts/presets.py`。

## 限制

- 论文没有印出个人得分的算例；测试核对的是切点和补充表 S11 的查表值，所以分级是草稿。
- “与零项相比”的相对风险是每分风险比的得分次方，论文没有印出，置信区间没有算。
- 诊断过或正在用药就算这一项“有”，即使数值已经正常；这是论文的定义。
- 体质指数正好 28 时，补充方法 S1 的表（>28 算风险）和统一说明（≥28）不一致，脚本照表算。
- 队列都在中国南方，百岁组只来自海南；基线只测一次。

## 边界

报告里必须原样保留这句：这是中国三个队列里人群层面的关联（风险比），是模型估计，不是诊断，也不是这个人一定会发生的事；它不决定是否用药，不能据此开始或停用任何药物。
