---
name: ldl-exposure-risk-reduction
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Uses the EAS LDL exposure-duration equation to estimate proportional ASCVD risk
  reduction from a person's absolute LDL-C reduction and years of sustained exposure. Triggers on
  LDL降幅、降胆固醇持续年数、降低LDL的相对获益、LDL exposure duration and relative cardiovascular risk reduction. Compares
  user-supplied target scenarios without recommending treatment or estimating absolute event risk.
---

# LDL 降幅与持续时间的相对风险情景

采用 Ference 等，European Heart Journal，2017 的表2脚注。完整产品合同及表格不一致见 [references/contract.md](references/contract.md)，证据核对见 [references/claims.md](references/claims.md)。

## 用户命令

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

测量文件为 `marker,value,unit` 三列 CSV，例如：

```csv
marker,value,unit
LDL-C reduction,0.5,mmol/L
持续年数,5,a
```

- 必须提供 LDL-C **绝对下降量**（基线浓度减降低后的浓度，或用户明确指定的假设下降量）和持续年数。不要把单次 LDL-C、总胆固醇、non-HDL-C、apoB、百分比降幅或实足年龄直接代入。
- 允许下降量 0–3.5 mmol/L、持续时间 5–40 年；0 是无下降的对照情景。范围用于限制外推，不是临床安全范围或推荐目标。
- 接受 mmol/L 和 umol/L（乘0.001）。不使用表3、4括号里的粗略 mg/dL 对照值换算。若只有 mg/dL 报告，本技能会指出单位问题，助手需取得可靠换算后的下降量再运行。
- 持续时间必须指维持该下降量的总年数；未来年数明确标为情景假设。两次化验不能证明已持续多年。
- 年龄和性别不进入本方程，无需收集。不要向用户索要论文、补充材料、研究队列或源码。
- 需要比较目标时加 `--targets targets.csv`；同样三列，可只给一个或同时给两个输入。目标必须由用户提出，不能用本技能替用户设定治疗目标。

## 输出与失败处理

成功写 `out/report.md`、`out/result.json`、`out/levers.json`。敏感度以“相对风险下降幅度的百分点/输入单位”表示；目标文件存在时另写单项变化与共同变化。没有目标文件时仍写当前敏感度。

缺项、无效单位、非有限数、未知项目或超范围时退出3，写 `out/problems.json` 和含论文卡片的中文报告；不保留旧的结果或目标文件。助手根据问题清单说明缺什么，不补猜数值。

## 解释限制

只计算表2脚注的相对风险及相对下降比例。复现测试覆盖选定单元格，并非所有表格一致：表2部分30年单元格、表3和表4存在脚注与表值不一致，详见合同。不得声称已复现表3、4；不输出绝对风险、NNT或指南用药判断。5年以后包含长期外推，不能宣称来自同等持续时间的随机试验；本技能也不是对现代指南的更新。

每份报告从论文卡片开始，必须原样保留：

> 边界：这是基于人群证据的相对风险情景估计，不是个人发病概率、寿命预测或治疗建议；长期外推不等于同等年限的随机试验证明。只有LDL-C下降与LDL颗粒数下降一致、且没有抵消获益的有害脱靶作用时，论文的推断才适用；不能据此开始、停用或调整药物。
