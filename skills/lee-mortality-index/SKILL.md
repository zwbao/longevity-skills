---
name: lee-mortality-index
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Calculates the Lee four-year mortality point index from age, sex, BMI, self-reported
  diagnoses, smoking, and functional difficulties, and maps the score to the published
  validation-cohort mortality percentage. Use for community-dwelling adults aged 50 or older asking
  about the Lee index or questionnaire-based mortality risk. Reports in Chinese and supports explicit
  target scenarios without interpreting them as treatment effects.
---

# Lee四年死亡风险指数

根据 Lee 等，JAMA 2006，正文表3和表4运行。用户提供自己的问卷，技能已冻结公开计分和查表值；不要向用户索取论文、HRS原始数据或补充材料。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 70 --sex female --out out
```

`measurements.csv` 列为 `marker,value,unit`；必需项目和含义见下表。二元项只接受0或1，未知不能当作0。年龄按已满周岁填写，`--sex` 接受 male/female、男/女或1/0。年龄小于50岁、非社区居住、缺项、错单位或非法值均停止计算，退出3并写 `out/problems.json`。软件年龄上界120岁仅用于拦截明显错误，不是研究已验证到120岁的声明。

| marker | unit | 含义 |
|---|---|---|
| bmi_kg_m2 | kg/m^2 | 本人BMI，也接受kg/m2（因子1） |
| community_dwelling | 1 | 1=社区居住；0=养老院等机构照护；仅检查适用性 |
| diabetes | 1 | 医生曾告知糖尿病或高血糖 |
| cancer | 1 | 医生曾告知癌症或恶性肿瘤，排除轻微皮肤癌 |
| lung_disease | 1 | 慢性肺病限制日常活动或需居家氧疗 |
| heart_failure | 1 | 医生曾告知充血性心力衰竭 |
| current_smoker | 1 | 过去一周吸过香烟 |
| bathing_difficulty | 1 | 因健康或记忆问题，洗澡或淋浴有困难 |
| finances_difficulty | 1 | 因健康或记忆问题，付账单、记录开支等有困难 |
| walking_difficulty | 1 | 因健康问题，步行数个街区有困难 |
| pushing_difficulty | 1 | 因健康问题，推拉客厅椅子等大件物品有困难 |

不从化验值推断诊断，不把所有肺病自动记为是，不将步行数个街区换成固定距离。需要帮助或不能完成的功能应按对应问句核实；仅仅不做某活动且原因不明时补问。

输出 `out/report.md`、`out/result.json` 和 `out/levers.json`。报告先列论文卡片，再列12项得分与总分对应的表4验证队列观察比例。≥14分共用最后一行，不外推、不平滑、不生成置信区间或个人预期寿命。

用户明确提供目标时，在同一命令加 `--targets targets.csv`，列格式相同，只需填想比较的项。允许BMI、吸烟和4项功能指标；年龄、性别、既往诊断和居住场景不可作为目标。每项单独和全部同时代入，给出分数与查表百分数的变化。不推荐任何目标；BMI低于25加分不代表增重有益，病史不可因控制改善而清零。

`levers.json` 的敏感度是离散比较：二元项翻转，年龄比较下个计分档，BMI比较25或24.9；它不是连续导数。非可改变项也显示其评分影响，但标记不可设目标。最高年龄档无下一个年龄切点。表4在11分至12分不单调，原样保留。

验证暂定：表3逐项和表4各行测试通过；正文78岁女性示例却使用3分年龄权重，与表3的75–79岁4分不符。严格预期失败测试保存论文印出的总分6，不修改年龄权重来迎合示例。JAMA勘误只纠正Box中糖尿病为1分。详见 [合同](references/contract.md) 和 [证据核对](references/claims.md)。

每份报告（含输入失败）必须保留：

> 边界: 本结果是美国社区居住、50岁及以上人群的历史观察性风险分层，不是个人寿命预测，也未在当代中国人群或机构照护人群中验证；不能据此开始或停止药物、筛查或治疗。目标模拟只反映模型变化，不能解释为干预能减少的死亡风险，不能把BMI阈值当作增重目标。
