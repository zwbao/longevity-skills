---
name: schonberg-mortality-index
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes the original Schonberg mortality index from eleven self-reported factors
  and looks up five-year mortality in the published validation cohort. Use when a community-dwelling
  adult aged 65 or older asks about the Schonberg score or questionnaire-based mortality risk. Reports
  Chinese explanations, per-factor points, grouped risk and confidence limits, and optional
  user-specified scenarios.
---

# Schonberg 五年死亡风险指数

用户命令：用我的年龄、性别和健康问卷计算 Schonberg 五年死亡风险指数，并解释对应的风险档位。

适用于能自行回答的65岁及以上社区居住者。开始前确认居住情况及有无痴呆；养老机构居民、痴呆患者、需代理回答者不应用本方法。若情境不明，先核实，不把代理回答当本人自报。风险来自美国历史队列，不能直接作为其他国家或当前时期已经校准的概率。

## 运行

```bash
python3 scripts/personal_report.py --measurements my-health.csv --age 80 --sex female --out out
```

测量表使用 `marker,value,unit` 三列。填写本人的已知情况；不清楚的项目不要填零。年龄是已满周岁整数；性别按论文使用的二分类传入 `male/female` 或 `男/女`。这里只用已算好的 BMI，不把身高或体重直接当作 BMI。

| marker | 单位 | 应填写的数值与问题范围 |
|---|---|---|
| bmi_kg_m2 | kg/m^2 | 体质指数 |
| health_code | 1 | 0=极好/很好；1=好；2=一般/差 |
| copd_history | 1 | 医生曾告知肺气肿或慢性支气管炎：0=否，1=是 |
| cancer_history | 1 | 医生曾告知癌症：0=否，1=是；不含非黑色素瘤皮肤癌 |
| diabetes_history | 1 | 医生曾告知糖尿病（包括原问卷的临界糖尿病）：0=否，1=是 |
| iadl_help | 1 | 因身体、精神或情绪问题，家务、办事、购物或外出等至少一项需他人帮助：0=否，1=是 |
| walking_difficulty | 1 | 独自、不用辅助设备步行四分之一英里（约三个街区）：0=完全不困难，1=任何困难、不能走或不走 |
| smoking_code | 1 | 0=从未（终生少于100支）；1=既往；2=目前每天或部分日子吸烟 |
| hospitalizations_count | 1 | 过去12个月过夜住院的整数次数，不是天数 |

分类数值是输入编码，不是积分。原题措辞及计分来源见 [contract.md](references/contract.md)。输入名称支持 `skill.json` 中列出的中英文别名。运行无需联网，也不向用户索要论文、附录、NHIS数据或任何训练文件。

## 目标情景

有用户指定目标时，加 `--targets targets.csv`；表头相同，仅填要比较的项目。可比较 BMI、自评健康、日常事务帮助、步行困难、吸烟状态和住院次数。年龄、性别及既往诊断不作为目标；已有吸烟史不能改为“从未吸烟”。住院次数表示另一个观察时间窗的情景，不能抹去已发生的住院。

不自行生成“最佳目标”。阶梯式评分用离散档位比较表示敏感度，不估计连续导数；单项变化不能简单相加为联合风险变化。报告中明确情景不是因果效果，BMI切点不是增重建议，也不应为了评分避免必要住院。

## 输出与核对

- `out/report.md`：中文论文卡片、逐项积分、总积分、验证队列同档五年风险和该档95%置信区间、边界。
- `out/result.json`：上述个人数值与风险档位。
- `out/levers.json`：当前结果、全部计分因素的离散档位敏感度；提供目标时另有逐项和联合替换结果。
- 缺项、错单位、非整数类别、不合理范围或不可识别内容：退出码3，写 `out/problems.json` 和含论文卡片的未计算报告，清除旧结果。

论文讨论中的无其他风险因素女性病例、第二个多因素病例、表2所有类别及表3全部验证队列档位均有测试；见 [claims.md](references/claims.md)。这里复现的是公开积分及风险查表，不是重新拟合 Cox 模型。

每份报告必须原样保留：

> 边界：这是美国社区居住、可自报健康状况且无已报告痴呆的65岁及以上人群的历史队列分档估计，不是个人剩余寿命或因果干预效果；不适用于养老机构居民或痴呆患者，不能据此开始或停止药物、筛查或其他治疗。
