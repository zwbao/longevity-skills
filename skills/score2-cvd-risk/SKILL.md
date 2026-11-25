---
name: score2-cvd-risk
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Estimates SCORE2 ten-year first-onset fatal and non-fatal cardiovascular risk
  from age, sex, smoking, blood pressure and cholesterol in adults aged 40–69 without prior CVD or
  diabetes in the paper's European risk regions. Use for SCORE2、欧洲心血管风险、血压血脂风险 and user-specified
  target scenarios.
---

# SCORE2 心血管风险

用户命令：「用我的年龄、性别、吸烟状态、血压和血脂算 SCORE2 十年心血管风险，并比较我填写的目标。」

收集年龄（40–69 岁）、论文模型性别（male/female）、所在国家对应的风险地区、既往心血管病和糖尿病情况。用 [地区表](references/regions.md) 选择 `low/moderate/high/very_high`，不能按个人感觉选地区，不能将中国套入欧洲地区。`--europe yes` 表示属于该表列出的校准国家（包括部分邻近国家），不是国籍或种族判断。不确定地区或病史时先补全，不默认阴性。

测量文件 CSV/TSV 表头为 `marker,value,unit`，四项必须齐全：

| marker | 含义 | unit |
|---|---|---|
| sbp_mmhg | 收缩压 | mmHg |
| tc_mmol_l | 总胆固醇 | mmol/L |
| hdl_mmol_l | HDL 胆固醇 | mmol/L |
| smoker | 当前吸烟 1，其他 0 | 1 |

中文化验单别名及 mg/dL、mg/L 血脂和 kPa 血压换算见 `skill.json`。非 HDL 胆固醇不能替代总胆固醇；风险图虽用非 HDL 展示，连续模型需要 TC 和 HDL 分别输入。

执行（参数替换为用户数据）：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 50 --sex male --region low --europe yes --prior-cvd no --diabetes no --out out
```

目标文件使用相同表头，可只填想比较的血压、TC、HDL 或吸烟状态，添加 `--targets targets.csv`。不生成默认目标，不把模型差当成干预获益，尤其不把 HDL 升高的关联当成治疗效果。年龄、性别、地区不能作为目标。每次成功均输出 `report.md`、`result.json` 和 `levers.json`；缺项、单位错误、范围错误或不适用时退出 3，并输出 `problems.json` 与不含已算风险的报告。

所有参数已冻结在 `scripts/presets.py`；不要求用户提供论文、附件、公共队列或作者代码。报告从论文卡片开始，使用中文，并原样保留：

> 边界：仅适用于欧洲风险地区、40–69 岁、无既往心血管病且无糖尿病的人；这是首次致死或非致死心血管事件的十年模型估计，不是诊断或个人寿命预测；目标情景不代表干预效果，不能据此开始或停止药物。

不添加药物剂量、启停建议或个人高低危治疗阈值。SCORE、SCORE2-OP 和 SCORE2-Diabetes 是不同模型，不能替换。方法、参数出处和误差容限见 [合同](references/contract.md) 与 [核查记录](references/claims.md)。
