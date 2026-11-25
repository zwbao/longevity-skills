---
name: friend-treadmill-crf-percentiles
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Interprets directly measured maximal treadmill CPX oxygen uptake using the FRIEND
  age- and sex-specific reference percentiles. Use when a person provides a maximal treadmill
  cardiopulmonary exercise test and asks how their cardiorespiratory fitness compares with peers.
  Requires age, sex, peak RER and confirmation of the paper's eligibility conditions.
---

# FRIEND 跑台心肺适能参考百分位

用 Kaminsky 等 2015 年论文表 3 中的 FRIEND 实测值定位个人心肺适能。只输出匹配的百分位阈值或相邻阈值区间；没有连续百分位公式。

用户命令：

> 用我的最大跑台心肺运动试验报告，按 FRIEND 参考表看实测最大摄氧量在同年龄、同性别人群中的位置。

## 需要个人提供的数据

测试时整周岁年龄（20–79）、论文中的男/女性别分层、体重归一化实测最大摄氧量及同次试验峰值呼吸交换率（RER）。应确认测试采用最大跑台 CPX、呼吸气体实测，没有已知心血管病或 COPD，且未在自愿最大努力前因异常临床发现终止。未知项先补齐，不默认“无病”。

测量文件为 `marker,value,unit` 的 CSV 或 TSV；例如 `VO2max,48.0,mL/kg/min` 和 `RER,1.20,1`。摄氧量支持 mL/kg/min 或 L/kg/min，后者乘以 1000。必须保留测量来源，不能把手表估值或负荷推算值改名成实测值；自行车及次最大测试不适用。

## 执行

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 20 --sex male --test-type maximal_treadmill_cpx --cvd no --copd no --early-stop no --out out
```

`--sex` 接受 male/m/男、female/f/女。其余确认参数见上，均不能在没有依据时填写。年龄为整数，RER 必须至少 1.00。缺项、错单位、非数值、超出录入范围或不符合适用条件时退出 3，写 `out/problems.json` 和带论文卡片的中文说明，不输出个人百分位。

成功时生成 `out/report.md`、`out/result.json`。低于 P5 或高于 P95 的未定界一端在 JSON 为 null。落在两阈值之间不插值、不四舍五入成某个百分位。相等仅表示与论文的一位小数阈值相同。

表格已经冻结在 `scripts/presets.py`。禁止向用户索要 FRIEND 原始数据库、论文 PDF、公共补充表或代码。此方法为静态参考表，不是可推演干预效果的风险方程，不提供目标敏感度或运动处方。

## 报告边界

报告先放论文卡片，明确美国参考人群、年龄和性别分层、阈值舍入及跨人群限制。不要把横断面的年龄差异当成个人随年龄下降的预测。每份报告保留：

> 边界: 这只是与美国 FRIEND 同年龄段、同性别人群的实测心肺适能参考值比较，不是疾病诊断、个人死亡风险、寿命或生物年龄；不能据此开始或停止药物，也不生成运动处方。

核查记录见 [产品合同](references/contract.md) 和 [论文核对](references/claims.md)。
