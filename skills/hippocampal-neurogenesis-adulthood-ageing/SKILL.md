---
name: hippocampal-neurogenesis-adulthood-ageing
description: >-
  Tier B lookup (human): what the paper reports about named entities, not a validated personal score.
  Checks a supplied age and episodic-memory comparison against the SuperAger enrollment definition
  (age 80 or older, episodic memory at least that of 50 to 59 year olds) used in Disouky et al.,
  Nature 2026. The paper's findings come from single-nucleus profiling of post-mortem hippocampus,
  which no living person can measure, so this is a definition check, not a personal neurogenesis
  estimate. Use when the user mentions hippocampal neurogenesis, SuperAgers, immature neurons, or this
  Nature paper. Medicines and checkup labs do not change that check. The report does not say what to
  start or stop.
---

# 情景记忆对照

用户交现用药、体检、年龄，以及情景记忆是持平或更好、更差，还是未知。不要向用户要 GEO、STRING 或 PDF。

论文的结论来自死后脑组织，活人测不了海马神经发生；这里只是定义核对，不是个人的神经发生估计。年龄和记忆给全时，报告只核对是否符合 SuperAger 的入组写法。记忆写未知时名单是空的；缺年龄或记忆时不核对，报告写明缺什么。药名对不上时保留「不能据此停」。体检不增删方法算出的名单。

## Command

```bash
python "$SKILL/scripts/personal_report.py" \
  --medications meds.txt \
  --labs checkup.csv \
  --age 82 \
  --memory equal_or_better \
  --out out/
```

`--age` 和 `--memory` 都要给。`--memory` 取 `equal_or_better`、`below` 或 `unknown`；写 `unknown` 时报告不判断。缺一项、年龄不在 18–110 岁之间或 `--memory` 不是这三个词时不核对：报告写明原因，脚本退出码 3。`skill.json` 列出这两项。`out/result.json` 写出 `superager`（符合或不满足；unknown 时为空）。

把 `out/report.md` 整段交给用户，包括最后一行 `边界:`。
