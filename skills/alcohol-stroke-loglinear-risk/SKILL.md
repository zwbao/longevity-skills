---
name: alcohol-stroke-loglinear-risk
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Compares two personal pure-alcohol intake scenarios using the published male
  stroke log-linear associations from the China Kadoorie Biobank. Use when an adult man asks how
  different alcohol intake amounts compare for stroke, or provides a target intake. Reports relative
  risks and coefficient uncertainty, not personal absolute risk or an intervention effect.
---

# 饮酒量情景与卒中相对风险

用户命令：**“用我的纯酒精摄入量和比较情景，算卒中相对风险；如果我提供目标，也算目标情景。”**

读取 [skill.json](skill.json) 后运行 `scripts/personal_report.py`。
参数为 `--measurements intake.csv --age 50 --sex male --prior-cvd 0 --out out`；
有用户自己提供的目标时才加 `--targets targets.csv`。

输入 CSV 表头 `marker,value,unit`，两项均必需：

| marker | 含义 | unit |
| --- | --- | --- |
| alcohol_g_day | 当前平均每日纯酒精克数 | g/d |
| reference_alcohol_g_day | 用户选定的比较情景平均每日纯酒精克数 | g/d |

按所有日历日取平均，不是只算饮酒日。已知每周纯酒精克数时精确除以 7；
保留足够小数。单位仅接受 `g/d`，其他单位的 `accept` 为空。
杯、瓶、两、毫升酒水不能直接当纯酒精克数。不得自行假定酒精密度、杯容量或酒精度。
只有酒水体积而没有可核对的纯酒精克数时，说明还缺纯酒精量，暂不计算。

`--age` 和 `--sex` 必需。实现仅支持 30–79 岁男性，年龄不进入方程。
`--prior-cvd` 必需：0 表示无既往冠心病、卒中或短暂性脑缺血，1 表示任一有。
病史未知时不能默认填 0；有病史时本方法不计算。
不向用户索取论文、附录、CKB 队列或基因原始文件；系数已经从原始材料冻结。

目标 CSV 使用相同表头，只允许 `alcohol_g_day`，比较情景固定。
不替用户选择饮酒目标。`levers.json` 始终包含当前输入处的敏感度；
提供目标时再包含目标结果和单独改变当前摄入量的差异。

输出 `out/report.md`、`out/result.json`、`out/levers.json`。
缺项、错误单位、非法数值、超出输入合理范围或不适用人群时退出 3，
写 `out/problems.json` 及含论文卡片的中文说明，删除同一路径旧结果。
摄入量超出附录类别均值 4–255 g/周时仍可做方程换算，但必须展示外推提示，不能称为经过验证的风险预测。

报告必须先显示论文卡片，然后列当前情景相对比较情景的缺血性卒中、脑内出血和总卒中 RR。
总卒中是单独发表的结局，不能将两个亚型相加或相乘。
保留系数传播区间、长期暴露与个人短期改变的区别，以及所有外推提示。
不生成心肌梗死保护结论、绝对发病概率、安全阈值、饮酒处方或药物剂量。

每份报告保留边界原句：

> 这是中国男性人群遗传研究的对数线性情景换算，不是个人发病概率、短期改变饮酒后的效果预测或安全饮酒阈值；不适用于女性或既往心脑血管病者，不用于诊断或用药决策，不能据此开始、停用或调整药物。

方法、验证和来源见 [references/contract.md](references/contract.md)、
[references/claims.md](references/claims.md)、[references/sources.md](references/sources.md)。
