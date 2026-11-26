---
name: gad-7
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates GAD-7 item scores, total, anxiety symptom severity and screening
  cutoff status from seven personal answers about the past two weeks. Use for GAD-7 scoring, 焦虑自评,
  广泛性焦虑筛查 or 焦虑症状程度 when questionnaire responses are available.
---

# GAD-7 焦虑症状评分

使用 Spitzer 等在 Archives of internal medicine（2006）发表的原始计分法。
请本人回答过去两周各问题困扰自己的频度，再将七题写入 `marker,value,unit` 表：

```bash
python3 scripts/personal_report.py --measurements measurements.csv --out out
```

## 收集回答

每题均选择：**0 完全没有；1 有几天；2 超过一半的天数；3 几乎每天**。
不要自行把“有几天”改成原文没有规定的精确天数区间。
以下为解释性翻译，不声称是经验证的正式中文版；需要正式中文版时应使用经核对的译本。

| marker | 过去两周的困扰 | unit |
| --- | --- | --- |
| gad7_item_1_score | 感到紧张、焦虑或坐立不安 | score |
| gad7_item_2_score | 无法停止或控制担忧 | score |
| gad7_item_3_score | 对各种事情担忧过多 | score |
| gad7_item_4_score | 难以放松 | score |
| gad7_item_5_score | 烦躁不安，难以静坐 | score |
| gad7_item_6_score | 容易烦恼或易怒 | score |
| gad7_item_7_score | 感到害怕，仿佛会有可怕的事情发生 | score |

七题须齐全，每题一个整数；未知、漏答不能补零，不收平均分或仅有总分的输入。
用户的原回答若为文字，助手按上面四种频度确认后填入对应分值。
不要从聊天中自行推断分值，也不要让家属代替本人完成自评。
原图中的功能困难附加题可作为交流背景，不是第八个计分项。

`--age`（岁）和 `--sex` 可选，仅用于上下文和年龄适用范围提示，不改变计分。
研究对象年龄为18–95岁；超出时报告提示证据外推。
此技能是症状量表，不是干预预测模型，不提供 `--targets` 或治疗收益估算。

## 读取报告

读取 `out/report.md` 和 `out/result.json`，报告先放论文卡片，再给逐项分、总分、
症状分档和筛查切点状态。计分常数集中在 `scripts/presets.py`。
原文表2重度行与表3、讨论有冲突；采用后两处一致的定义，核查记录见 references。
量表既不包含自伤风险问题，也不能用低分判断一个人没有心理风险。

退出码3表示输入有问题。读取 `out/problems.json`，说明缺哪题或哪个值、单位不合法，
补齐后再运行；错误报告不输出分数，旧的结果文件会清除。

运行离线，不向用户索要原文、补充表、研究队列、代码或化验单。
不把研究的灵敏度、特异度、阳性预测值或功能受损均值解释为这个人的概率或未来结果。
验证复现了图1的逐项分值和原文总分端点；未声称拥有论文患者的完整记录。

每份报告保留：

> 边界: GAD-7 只用于焦虑症状筛查和程度分档，不能单独确诊或排除广泛性焦虑障碍，也不估计个人患病概率、生物年龄或寿命；本研究验证对象为美国基层医疗成年患者，中文题干为解释性翻译，其他语言和人群的适用性需另行核对；不能据此开始、停止或调整药物。
