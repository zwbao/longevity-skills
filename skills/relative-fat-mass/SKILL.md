---
name: relative-fat-mass
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Estimates adult whole-body fat percentage with the published relative fat mass (RFM)
  equation from height, waist circumference and the paper's sex coding. Use when a person asks about
  RFM, 相对脂肪量, or estimating 体脂率 from 身高 and 腰围. Produces a Chinese report and optional waist-target
  scenarios with population and measurement limits.
---

# RFM 全身体脂率估计

用户命令：「用我的身高、腰围、年龄和性别估算 RFM 体脂率；如果我给了腰围目标，也算公式会怎样变化。」

收集本人的身高、腰围、实足年龄和论文使用的性别类别。只接受 20 岁及以上；孕妇不运行。不能从姓名推断性别，论文男=0、女=1，与 NHANES 原始编码不同。年龄不进入公式。

腰围须在站立呼气末、右侧髂骨上缘水平绕裸露腰部测量，记录至 0.1 cm。已有报告写“腹围”时，先核对测量位置；肚脐围、最细腰部围度不能直接替代。

将本人测量整理成 CSV，列为 `marker,value,unit`。规范键为 `height_cm`、`waist_cm`；可使用清单中的中英文别名。支持 cm、m、mm、in；别名行必须写单位，规范键省略单位按 cm 读。范围仅作录入校验，不代表研究覆盖范围。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 40 --sex male --out out
```

`--age` 填岁数；`--sex` 填 `male/m/男/0` 或 `female/f/女/1`。缺项或错误退出码为 3，先读 `out/problems.json`，告诉用户补哪项或核对哪个单位，再运行，不用默认值填补。

有用户指定的腰围目标时加 `--targets targets.csv`，列同上，仅接受腰围。身高、年龄、性别保持不变。目标情景是公式变化，不能说成实际减脂效果，也不替用户设目标。

输出：`out/report.md`、`out/result.json`、`out/levers.json`。没有目标时仍输出当前输入的敏感度；性别项是离散编码差，年龄项为零，不是改变目标。失败重跑会清除旧结果。

报告标题后先放论文卡片，再给结果，保留暂定验证状态、测量位置和适用范围。独立验证只覆盖 20–69 岁；年龄更大时必须显示超出验证范围。研究分族群分析限美国墨西哥裔、欧洲裔和非洲裔，本研究未验证中国人群、运动员或特定疾病人群。研究排除孕妇及部分超出 DXA 扫描条件者。较瘦人群的表现较弱。

不要把论文任意选择的研究切点变成个人肥胖诊断，不给正常/异常分档，不把群体误差当个人置信区间，不输出用药剂量或启停建议。估计超出体脂百分比的物理范围时停止，不截断为零。

每份报告必须原样保留：

> 边界：RFM 是横断面人群公式的体脂率估计，不是 DXA 实测或肥胖诊断；不能据此推断个人寿命、减脂效果或决定开始、停止药物。

公式已冻结在脚本中，个人计算完全离线。不得要求用户寻找论文、补充材料、NHANES 数据或作者代码。

资料核查见 [合同](references/contract.md)、[证据核对](references/claims.md) 与 [材料清单](references/sources.md)。
