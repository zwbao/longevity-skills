---
name: lifes-essential-8
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates adult Life’s Essential 8 cardiovascular health scores from a completed
  MEPA diet score, activity, nicotine exposure, sleep and routine measurements. Use for an adult
  asking about LE8, 心血管健康八要素, or changes in these scores. Supports explicit target scenarios; does not
  estimate disease risk or prescribe treatment.
---

# 成人 Life’s Essential 8

依据 Lloyd-Jones 等，Circulation 2022。用户命令：

> 用我的饮食问卷、运动睡眠和体检数据算成人 LE8 心血管健康评分，并比较我给出的目标。

收集 `marker,value,unit` CSV，按 [输入说明](references/inputs.md) 核对编码、测量时期与单位。饮食需要已完成的成人 16 项 MEPA 总分，不从自由描述猜分。用户不必寻找论文、补充表、NHANES 或代码，规则已冻结在 `scripts/presets.py`。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 75 --out out
```

用户明确给出目标时加 `--targets targets.csv`，格式相同，仅含要改变的指标；可选 `--sex` 仅记录上下文。不能把用药状态、糖尿病史或祖源评分尺度当作改善目标。运行前阅读 [合同与边界](references/contract.md)；需要查来源时阅读 [证据核查](references/claims.md)。

成人规则从 20 岁开始。必须具备八项评分所需的数据；缺项不补零，也不计算部分均值。糖尿病患者必须有 HbA1c。低体重、未确诊但血糖超过无糖尿病分支范围、两个血糖指标分档不一致时，返回需核实事项。不能自动替医生判断。

输出为中文 `out/report.md`（以论文卡片开始）、`result.json` 和 `levers.json`。输入有误时退出 3，写 `problems.json`，结果值为 null，不产生情景结果。以 problems 中的具体原因解释还缺什么测量或信息。

报告必须原样保留：

> 边界：这是心血管健康评分，不是个人患病概率、寿命预测或治疗建议；目标情景只是同一算法的重算，不能据此开始、停止或调整药物。

不得把提高分数解释为延寿或减少疾病的确定收益，不建议剂量，不把治疗扣分解释为停药理由。
