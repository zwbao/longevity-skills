---
name: itfnat-face-name-mci-cutoff
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Compares a person's own Italian Face-Name Association Test (ItFNAT) delayed free
  recall score and MoCA total score, both already adjusted with the Italian norms, with the mild
  cognitive impairment cut-offs of Scaramuzzi et al. (GeroScience 2026, Table 4: DFR <= 3.21, MoCA <=
  23.99) and reports which side of each cut-off the score falls on and the likelihood ratio for that
  side from the printed sensitivity and specificity. Use for 人脸姓名联想记忆, 人脸-姓名测验, ItFNAT, face-name
  test, MoCA 切点, 轻度认知障碍筛查, 记忆力下降. Does not convert raw scores, does not give a probability of MCI and
  does not diagnose.
---

# ItFNAT 延迟自由回忆与 MoCA 的轻度认知障碍切点

用户交自己神经心理报告上的两个校正分（至少一项）：ItFNAT 延迟自由回忆（DFR）校正分、MoCA 校正总分。不要向用户要论文、常模表或原始答题记录，切点和灵敏度、特异度已经在技能里。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements scores.csv --out out
```

`scores.csv` 的列是 `item,value,unit`，unit 写 `score` 或留空：

- `ItFNAT DFR adjusted`（也认 延迟自由回忆校正分、DFR校正分、DFR punteggio corretto 等）
- `MoCA adjusted`（也认 MoCA 校正分、MoCA 校正总分、MoCA punteggio corretto 等）

分数必须是论文用的校正分：ItFNAT DFR 按 ItFNAT 意大利常模做年龄校正，MoCA 按意大利 MoCA 8.1 常模做年龄和教育校正。只写 `MoCA`、`DFR` 而没写“校正/adjusted”的行会被当作原始分拦下，报告说明要什么；中文版 MoCA 原始分不能套这个切点。超出范围、单位不对、一项也没有时不计算，脚本退出码 3。

报告给出每个分数在切点哪一侧，以及按表 4 灵敏度、特异度算的那一侧的似然比（DFR 阳性 3.086、阴性 0.497；MoCA 阳性 2.340、阴性 0.485）。`out/result.json` 给出 `dfr_cutoff_result`、`dfr_likelihood_ratio`、`moca_cutoff_result`、`moca_likelihood_ratio`。两项不合并，不算患病概率。

## 报告里必须保留的话

- 切点来自意大利南部 136 人的小样本，论文自己说应视为初步；只适用于意大利常模校正分。
- 结果是筛查线索，不是轻度认知障碍或痴呆的诊断；担心记忆下降，请到神经内科或记忆门诊做完整评估。

引用 `out/report.md`，包括 `边界:` 那一行。来源和核对见 [references/contract.md](references/contract.md)，论文说法与技能实现的对照见 [references/claims.md](references/claims.md)。
