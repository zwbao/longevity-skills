---
name: fnih-sarcopenia-cutpoints
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Uses the FNIH sex-specific cutpoints to classify maximum grip strength and appendicular
  lean mass relative to BMI in community-dwelling older adults. Trigger when a user provides grip
  strength, DXA appendicular lean mass and BMI and asks about FNIH weakness or low lean mass criteria.
  Reports recommended and alternate criteria separately in Chinese.
---

# FNIH 握力与四肢瘦体重切点

适用于已有握力、DXA 四肢去骨瘦体重和 BMI 的 65 岁及以上用户。依据 Studenski 等，2014，doi:10.1093/gerona/glu010，正文表 3。

## 用户命令

“请用 FNIH 标准看我的握力和四肢瘦体重；我 75 岁，男性，测量在 measurements.csv。”

## 输入与执行

用户只提供自己的测量和年龄、性别。禁止向用户索要论文 PDF、补充材料、研究队列或系数文件。
公开切点已冻结在 `scripts/presets.py`，运行时无需联网。

测量文件为 CSV 或 TSV，列名 `marker,value,unit`，必需三项：

| 键 | 测量 | 单位 |
|---|---|---|
| grip_max_kg | 手持测力计双手测量中的最大握力 | kg |
| alm_kg | DXA 双臂及双腿去骨瘦体重之和 | kg |
| bmi_kg_m2 | 同次测量的体质指数 | kg/m² |

按 `skill.json` 识别中英文名称及单位；质量字段支持 g、lb 的精确换算。不要把单手平均握力、单腿瘦体重、全身肌肉量、体脂秤估计或 ALM/身高² 填入这些字段。肢体测量缺失时不能填零或外推。

执行 `scripts/personal_report.py`，参数为 `--measurements measurements.csv --age 75 --sex male --out out`。
`--sex` 可用 male/男 或 female/女；缺失时不得推测。年龄不参与阈值计算，65 岁以下不运行本工具。

## 报告合同

输出 `out/report.md` 和 `out/result.json`。中文报告以论文卡片开头，列出推荐的握力与 ALM/BMI 分层，再分别列出备选的握力/BMI 与绝对 ALM 分层。四个条件独立，不合并为肌少症诊断或严重程度。

所有切点均为严格小于，等于切点时为“未低于切点”。保留未舍入数值进行判断。结果未低于切点不能解释为排除了功能问题。

输入缺失、单位错误、非有限值或超范围时退出码为 3，读取 `out/problems.json` 向用户解释要补测或纠正的具体项目，不输出个人数值。

本方法为阈值分层，不是可预测改变输入后治疗效应的连续模型；不提供目标优化或药物建议。

每份报告必须保留：

> 边界: 本报告仅按 FNIH 2014 研究切点描述握力和四肢瘦体重，不诊断肌少症，不估算个人失能或死亡概率，也不能据此开始、停用或调整药物。

验证仍为草稿：正文及补充附录无个人输入—输出算例。切点转录与合成边界测试不冒充论文算例复现。详见 `references/contract.md` 和 `references/claims.md`。
