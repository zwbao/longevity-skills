---
name: unruptured-intracranial-aneurysm-prevalence
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Places one person in the groups that Dremel et al. (Lancet Neurology 2026) pool
  for unruptured intracranial aneurysm prevalence: age band (study mean age under or over 55), sex,
  ADPKD, connective-tissue disorder, family history of aneurysm or aneurysmal subarachnoid
  haemorrhage, atherosclerotic disease, current smoking, hypertension and country. It quotes each
  group's printed prevalence and prevalence or risk ratio. It never multiplies ratios into a personal
  probability and never says whether to screen. Use for 脑动脉瘤, 颅内动脉瘤, 未破裂动脉瘤有多常见, 多囊肾 or 家族史.
---

# 未破裂颅内动脉瘤：你所在人群的患病率

用户只提供年龄、性别和几项是或否的回答。不要向用户要论文 PDF、附录或影像报告。

## 命令

Set `SKILL` to the directory that contains this file.

```bash
python3 "$SKILL/scripts/personal_report.py" --age 58 --sex female \
  --adpkd no --connective-tissue no --family-history 1 --atherosclerosis no \
  --smoking never --hypertension yes --country 中国 --out out/
```

- `--adpkd`、`--connective-tissue`（马方、埃勒斯-当洛斯、Loeys-Dietz）、`--atherosclerosis`（颈动脉狭窄、缺血性卒中、冠心病等）、`--hypertension`：yes 或 no。
- `--family-history`：一级亲属里得过颅内动脉瘤或动脉瘤破裂出血的人数，写 no、1 或 2+；只知道有、不知道几位时写 yes。
- `--smoking`：current、former 或 never。
- `--country` 可选；附录只单列了中国、日本、韩国、美国、芬兰、德国、荷兰、英国。

缺一项、写了读不懂的词、或年龄不在 18–110 岁，脚本退出码 3，写 `out/problems.json`，报告里不出现任何患病率。正常时写 `out/report.md` 和 `out/result.json`。

## 报告必须保留

- 论文卡片放在开头。
- 每个人群的数单独列出，不相乘；同时属于几组时只指出点估计最高的一组。
- 年龄两档是按研究人群平均年龄分的，不是按个人年龄。
- 已经查到动脉瘤的人不适用；患病率不是破裂风险。
- 边界句原样出现：这些是论文汇总的人群患病率，不是本人有没有动脉瘤的判断；不决定要不要筛查、做哪种检查，也不决定开始或停止任何药物。

方法和出处见 [references/claims.md](references/claims.md)，查表合同见 [references/contract.md](references/contract.md)。
