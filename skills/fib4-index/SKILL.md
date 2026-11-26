---
name: fib4-index
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. 根据年龄、AST、ALT 和血小板计算 FIB-4 指数，按 Shah 等成人非酒精性脂肪肝研究的切点分档。用于用户询问
  FIB-4、脂肪肝的肝纤维化指标，或提供相关化验时；可展示指定化验值的数学情景，不输出个人患病概率或治疗目标。
---

# FIB-4 指数

用户命令：`用我的年龄、AST、ALT 和血小板算 FIB-4，解释论文分档。`

先取得采样时年龄及同次检查的 AST、ALT、血小板。只收用户自己的数据；不要向用户索要论文、补充表或研究队列。适用背景为成人非酒精性脂肪肝；本方法不能诊断脂肪肝本身。

将化验整理成 `marker,value,unit` CSV 后运行：

```bash
python3 scripts/personal_report.py --measurements labs.csv --age 50 --out out
```

这里的年龄仅为命令格式示意，运行时换成用户的实际年龄。AST、ALT 使用 U/L（支持 IU/L、ukat/L），血小板使用 10^9/L（支持 10^3/uL、/uL）。别名行必须写单位；带单位的规范键可省略单位列的值。缺项、非数值、单位错误或超范围时退出 3，查看 `out/problems.json`，请用户核对而不是填补。

如用户明确指定假设化验值，可加 `--targets targets.csv`，表头与化验表相同，允许只给部分化验。年龄固定，未知项、空表或错误值均退出 3。正常运行生成 `report.md`、`result.json`、`levers.json`；后者含各输入的局部敏感度和单项、合并情景。不可把 ALT 上升造成的指数下降说成改善。

报告首先显示论文卡片，再显示个人数值、输入与分档。所有分档用未舍入值计算，切点等号采用表 5 而非摘要，详见 `references/contract.md`。不要把人群预测值解释为个人概率，不据指数决定肝活检，不把指数变化解释为纤维化改善。

每份报告保留：

> 边界: 本结果仅为成人非酒精性脂肪肝研究中的 FIB-4 指数及分档，不是个人患病概率、纤维化分期或 NASH 诊断，不能替代医生评估或据此决定是否肝活检，不能据此开始或停止用药。

来源、样本及未复现原因见 `references/claims.md` 与 `references/contract.md`。
