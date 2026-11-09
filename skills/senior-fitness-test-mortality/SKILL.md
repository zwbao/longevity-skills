---
name: senior-fitness-test-mortality
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Places an older adult's own Senior Fitness Test results (2-minute step, 30-second arm
  curl, 30-second chair stand, back scratch, chair sit-and-reach, one-leg stance, 8-foot up-and-go) in
  the sex-specific quintiles of the Taiwan National Physical Fitness Survey cohort (Wu et al., JAMA
  Network Open 2026; 13,423 adults aged 65-90, about 7 years of follow-up) and reports the printed
  adjusted hazard ratio of all-cause mortality for that quintile versus the lowest. Use for 老年体适能,
  体能测试, 椅子坐立, 单脚站立, 起身绕行, 2分钟踏步, 体能和寿命, 死亡风险. States that the hazard ratios are population
  associations, one model per test, not a personal probability.
---

# 老年体适能五分位与全因死亡风险比（台湾国民体能队列）

用户交自己的体能测试成绩（七项里任意几项）和性别，年龄可选。不要向用户要论文、PDF 或补充表，五分位范围和风险比已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements fitness.csv --sex female --age 72 --out out
```

`fitness.csv` 的列是 `item,value,unit`：

- 2 分钟原地抬膝踏步、30 秒手臂弯举、30 秒椅子坐立：次数，单位留空或写“次”。
- 抓背、椅子坐姿体前弯：cm（也接受 mm、in），**必须写单位**；重叠或超过脚尖记正，差距记负。
- 睁眼单脚站立、8 英尺起身绕行：秒（写 s 或“秒”）。单脚站立超过 30 秒按 30 秒归档（论文测试上限）。
- 名称也认英文名和台湾体适能常用名（肱二头肌手臂屈举、开眼单足立、椅子坐立绕物等），`skill.json` 列出全部。

可选 `--targets targets.csv`（同样的列）：脚本另写 `out/levers.json`，给出每项目标成绩所在的五分位和该档风险比，以及进入上一档的成绩起点。

报告给出每项成绩的同性别五分位（Q1 最差、Q5 最好）、该档的成绩范围、同性别分层模型（补充 eFigure 5、6）和男女合并模型（正文图 3、补充 eFigure 4）的风险比与 95% 置信区间。成绩落在两档印出范围之间的空隙时归入较差一档并注明。`out/result.json` 给出每项的 `*_quintile`、`*_ahr_sex`、`*_ahr`，以及 `tests_done`、`tests_in_q1`。

不计算：论文的综合体适能指数（需要整个队列的百分位分布，论文没印），个人死亡概率，几项合起来的总风险。

缺性别、一项成绩都没有、单位不认识、抓背或体前弯没写单位、数值超出合理范围时不计算：报告写明原因，脚本退出码 3。

## 报告里必须保留的话

- 风险比是论文人群（台湾 65–90 岁社区老人，约 7 年）里该五分位组相对同性别最低一组的关联，每项测试单独建模，不能相乘或相加，不是个人死亡概率，也不能说明提高成绩就会降低风险。
- 8 英尺（2.44 米）起身绕行不是 3 米起立-行走计时；椅子坐姿体前弯不是地面坐位体前屈。
- 成绩明显偏低、近期跌倒或有心肺疾病时，建议先找医生评估再开始新的锻炼；不写诊断、不开运动处方。

引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)。
