---
name: longevity
description: >-
  Published longevity and ageing methods, an evidence store and within-person variation data behind one command
  (`longevity`) or MCP server. Use whenever a question gives a person's blood tests or body measurements, in any
  language (English report or NHANES-style names such as "Albumin (g/dL)", "Lymphocyte percent (%)", "White blood cell
  count (1000 cells/uL)" are accepted): phenotypic or biological age, 5/10/15/20-year mortality risk and model survival
  (PhenoAge Gompertz model; needs age), which of two people has higher mortality risk, eGFR and kidney stage, China-PAR
  10-year cardiovascular risk, body fat from tape measurements, methylation or proteomic clocks; also what papers say
  about a drug, supplement, diet or gene (NMN, rapamycin, fasting), and whether a lab change is real or within normal
  variation. 生物年龄、表型年龄、死亡风险、肾小球滤过率、心血管风险、体脂率、甲基化年龄、补剂或药物证据、指标变化是不是真的。
---

# longevity

不要自己按记忆套公式，也不要逐个读库里的技能目录：用下面的工具或命令，结果里有论文、验证状态和来源。

## 怎么调用

有 MCP 工具（`find_methods`、`read_method`、`run_method`、`query_evidence`、`review_change`、`review_trend`、`plan_experiment`）就直接用。没有就用命令行，按顺序试：

1. `longevity …`（已安装）。没有的话可以先装：`uv tool install git+https://github.com/zwbao/longevity-skills`
2. `uvx --from git+https://github.com/zwbao/longevity-skills longevity …`（不安装；第一次要下载）
3. 在仓库检出里：`python3 longevity …`

输出都是 JSON。`longevity --help` 列出全部命令。

## 步骤

1. **找方法**：`longevity find <用户原话>`；或者 `longevity methods --have 肌酐,白蛋白,年龄,性别`，看 `complete` 是否为 true、还缺什么、还要问用户什么（`also_ask`）。
2. **看输入**：`longevity describe <方法>`，了解单位、可换算单位、范围和要问用户的项目；`run_example` 是一行可以照着填的命令。
3. **运行**：例如 `longevity run ckd-epi-2021-egfr --age 62 --sex female -m '肌酐=78 umol/L'`。数值和单位照化验单原样写，中英文名称都可以（英文化验单、NHANES 式名称会自动对应）；是否项、文件路径等用 `--answer 键=值`，例如 `--answer smoker=no`。
4. **查证据**：`longevity evidence NMN`。
5. **看变化**：`longevity change --marker 收缩压 --before 138 --after 131`；有多次带日期的结果用 `longevity trend`。

## 规则

- 回答时写明结果的标签（例如「已发表模型（已复现论文）」）、论文和 DOI。
- `status` 不是 `ok` 时照实转告原因（`input_problem`、`not_computed`、`refused`、`missing_dependency`、`error`），不要换别的方法或自己估算来代替。
- 结果为 `refused` 时，只有用户明白风险后才能加 `--allow-draft` 或 `--allow-mixed-dates`。
- 动物和细胞实验的结论不是人的效果；证据库里没有某个名字，不说明它安全或无效。
- 不给剂量，不替用户决定开始、停止或更换药物；出现急症（胸痛、呼吸困难、意识改变等）先让用户拨打急救电话（中国大陆 120）或立即就医。
