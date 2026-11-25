---
name: ckb-diet-score
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes the CKB five-component diet score from habitual food-consumption days
  per week and retrieves the corresponding published mortality associations, including separate male
  and female tables. Use for diet records, CKB diet scoring, or comparing user-supplied dietary
  frequency targets. Reports in Chinese and distinguishes cohort associations from personal mortality
  or lifespan predictions.
---

# CKB 饮食评分

把用户过去 12 个月的通常食用频率整理为 `diet.csv`。只计算饮食部分，不把五种食物误当成五项生活方式。

```bash
python3 scripts/personal_report.py --diet diet.csv --age 50 --sex female --out out
```

输入列为 `marker,value,unit`。五个必填项目为新鲜蔬菜、新鲜水果、红肉、豆类、鱼。键名、别名见 `skill.json`；单位 `d` 表示**固定七天一周中食用的天数**，范围 0–7，每天填 7。它不是进食次数、份量或持续小时数。不要把次数/周、克/天、单独一周的记录擅自换成过去一年的通常食用天数。可用用户明确给出的平均食用天数，脚本按原文切点直接判断，不取整。无法确定通常频率时，先补齐这五项记录。

示例输入模板见 `references/input-format.csv`，只演示格式，不是论文中的受试者。不要把模板默认填入个人报告。

`--sex male` 查表 S3；`female` 查表 S4；不提供性别或指定 `pooled` 查男女合并的表 1。年龄只核对研究入组范围，不改变得分。主分析排除基线冠心病、脑卒中和癌症，已有这些病史者不能把查表结果当作自身疾病人群的估计。

用户明确提供目标时，加 `--targets targets.csv`，列与饮食文件一致，可只填部分项目。未提供的目标保持当前值。不自行设定或优化目标。`out/levers.json` 始终包含每项单独增减一天的有限差值；有目标时另含各目标单独达成和全部达成时的得分及查表结果。红肉项有上下界，得分低不构成开始吃肉的建议。

输出 `out/report.md`、`out/result.json` 和 `out/levers.json`。错误单位、缺项、超范围或无效值返回退出码 3，并输出 `out/problems.json`；不得用零补缺项。报告先显示论文卡片，再显示个人得分和人群关联。置信区间属于队列 HR，不属于个人预测。参照组未印出 CI，保留空值。

所有规则与 HR 已固化，无需用户提供论文、附录、CKB 或 CNHS 数据。来源、可计算范围和验证说明见 `references/contract.md`、`references/claims.md`。

每份报告原样保留：

> 边界：这是观察性研究的饮食评分和分组人群关联，不是你的死亡概率、个人预期寿命或改变饮食后的因果收益；不能据此开始或停止任何药物。
