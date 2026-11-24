---
name: clinical-frailty-scale-7
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Maps a clinician-confirmed whole-person descriptor to the original seven-category
  CSHA Clinical Frailty Scale and explains it in Chinese. Use for the original Clinical Frailty Scale,
  CSHA CFS, 临床衰弱量表 or 原版七级衰弱评估 when a clinical assessment is available. Does not derive a grade from
  individual symptoms or estimate personal outcome probabilities.
---

# 原版七级临床衰弱量表

依据 Rockwood 等发表于 CMAJ（2005）的原版量表框 1。

用户命令：

> 把临床人员给我确认的整体功能描述对应到原版七级临床衰弱量表，解释等级。

先确认描述来自临床评估，且指的是原版七级量表。原论文由医生在病史和查体后综合判断，不是可逐项累加的自评问卷。若只有零散症状或不能确定完整描述，请说明需要临床人员确认，不能代替临床判断选择等级。不要从后来的量表转换分数。

## 输入和执行

CSV/TSV 列为 `item,value,unit`。`item` 是下表描述的键、中文名称或英文名称；值 `1` 表示临床人员选中了这一完整描述，值 `0` 表示未选，单位为 `1`。只需提供选中的一行；若提供多个选项，只能有一行选中。未写出的选项表示未提交选择，不表示不存在某个症状。

| 键 | 临床人员需综合确认的整体描述（中文释义） |
|---|---|
| very_fit_selected | 精力体能充沛、积极主动，常规律锻炼，处于同龄人体能最好的群体 |
| well_selected | 没有活动性疾病，但不及最健壮者 |
| well_treated_comorbidity_selected | 有合并疾病，但症状控制良好 |
| apparently_vulnerable_selected | 无明显依赖，但常感到行动变慢，或有疾病症状 |
| mildly_frail_selected | 工具性日常生活活动有限度地依赖他人 |
| moderately_frail_selected | 工具性和非工具性日常生活活动都需要帮助 |
| severely_frail_selected | 日常生活完全依赖他人，或处于终末期疾病状态 |

这些不是互斥的独立症状规则；有描述重叠时需要临床人员选择最符合的整体描述。软件不指定优先级、不推断终末期。

从仓库根目录运行：

```bash
python3 skills/clinical-frailty-scale-7/scripts/personal_report.py --measurements assessment.csv --out out
```

不需要年龄或性别参数：它们不是框 1 等级映射的输入。不要向用户索要论文、附录、研究队列、系数、源码或化验单；原量表映射已内置。适用语境是老年人的临床评估，不外推到年轻人或用来自动判断急性变化。

成功写入 `out/report.md` 和 `out/result.json`。缺项、错误单位、非二元选项、多选、无法识别的项目或无法读取文件时退出码为 3，写入 `out/problems.json` 和带论文卡片的错误报告；所有结果为空。没有目标模拟：本方法是临床描述分级，不是可用等级变化计算干预收益的模型。

## 报告边界

每份报告保留原句：

> 边界: 本报告仅把临床人员确认的描述对应到 2005 年原版七级临床衰弱量表，不替代临床评估，不预测个人死亡或入住照护机构的概率，也不用于决定开始或停止药物。

复现状态只说明框 1 描述到等级的对应通过测试，不代表量表自评、临床判断或死亡风险模型得到新的验证。七级不能解释为已确认终末期；该级还包含完全依赖者。见 [合同](references/contract.md) 与 [证据核查](references/claims.md)。
