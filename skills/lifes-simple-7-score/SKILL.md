---
name: lifes-simple-7-score
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Life's Simple 7 (LS7) cardiovascular health score as scored in the HANDLS cohort
  (Georgescu et al., GeroScience 2026): rates smoking, healthy diet, physical activity, body mass
  index, blood pressure, total cholesterol and fasting glucose as ideal, intermediate or poor (2, 1, 0
  points) and adds them to a 0–14 total. Use for 心血管健康评分, LS7, Life's Simple 7, 生命简单七项, or what-if
  goals for blood pressure, cholesterol, glucose, weight and exercise.
---

# Life's Simple 7 心血管健康总分（HANDLS 计分）

## 这个方法算什么

美国心脏协会的 Life's Simple 7 把七项心血管健康指标各打 0–2 分，相加得 0–14 分，越高越好。本技能照 Georgescu 等（GeroScience 2026）补充材料的补充方法 2 和表 S1A 计分；这篇论文在美国巴尔的摩 HANDLS 队列里发现总分越高，随访期间全因死亡风险越低。

## 输入

- 测量值（`--measurements`，列 item,value,unit）：体重指数（kg/m²）、收缩压和舒张压（mmHg）、总胆固醇和空腹血糖（mg/dL 或 mmol/L，写明单位）、每周中等强度和高强度身体活动分钟数（没有写 0）、五项饮食目标达到了几项（0–5）。
- `--smoking`：never、quit_over_1y、quit_within_1y、current。
- `--bp-treated`、`--chol-treated`、`--glucose-treated`：是否在用降压、调脂、降糖药，yes 或 no。
- 可选 `--targets`：目标值表（同样的列），脚本另写 `out/levers.json`，给出达到目标时的总分和每一项单独达标的分数变化。

```bash
python3 scripts/personal_report.py --measurements m.csv --smoking never \
  --bp-treated no --chol-treated no --glucose-treated no --out out
```

不要向用户要论文 PDF 或补充表；切点已经写在 `scripts/presets.py`。

## 限制

- 论文正文表 2、表 3 印着 LS7 与全因死亡的风险比，出版社页面需要登录，没有取得；报告不给风险比，也不把总分换成个人死亡概率。
- 补充表 S1A 把戒烟超过 1 年算理想；同一补充材料第 1.1 节的文字把所有已戒烟者算中等。脚本照表 S1A，戒烟超过 1 年时报告写明另一种读法会低 1 分。
- 论文写中等和高强度活动“或两者组合”达标也算理想，但没印折算方法；两者都有、各自都没到切点时按中等计，报告写明。
- 饮食和活动两项在 HANDLS 里由 24 小时膳食回顾和 Baecke 问卷改编，个人自报的目标数和分钟数只是近似。

## 边界

报告里必须原样保留：LS7 总分是心血管健康的七项打分，研究里它和死亡风险相关，不能算出你个人的死亡概率；它不是诊断，也不决定开始、停用或调整任何药物。
