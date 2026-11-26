---
name: stop-bang
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Calculates the original 2008 STOP and STOP-Bang affirmative-answer scores and binary
  obstructive sleep apnea screening categories from personal questionnaire answers, BMI, neck
  circumference, age and sex. Use for STOP、STOP-Bang、打鼾、 睡眠呼吸暂停筛查 or an adult preoperative screening
  readout.
---

# STOP 与 STOP-Bang（2008 原版）

用户命令：**“用我的四项睡眠问卷回答、BMI、颈围、年龄和性别，计算原版 STOP 与 STOP-Bang。”**

根据 Chung 等，Anesthesiology，2008，108(5):812–821 的文内附录计分。
输出两项总分、八个分项和各自的高/低风险档。此版本没有中间风险档。
研究对象为加拿大两家医院的成人术前患者，排除了已确诊睡眠呼吸障碍者；
不能将结果用于监测已确诊者的治疗效果。

## 收集输入

用中文确认下列问题的含义，回答编码为是=1、否=0；不知道或无人能够确认时保持缺失。
中文说明是本技能的释义，并非另行验证的中文量表。

| CSV marker | 要确认的内容 | unit |
| --- | --- | --- |
| snoring_binary | 是否大声打鼾，声音超过说话声或隔着关门仍可听见 | 1 |
| tiredness_binary | 白天是否经常疲劳、倦怠或困倦 | 1 |
| observed_apnea_binary | 是否有人看到睡眠中停止呼吸 | 1 |
| hypertension_binary | 是否有高血压，或正在接受高血压治疗 | 1 |
| bmi_kg_m2 | 本人的BMI | kg/m^2 |
| neck_circumference_cm | 实测颈围；原研究由工作人员测量 | cm |

高血压已治疗且当前血压正常仍回答是。不要将“未知”转成否。
颈围也接受 mm、m、in，单位按清单精确换算；S/M/L 衣领尺码不能代替实测。
年龄以岁传入 `--age`，性别以 `male/female` 或 `男/女` 传入 `--sex`。
原论文性别项只有二元编码；未知或无法套用原题项时停止，不推定非男性。
这次命令同时计算两套问卷，所有输入都必需，缺项时不出部分评分。

## 执行

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 50 --sex female --out out
```

CSV 表头为 `marker,value,unit`。年龄与性别示例必须换成本人的信息。
无需联网，不向用户索要论文 PDF、研究队列、补充表或源代码。

成功时读取 `out/report.md` 与 `out/result.json`。
缺项、单位不符、超范围、非二元回答或非法资料时，退出码为3，
读取 `out/problems.json` 告诉用户需要确认或补测哪项，不自动补值。
报告以论文卡片开始，并展示各项与总分；低风险不表示排除疾病。

## 版本与验证

切点统一在 `scripts/presets.py`：STOP 肯定项至少2项、STOP-Bang 至少3项为高风险；
BMI >35 kg/m²、年龄 >50岁、颈围 >40 cm，各自独立计一个肯定项，等号不计。
不混用后来版本的三档分类、不同颈围阈值或BMI阈值。

验证状态为 draft：全文没有可复算的个人输入/总分实例；
现有测试核对原文分档规则、严格不等号、单位和错误输入，不能称为复现个人实例。
这是筛查计数，不是用于设定减重、颈围或用药目标的因果模型，因此不提供 `--targets`。

每份报告保留以下原句：

边界: STOP 与 STOP-Bang 是阻塞性睡眠呼吸暂停筛查工具，不能确诊或排除疾病，不能估计个人患病概率、严重程度或手术安全性；本研究验证对象是术前成人，其他人群的适用性需另行评估；不能据此开始、停止或调整药物。
