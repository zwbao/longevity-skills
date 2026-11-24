---
name: calvarial-bone-marrow-adiposity
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. Estimates calvarial bone marrow T1 signal from a person's MRI-derived intensity matrix
  using the published neural-network weights and scan quality controls. Use for 颅骨骨髓脂肪、头部MRI骨髓信号 or a
  boneMarrowLocalisationT1wMRI layers file. Requires author-preprocessed image measurements; outputs a
  semi-quantitative signal proxy, without converting it to fat fraction, age or disease risk.
---

# 颅骨骨髓信号

依据 Kaufmann 等，eLife，2026，doi:10.7554/elife.101499。

```bash
python3 scripts/personal_report.py --layers /path/to/my_layers.csv --intensity-unit score --layer-spacing-mm 0.5 --age 65 --sex female --out out
```

需要安装 `scripts/requirements.txt`。输入必须为本人的 T1 加权 MRI 经作者的 FreeSurfer 预处理和强度提取流程生成的矩阵：分号分隔、无表头，N×50 或 50×N；每层相距 0.5 mm，覆盖皮肤表面向内 25 mm。强度使用 `nu.mgz` 的 0–255 尺度。`score` 是此信号尺度的机器可读单位，不能填百分比、T1 弛豫时间或自行归一化为 0–1 的数据。

`--age`、`--sex` 可省略，仅记录背景；不改变计算。默认分层间距为 0.5 mm，其他间距会被拒绝。没有可用于个人目标优化的输入，不提供 `--targets`。

用户只有原始影像时，先说明需要影像处理环境，并按 [预处理说明](references/preprocessing.md) 生成个人矩阵。本入口不直接分割 DICOM/NIfTI、不读取影像文字报告，也不把用户报告中的骨密度代入模型。缺少个人矩阵时运行入口会输出缺项说明。不得向用户索要公开权重、论文、补充表或研究队列；模型随技能提供。

先检查输入、位点数量，再运行原始 SavedModel 并检查外板标准差及马氏距离异常比例。缺失、格式错误、单位错误、范围错误或质控失败时退出 3，写 `out/problems.json` 和中文报告，不输出个人骨髓指标。运行环境或模型完整性问题退出 2，不能把这类问题说成患者缺少测量。

成功输出 `out/report.md`、`out/result.json`、`out/qc.json` 和 `out/vertices.csv`。后者保留原始位点编号及层边界，便于影像人员核对；不生成无空间坐标的伪三维定位图。

报告必须以论文卡片开始，明确 draft、预处理要求和跨扫描比较限制。必须原样保留：

> 边界：这是头部磁共振骨髓信号的半定量代理指标，不是脂肪百分比、生物年龄或骨质疏松诊断；不能据此开始、停止或调整药物。

方法、参数来源与未完成的验证见 [合同](references/contract.md)，全文及补充材料核查见 [证据核查](references/claims.md)。
