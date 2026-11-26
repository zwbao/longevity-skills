---
name: qrisk3-cvd-risk
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. 按 QRISK3-2017 男女模型 C，使用年龄、血压及重复记录标准差、体质指数、总胆固醇/HDL 比值、Townsend 评分及病史估计十年心血管病风险。用户问
  QRISK3、英国心血管风险或目标测量值下的模型变化时使用。
---

# QRISK3 十年心血管风险

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 44 --sex male --out out
```

测量表为 `marker,value,unit`。按 `skill.json` 的别名、单位、范围读取；每个病史是否项都要明确填 0 或 1，未知不能当无。`--age` 为 25–84 周岁整数，`--sex` 为 male 或 female。已有冠心病、缺血性卒中、TIA 或正在用他汀时，本工具不计算。

用户只提供个人数据。不要向用户要论文、补表、模型代码、训练队列或外部数据文件。参数已冻结在技能内，运行离线完成。方法来自英国；不能把英国华人结果直接当中国居民模型。

- 收缩压是评估前最近一次记录。标准差是此前五年内所有可用收缩压重复记录的样本标准差，至少两次；同时填 `sbp_readings_n`。可由助手整理用户已有记录后按 `sqrt(sum((x-mean)^2)/(n-1))` 计算，保留来源、日期和所用记录。论文写“标准差”而未明确分母，采用样本标准差是本技能公开的操作约定。单次血压、没有记录或未知时不能填零。本脚本读取整理好的标准差及记录数，不读取原始血压序列，也不验证日期窗口。
- `townsend_score` 必须是已有的英国地区贫困评分。没有评分时报告缺项，不默认均值或零，不从中国邮编、收入或族裔推算。
- `tc_hdl_ratio` 需 TC 和 HDL-C 采用相同单位后相除；不接受 LDL-C 代替。
- 族裔编码 1–9：白人或明确未记录、印度、巴基斯坦、孟加拉、其他亚洲、加勒比黑人、非洲黑人、华人、其他。吸烟 0–4：不吸烟、既往吸烟、每日 1–9 支、10–19 支、至少 20 支。
- 男性还必须提供勃起功能障碍诊断或治疗状态；女性模型不用此项。药物、诊断和家族史的定义见 [输入合同](references/contract.md)。

可加 `--targets targets.csv`（相同三列）。仅接受 BMI、血脂比值、收缩压、收缩压标准差。目标由用户或医生提供，不自动生成。`out/levers.json` 含当前值、连续项局部敏感度、类别项对照、单项目标和全部目标同时达到时的结果。病史、药物、性别、年龄与族裔对照是数学说明，不能作为干预选项。

成功输出中文 `out/report.md`、`out/result.json` 和 `out/levers.json`。缺项、单位错误、超范围、非法编码或不符合使用人群时退出 3，写 `out/problems.json`，清除上次计算结果。报告开头保留论文卡片，写明“仍在验证”，不能把人群校准/区分度当个人置信区间。

每份报告必须保留：

> 边界：这是英国人群观察性模型的估计，仍在验证，不能替代医生评估，也不能证明改变某项就能获得对应治疗收益；不能据此开始、停止或调整药物。

原始代码的声明须随风险结果展示；脚本已包含。重新分发需保留 [LGPL](references/LICENSE-LGPL-3.txt)、[GPL](references/LICENSE-GPL-3.txt)、ClinRisk 版权及 [声明](references/disclaimer.txt)。

验证范围和未解决的个人示例输入见 [contract.md](references/contract.md)；全文、补表、补图和代码的核查记录见 [claims.md](references/claims.md)。
