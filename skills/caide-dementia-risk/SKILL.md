---
name: caide-dementia-risk
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example.
  根据中年年龄、性别、教育年限、收缩压、BMI、总胆固醇与闲暇活动计算原版CAIDE痴呆风险积分、队列分组比例及连续公式估计，可选已有APOE状态的模型。用于询问中年痴呆风险或比较自定目标情景。
---

# CAIDE中年痴呆风险评分

用户命令：`用我的中年体检和活动问卷计算CAIDE痴呆风险评分，并比较我提供的目标。`

使用 Kivipelto 等，The Lancet Neurology，2006 年原版模型。输入类型为常规体检、血压和问卷；模型2另需已有的APOE ε4携带状态。仅接受评估时39–64周岁，数据应属于同一次中年评估。

准备 `marker,value,unit` 三列表；五个必需项目为：

| marker | 含义 | unit |
|---|---|---|
| education_years | 已完成教育整年数 | a |
| sbp_mmhg | 坐位休息后收缩压 | mmHg |
| bmi_kg_m2 | BMI | kg/m^2 |
| total_cholesterol_mmol_l | 总胆固醇，不能用LDL替代 | mmol/L |
| active | 符合原文活动定义=1，否则=0；未知留空 | 1 |

活动定义是闲暇体力活动每周至少两次、每次至少20–30分钟，达到出汗和气喘的程度。不能用每天步数、轻家务或现代活动问卷总分直接替代。年限按完成的整年填报，不对小数自动取整。

执行：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 53 --sex female --out out
```

默认 `--model 1` 不需要基因检测。只有用户明确选择含APOE的版本且已有结果时，使用 `--model 2`，并在测量表加入 `apoe_e4,0,1`（已知非携带者）或 `apoe_e4,1,1`（至少携带一个ε4）。未知不按0处理，不要求用户为了运行去做基因检测。模型2改变多个项目权重，不能只在模型1上加APOE分。

如用户已有目标，添加 `--targets targets.csv`；列格式相同，只接受收缩压、BMI、总胆固醇和活动状态的部分目标。脚本不会推荐目标，年龄、性别、教育年限与APOE不作为目标。

成功生成中文 `out/report.md`、`out/result.json` 和 `out/levers.json`。阶梯积分的敏感度按跨类别的精确差表示，不把阈值附近的变化当作平滑导数。缺项、错单位、超范围或类别错误时退出3并写 `out/problems.json`，由助手解释需补什么；不补零、不猜测。

不向用户索要论文PDF、补充表、队列数据或作者代码。常数已冻结在 `scripts/presets.py`；来源和实现范围见 `references/contract.md`、`references/claims.md`、`references/sources.md`。

报告开头保留论文卡片。清楚区分表3的原队列分组发生比例与正文连续公式的估计：两者可能不同；组置信区间不属于个人。表3模型2的低风险组置信下限为负，按原表保留并解释，不能解释为负概率。不得把模型输出说成当代中国人的已校准绝对风险。

每份报告必须保留原句：

> 边界：这是芬兰中年人队列的风险模型，适用背景是存活到约20年后复查的人群；不用于诊断痴呆，也不能保证个人未来是否患病。目标情景只是模型重算，不代表改变指标就能获得相同风险降幅；不能据此开始、停止或调整药物。
