---
name: score2-op-risk
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Recomputes the published SCORE2-OP ten-year primary cardiovascular risk equation for
  older adults, using age, sex, smoking, diabetes, blood pressure, cholesterol and the paper's country
  calibration groups. Use for SCORE2-OP risk questions or comparisons at user-supplied target
  measurements. Regional examples remain unresolved; the Chinese report labels the estimate
  provisional.
---

# SCORE2-OP 十年心血管风险

用户提供自己的测量 CSV、年龄、模型分层性别、居住国家和既往心血管病情况。
本技能自带计算所需参数和国家表，不向用户索要论文、附件、队列数据或代码。

用户命令示例：

> 用 SCORE2-OP 看我的十年心血管风险：75 岁女性，住法国，无冠心病、卒中或外周动脉病史，目前吸烟，无糖尿病；收缩压 140 mmHg，总胆固醇 5.5 mmol/L，HDL 胆固醇 1.3 mmol/L。再比较我提供的目标值。

将测量整理成 `marker,value,unit`：

```csv
marker,value,unit
SBP,140,mmHg
TC,5.5,mmol/L
HDL-C,1.3,mmol/L
smoker,1,1
diabetes,0,1
```

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 75 --sex female --country France --prior-cvd no --out out
```

- 年龄限 70–89 岁，既往冠心病、卒中或外周动脉病者不适用。年龄上限是实现限制，并非论文的推导样本上限。
- 国家按补充 Table 2 的 2021 年分组，见 `scripts/presets.py::COUNTRIES`。不按种族选地区，不为中国或表外国家推测校准组。
- 糖尿病史和当前吸烟必须明确填 0/1。接受总胆固醇和 HDL；不能只凭 non-HDL 猜出两者。
- 有目标文件时加 `--targets targets.csv`。同样三列表头，仅接受收缩压、总胆固醇、HDL 和当前吸烟状态；年龄、性别、国家、糖尿病史保持原值。
- 退出码 3 时读取 `out/problems.json`，让个人助手说明缺项、单位或适用人群问题；不要填默认值或继续给出风险。
- 成功写 `out/report.md`、`out/result.json`、`out/levers.json`。`risk_10y_pct` 是暂定地区风险，`original_risk_10y_pct` 只用于校准前计算核对，不应呈现为第二种临床风险。

报告必须先放论文卡片，并说明补充 Methods Tables 1 与 3 的地区校准参数冲突。
算例中间风险可复现，最终校准结果未复现，不能宣称模型已验证。
仅计算十年主结局，不计算五年风险、含心衰住院的次要结局、风险等级、药物治疗收益或个人寿命。
目标值变化是方程重算，不能把它解释为戒烟、降压或降脂干预的因果效果。

每份报告保留：

> 边界: 这是已发表风险方程的暂定复算，尚未复现地区校准后的论文算例；不是诊断、个人寿命预测或治疗建议，不能据此开始或停止任何药物。目标值差异只表示模型估计变化，不等于干预能够带来的风险下降。

数值出处、版本差异与复现缺口见 `references/contract.md`；研究人群和利益冲突见 `references/claims.md`。
