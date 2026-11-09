---
name: philadelphia-expanded-ace
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Counts adverse childhood experiences with the 21-item Philadelphia expanded ACE
  survey, scored into 14 domains (abuse, neglect, household dysfunction, witnessed violence,
  discrimination, neighborhood, bullying, foster care) with the item thresholds in eTable 1 of Temple
  et al., JAMA Network Open 2026, places the count in the paper's 0, 1-3, 4-5 or 6+ category, and
  quotes that category's cohort rates (Table 2) and adjusted odds ratios versus 0 ACEs (Table 3) for
  depression, PTSD, suicidality, dating violence, substance use and schooling. It gives no personal
  probability, since the paper prints no intercepts. Use when someone asks about childhood adversity,
  ACE scores, 童年逆境, 童年创伤 or this study.
---

# 童年逆境计数（费城扩展 ACE）

用户交 21 道题的答案（18 岁以前的经历）。不要向用户要论文、补充表或 PDF：计分阈值和表 2、表 3 已冻在 `scripts/presets.py`。

## 命令

```bash
python "$SKILL/scripts/personal_report.py" --measurements answers.csv --age 19 --out out
```

`answers.csv` 带表头 `item,value,unit`，或每行 `名称,答案`。名称用 `skill.json` 里的键（如 `ea_insult`、`nb_safe`）或中文题名；答案写选项编号或选项文字（「不止一次」「有时符合」「是」……），每题的选项和阈值写在 `skill.json` 各输入的 `note_zh`。`--age` 可选，只用于提示论文队列约 19 岁。

- 缺题不当作「没有」。缺的题不改变分档时照常出报告；可能跨档时退出码 3，`out/problems.json` 列出要补答的题。
- 编号超出选项、带小数、不是数或写了别的单位时退出码 3，不计算。
- `out/result.json` 给出 `ace_count`（0–14）和 `ace_category`（`0`、`1-3`、`4-5`、`6+`）。

问这些题时语气要平和，告诉对方可以跳过任何一题；跳过的题会让报告说明条数的范围。

## 报告必须保留

- 开头的论文卡片。
- 表中数字是队列里该分档人群的比例和比值比，不是这个人的概率。
- 两题一类时按任一题达到阈值计；若两题都要满足会换档，报告照写。
- 末行 `边界:` 原样引用，含求助提示。不给任何用药建议。
