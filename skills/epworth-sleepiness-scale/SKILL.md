---
name: epworth-sleepiness-scale
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes the original Epworth Sleepiness Scale total from eight completed adult
  questionnaire item scores. Use when a person wants ESS scoring or a daytime sleepiness readout from
  their own responses. Produces a Chinese report and structured results without diagnosing a sleep
  disorder or estimating lifespan.
---

# Epworth 日间嗜睡量表计分

用户命令：`用我已完成的ESS问卷八项分数计算总分，生成中文报告。`

接收成年人已完成问卷的八个单项分数，每项为 0–3 的整数。字段以原文表 1 的顺序编号；中文简称只用于核对数据，不是经过验证或获授权的中文版问卷。问卷应通过适当授权的来源取得，不把本技能的字段表当成新问卷发放。

## 输入与执行

将用户给出的分数整理为 `marker,value,unit` CSV：`marker` 为 `ess_item_1_score` 至 `ess_item_8_score`，`value` 为其本人作答对应的分数，`unit` 为 `score`。可识别 `ESS1` 至 `ESS8` 及 manifest 中的中文字段名。不要把只有一个总分的报告拆成八项，不填补缺项。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

可选 `--age` 与 `--sex` 是上下文，不参与计分。年龄只接收成人；原文患者为 18–78 岁，超出该上界会提示适用性限制。性别可填男、女、其他、未知或相应英文。

- 八项齐全且输入合法时，输出 `out/report.md` 与 `out/result.json`，列出单项及总分。
- 缺项、错单位、超范围、非整数或文件错误时，退出码为 3，输出 `out/problems.json` 与含论文卡片的错误报告；先让用户核实指出的项目，再重跑。
- 评分反映近期通常生活中的入睡倾向，不是疲劳、睡眠时长或此刻困倦。原文未固定精确回忆天数；不擅自改成过去一周。未经历某情境的回答由本人根据原问卷估计，不能代答为零。

## 报告规则

报告开头保留论文卡片，再给个人结果。仅把单项分数相加，不加年龄或性别权重，不输出轻中重诊断分档，也不使用原文的组水平回归去预测个人呼吸紊乱指数、血氧或睡眠潜伏期。

保留边界句：

> 边界: ESS 衡量近期通常生活中的自报日间入睡倾向，不是诊断；不能据此判断特定睡眠疾病、驾驶安全、衰老速度或个人寿命，也不据此开始、停用或调整药物。

无需用户寻找论文、补充表或代码，也无需上传睡眠监测报告。运行全程离线。它是自报症状评分，不提供 `--targets` 或把降低作答分数解释为健康改善的敏感度模型。

方法与验证边界见 [references/contract.md](references/contract.md)；核对来源、研究人群和版本差异见 [references/claims.md](references/claims.md)。
