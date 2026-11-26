---
name: smoking-cessation-mortality-lookup
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example.
  按男性当前年龄、吸烟史和戒烟年龄匹配英国医生队列已发表的死亡率与戒烟组近似寿命差。用于询问吸烟史对应的历史队列死亡率、不同戒烟年龄的研究结果；不预测个人死亡概率或剩余寿命，不用于女性、电子烟或混合烟草模式。
---

# 吸烟史与死亡率查表

读取 [产品合同](references/contract.md) 和 [来源核查](references/claims.md)。离线查表只用 Doll 等 BMJ 2004 的表5、图4图注及其正文概括，数据已在 `scripts/presets.py` 冻结。

## 一条命令

```bash
python3 scripts/personal_report.py --measurements smoking-history.csv --age 65 --sex male --out out
```

`smoking-history.csv` 的列是 `item,value,unit`。例如：

```csv
item,value,unit
smoking_history_code,2,1
quit_age_years,50,a
```

这是问卷数据，不需要化验。先核实实际吸烟模式，再由助手编码：

- `0`：终生不吸烟。按论文定义，不能曾在一年内大多数日子吸烟。
- `1`：持续仅吸卷烟，当前仍吸烟。
- `2`：曾持续仅吸卷烟，现在已戒烟；必须填写真实 `quit_age_years`。
- `3`：其他、混合烟草、电子烟、复吸或间歇模式；脚本报告不支持并退出3。不清楚模式时先补问，不能强行归入1或2。

当前年龄必须在35岁至85岁生日之前，性别必须明确为男性。戒烟者的戒烟年龄须在25岁至65岁生日之前且不大于当前年龄；接受年 `a` 或月 `mo`（除以12）。未戒烟者省略戒烟年龄，不填0。中文、英文别名在 `skill.json`，不提供不确定的LOINC。

不要向用户索要全文、表格、作者图件或队列原始数据。作者图表下载有失效链接，核查状态已记录；本查表的全部常数均来自可读全文。

## 结果及缺项

- `out/report.md`：中文论文卡片、匹配组、历史队列参照及边界。
- `out/result.json`：表5原始死亡率、队列死亡数、持续吸卷烟/不吸烟的原表比值，以及已戒烟组的近似寿命差。
- 缺项、错误单位、超范围、矛盾或不支持的输入：退出3，写 `out/problems.json` 和有论文卡片的说明报告；数值输出全部为null。

原表空格不是输入错误：同一戒烟年龄段的死亡率，以及25–34岁戒烟组未列出的表5死亡率，保持null；已印出的图4组别说明仍可输出。不要填0、插值、外推或套用邻近组。

这是既往史的描述性查表，不是可改变输入后推算个人获益的模型；没有 `--targets`。不把已发生的戒烟年龄当作可调整目标，不生成个人敏感度、剩余寿命或生存曲线。图4的近似寿命差属于整个历史戒烟组，不能说成“你现在还能多活几年”。

报告必须原样保留：

> 边界: 本结果仅为1900–1930年出生、1951–2001年随访的英国男性医生队列参考，不是你的死亡概率、剩余寿命或个人戒烟获益预测；不适用于女性或其他烟草使用模式，不能据此开始或停止任何药物。
