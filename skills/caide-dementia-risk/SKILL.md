---
name: caide-dementia-risk
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the CAIDE midlife dementia risk score from age, education, sex, blood
  pressure, BMI, cholesterol and physical activity, with an optional APOE model. Use for a request to
  calculate CAIDE or understand long-term dementia risk from midlife measurements. Reports Chinese
  explanations of the score, cohort category incidence and the published risk equation.
---

# CAIDE 中年痴呆风险评分

用户命令：「用我的中年体检和生活信息算 CAIDE 评分，并比较我给出的目标情景。」

基于 Kivipelto 等，The Lancet Neurology，2006。仅接受同一中年基线时点的信息，年龄 39–64 岁。不能用晚年血压替代中年血压。报告不是痴呆筛查或诊断。

## 输入与执行

将用户提供的数据整理为 UTF-8 CSV，列名 `marker,value,unit`。必需指标：

| marker | 内容 | 单位 |
|---|---|---|
| education_years | 已完成受教育整年数 | a |
| sbp_mmhg | 收缩压 | mmHg |
| bmi_kg_m2 | BMI | kg/m^2 |
| total_cholesterol_mmol_l | 总胆固醇 | mmol/L |
| physical_active_1 | 身体活动达标：1 是，0 否 | 1 |
| apoe_e4_1 | ε4 携带：1 是，0 否；仅 APOE 模型必需 | 1 |

活动达标采用原文定义：休闲活动每周至少两次、每次至少 20–30 分钟并引起出汗和气促。不能仅凭步数猜测。APOE ε4 状态指是否至少携带一个 ε4 等位基因，不是拷贝数，也不是某个单独 SNP。未知不能填零。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 50 --sex female --out out
```

默认 `--model basic` 使用模型 1。仅用户已有明确 APOE ε4 状态且要使用遗传模型时加 `--model apoe`；模型 2 有独立的年龄、教育、胆固醇分值，并非只在模型 1 上加 APOE 分。

性别参数 `female` / `male` 对应原研究分类。年龄是测量时的年龄。中文指标名及常用英文别名在 skill.json；胆固醇还接受 mg/dL、umol/L，血压接受 kPa。保留原始单位，不自行猜单位或填补缺项。输入错误或缺失时退出 3，读取 `out/problems.json` 向用户说明需要补充什么。

目标文件同样为 `marker,value,unit`，只含用户指定的收缩压、BMI、总胆固醇或身体活动目标，用 `--targets targets.csv`。不替用户设置目标。每次运行均生成 `out/levers.json`，逐项列出跨分档的敏感度；有目标时另列单项与联合情景。分值阶梯的零变化不代表没有健康作用。

## 交付

读取 `out/report.md` 和 `out/result.json`。报告以论文卡片开始，保留逐项分数，明确区分表 3 分组发生率与方法段公式估计。表 3 置信区间属于原队列分组，不是个人预测区间；模型 2 首组负下限按原表保留并解释。

所有常数已来自正文并冻结于 `scripts/presets.py`；不得要求用户提供论文、补充表、队列文件或代码。来源与访问限制见 `references/sources.md`。不输出诊断、药物剂量或开始/停止用药指令。

每份报告原样保留：

> 边界：这是芬兰中年队列的观察性风险模型，适用于基线 39–64 岁且存活至晚年复查的人群；不能诊断痴呆，也不是你必然发病的概率。目标情景的数值变化不是干预效果，不能据此开始或停用药物。
