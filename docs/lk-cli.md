# `longevity` 命令行与 MCP 服务

把这个库接到任何 Agent 上：Claude Code、Codex、Cursor、OpenCode、pi，或者只能调用工具的产品运行时。一个命令行，一个 MCP 服务，背后是同一个引擎；所有命令输出 JSON。

## 安装

三种方式任选一种：

```bash
# 1. 装成命令（推荐；库数据随包安装，之后离线可用）
uv tool install git+https://github.com/zwbao/longevity-skills
longevity version

# 2. 不安装，直接运行（第一次会下载）
uvx --from git+https://github.com/zwbao/longevity-skills longevity version

# 3. 已经有仓库检出
python3 longevity version
```

要固定版本，在地址后面加发布标签，例如 `git+https://github.com/zwbao/longevity-skills@v2026.45.0`。只用 Python 标准库，需要 Python 3.9 及以上；少数方法要 numpy 等包，装 `longevity-skills[scientific]`，或者按 `longevity run` 返回的缺依赖说明安装。

## 命令

| 命令 | 作用 |
| --- | --- |
| `longevity find 我的生物年龄是多少` | 把用户的话对到意图和方法 |
| `longevity methods [--intent ID] [--have 肌酐,白蛋白,年龄,性别] [--all]` | 列出 A 类方法；给了手上有的项目，就标出能不能算、还缺什么。`--all` 加上 B 类查表和工具 |
| `longevity describe ckd-epi-2021-egfr` | 输入（单位、可换算单位、范围）、输出、验证状态、论文和一行运行示例 |
| `longevity run ckd-epi-2021-egfr --age 62 --sex female -m '肌酐=78 umol/L'` | 运行方法。是否项用 `--answer smoker=no`；也可以 `--input person.json` 或 `--input -` |
| `longevity evidence NMN 雷帕霉素` | 已收录论文对这些对象的说法，按人群、动物、细胞分组，逐条带 DOI 和原文位置；同时列出试验平均效应 |
| `longevity change --marker 收缩压 --before 138 --after 131` | 两次结果的变化是否超出个体正常波动 |
| `longevity trend --marker 空腹血糖 --series 2024-09-03:5.0 2025-09-02:5.3 2026-09-01:5.6` | 多次带日期的结果有没有趋势 |
| `longevity plan` / `predict` / `markers` | 一个人能不能测出某个干预的效果；有波动数据的指标 |
| `longevity mcp` | 以 stdio MCP 的方式提供上面的功能 |
| `longevity version` | 发布号、库的位置 |

`--input` 的 JSON：

```json
{"age": 60, "sex": "male",
 "measurements": [{"item": "收缩压", "value": 130, "unit": "mmHg", "date": "2026-10-01"},
                  {"item": "总胆固醇", "value": 210, "unit": "mg/dL", "date": "2026-10-01"}],
 "arguments": {"smoker": "no", "diabetes": "yes"},
 "medications": ["阿托伐他汀"]}
```

退出码：0 成功，2 用法错误，3 输入没通过检查，4 拒绝运行，5 缺依赖，1 其他错误。

## 引擎替所有宿主执行的规则

- 只运行 A 类方法、B 类查表和工具；C 类只收录，拒绝运行。
- 仍在验证（`draft`）的 A 类方法默认拒绝，加 `--allow-draft` 才运行，结果标明仍在验证。
- 测量带采样日期且日期不一致时拒绝，加 `--allow-mixed-dates` 才运行。
- 单位换算和范围检查用各方法自己的 `skillkit`；不通过就返回原因，不计算。
- 每个结果都带发布号、方法的分级和标签、验证状态和论文。

宿主自己要做的只有一件事：确认交给引擎的数值确实是这个人、这一次的测量。

## MCP

```json
{"mcpServers": {"longevity": {"command": "longevity", "args": ["mcp"]}}}
```

没装成命令时用 `{"command": "uvx", "args": ["--from", "git+https://github.com/zwbao/longevity-skills", "longevity", "mcp"]}`；在仓库检出里用 `{"command": "python3", "args": ["<仓库路径>/longevity", "mcp"]}`。

工具名和 LongPi 的原生工具一致：`find_methods`、`read_method`、`run_method`、`query_evidence`、`review_change`、`review_trend`，另有 `plan_experiment`。

## 精简接入技能

`agent/skills/longevity/SKILL.md` 是一个路由技能，告诉 Agent 先用 `longevity` 命令或 MCP 工具，而不是逐个读 178 个技能目录。

- Claude Code：`/plugin marketplace add zwbao/longevity-skills`，再安装插件 `longevity`（只含这一个技能和 MCP 配置）。原来的 `longevity-skills` 插件（全部技能）不变。
- 其他 Agent：`npx skills add zwbao/longevity-skills --skill longevity`，或者把 `agent/skills/longevity/` 复制到 Agent 的技能目录。
