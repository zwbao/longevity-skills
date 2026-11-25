---
name: ctt-ldl-relative-risk
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Converts an absolute LDL cholesterol reduction into a major vascular event rate
  ratio using the CTT multiplicative relationship. Use for LDL-C reduction scenarios or
  before-and-after LDL-C comparisons; accepts a measured reduction and an optional target reduction,
  with explicit units.
---

# LDL-C 降幅的相对发生率换算

用户命令：`用我的 LDL-C 绝对降幅，估算主要血管事件的相对发生率，并比较我的目标降幅。`

将用户的绝对降幅整理为 CSV（marker,value,unit），运行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

已有目标时增加 `--targets targets.csv`，列格式相同。目标是相对同一参照的总降幅，不是额外降低量。没有目标时不替用户设置目标，仍输出当前敏感度。

## 输入

- 唯一输入 `ldl_reduction_mmol_l`：LDL-C 参照值减去比较值，接受 mmol/L、mg/dL、umol/L。化验单只有两次浓度时，先核对时间、参照状态和单位，再计算差值；不要把单次 LDL-C 直接填成降幅。
- 推荐行名「LDL-C 绝对降幅」或「LDL-C reduction」。单次化验常见的「LDL-C」「低密度脂蛋白胆固醇」故意不作为降幅别名；百分比也不接受。不用 LOINC 标识两个浓度的差值。
- 只支持非负降幅，最大值限于正文最大外推示例。范围是产品护栏，不是疾病阈值。超出范围先解释限制，不截断、不取绝对值。
- 年龄、性别、现用药不进入本公式。适用语境是成人他汀试验；不得把其他情境包装成已经验证的个人获益。

## 输出与边界

读取 `out/report.md`、`out/result.json` 和 `out/levers.json`。输入有误或缺失时退出 3，读取 `out/problems.json` 告诉用户该补什么；不得补零。

报告从论文卡片开始。RR 是主要血管事件复合终点的相对发生率，不是绝对发生概率、终生风险或寿命。区间来自总体系数的不确定性，不是个人预测区间。短期化验变化不能证明个体因果效应，不能将比值按年重复相乘。

必须原样保留：

> 边界: 这是他汀随机试验人群平均效应的数学换算，不是个人绝对风险、寿命或净获益预测；不能据此开始或停止用药，也不能据此调整剂量。

不要向用户索要原文、附录、试验个体数据或代码。运行完全离线，常数已核对并冻结。出处、复现容差和适用范围见 `references/contract.md`，材料核对见 `references/claims.md`。
