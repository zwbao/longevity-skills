---
name: sleep-neurovascular-csf-contrast
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes a conditional NREM cerebrospinal-fluid power contrast from frontal EEG
  and global gray-matter BOLD power ratios using published mediation slopes. Use for research EEG/fMRI
  records collected with matching acquisition and processing in the same age group, when a person asks
  about sleep-related CSF power differences. Does not estimate brain age, clearance, or dementia risk.
---

# NREM 神经血管模型的脑脊液功率对比

用户命令：

> 用我同年龄组两份同步 EEG/fMRI 的 NREM 功率，比较脑脊液功率的模型差，并说明边界。

仅当已经拿到研究级功率数据时调用。Bailes 等，Nature Aging，2026
（DOI 10.1038/s43587-026-01270-4），人体横断面研究。

## 输入

两份记录都必须按论文流程处理，都是 NREM；方向统一为比较记录/参照记录。
不是清醒与睡眠的对比，不用手环、睡眠分期比例或常规 MRI 报告替代。

CSV 表头 `marker,value,unit`：

- `eeg_nrem_power_ratio`：额叶七电极平均的 0.5–4 Hz 慢波线性功率比。
- `bold_nrem_power_ratio`：全灰质 0.01–0.1 Hz BOLD 线性功率比。
- 单位 `1`，或 `%`（100% 表示相等，非增加100%）。线性功率先按论文汇总后取比。

若原报告已经给出 dB 功率，先由 agent 用脚本按
`10 ** ((比较记录dB - 参照记录dB) / 10)` 得到比值。
禁止把 dB 数直接填进比值列，禁止对 dB 数做相除。
完整数据处理要求见 [contract.md](references/contract.md)。

两次记录时的年龄分别传 `--age` 和 `--reference-age`。两者须同属
18–39 岁或 60–83 岁；拒绝研究未覆盖的中年及跨组比较。
`--sex` 仅作背景，不改变结果。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --age 23 --reference-age 23 --out out
```

目标情景可加 `--targets targets.csv`，表头同上，允许只给一个功率比。
目标仍是相对同一参照记录的比值，不代表可通过生活方式实现的目标或疗效。

## 输出

`out/report.md` 先给论文卡片，再给 EEG、BOLD 功率差及相应条件模型项和
CSF 模型功率差（dB）；`result.json` 保存全部读出。
`levers.json` 保存当前点敏感度；有目标时包含单项及合并目标的模型差。

缺项、错单位、越界或不支持的年龄组合：退出码3并写 `out/problems.json`，
告诉用户缺的是哪项个人测量，不用零填补；不产生计算结果。

无需用户查找论文、补充材料、HRAN、源数据或队列数据：表3系数已冻结。
本技能不读取原始 EEG、DICOM、NIfTI、PDF，不代做影像预处理。

## 解读与边界

正负只表示比较方向，无正常/异常切点。路径乘积的复现不等于个人预测经过验证。
绝对 CSF 功率所需的截距未印出，且没有个人预测区间所需的完整误差参数；不估算它们。
同年龄组差分使截距与年龄组项抵消，不能把年龄组效应按每岁解释。
论文未验证个人纵向变化或干预因果效果。

报告必须原样保留：

> 边界：这是横断面研究模型在同年龄组、同测量流程下的条件功率对比，不是个人实测脑脊液流量、废物清除效率、脑龄或痴呆风险，也不能预测改善睡眠或任何干预的效果；不能据此开始或停止药物。

方法和验证见 [contract.md](references/contract.md)，研究核查见
[claims.md](references/claims.md)，材料清单见 [sources.md](references/sources.md)。
