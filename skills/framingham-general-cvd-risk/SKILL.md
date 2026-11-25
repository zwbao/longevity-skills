---
name: framingham-general-cvd-risk
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the Framingham general cardiovascular disease ten-year risk and
  continuous heart/vascular age from personal blood pressure and lipids or BMI. Use for Framingham
  2008 risk, 总体心血管风险、心脏年龄、血管年龄, or comparing user-supplied blood pressure and lipid targets in adults
  aged 30–74 without prior cardiovascular disease.
---

# Framingham 总体心血管风险

根据 D’Agostino 等，Circulation 2008 的男女 Cox 方程，计算首次总体心血管事件风险。它包含冠心病、脑血管事件、间歇性跛行和心衰，不能称为单独心梗风险或 ASCVD 风险。

用户只提供个人测量和健康状态。所有系数已冻结在 `scripts/presets.py`，运行无需联网；不要向用户要论文、补充表、队列数据或官网工作簿。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 61 --sex female --treated no --smoker yes --diabetes no --prior-cvd no --model lipids --out out
```

测量文件表头为 `marker,value,unit`，可用中文或英文别名。默认血脂版需要收缩压、总胆固醇和 HDL-C；血脂接受 mg/dL 或 mmol/L，收缩压接受 mmHg 或 kPa。没有血脂时明确使用 `--model bmi`，需要收缩压和 BMI（kg/m²），不自动替换缺失项，也不将两个方程混合。

年龄以岁填写，限 30–74 岁；性别 `male/男` 或 `female/女`。必须明确当前是否接受降压治疗、是否当前吸烟、是否有糖尿病，以及既往是否已有心血管病（包括冠心病、卒中/TIA、外周动脉病或心衰）。是/否可填 yes/no；未知不能当否。已有心血管病时不运行首次事件模型。糖尿病使用已有诊断信息，不由本技能诊断。

可附加 `--targets targets.csv`，表头与测量文件相同，允许只写部分连续测量目标。血脂版接受收缩压、总胆固醇、HDL-C；BMI 版接受收缩压、BMI。禁止替换年龄、性别、治疗、糖尿病、吸烟状态或方程版本。不要替用户设目标；输出是数学情景差异，不是因果疗效或治疗建议。

成功输出 `out/report.md`、`out/result.json`、`out/levers.json`。杠杆文件含当前数值附近的敏感度，有目标时增加每项独立变化和同时变化，风险差单位为百分点。缺项、非数、错误单位、不适用人群或无效目标时退出 3，生成 `out/problems.json` 与带论文卡片的中文问题报告，不留下旧的计算结果。

报告保留：

- 开头的论文卡片、所选模型及实际输入。
- 十年风险、同龄同性别参考状态风险、连续方程等价心脏年龄及年龄差。
- 原论文参考状态仅用于风险表达，并非治疗目标。连续心脏年龄不是表9/10的整数积分查表结果。
- 历史美国、以白人为主的人群来源；未在本报告中对中国人群重新校准。
- 边界：这是历史美国队列的首次总体心血管事件风险估计，不是诊断、个人命运或干预效果预测；心脏年龄只是风险的等价表达，不是实测器官年龄。不能据此开始、停止或调整药物。

原在线补充材料访问受限；本实现使用正文与研究官网已核对参数。参见 `references/contract.md` 的可行性审计和 `references/claims.md` 的研究边界。不输出整数积分表、分项疾病风险、风险诊疗分档、剂量或启停药建议。
