# `longevity` 命令行与 MCP 服务

把这个库接到任何 Agent 上：Claude Code、Codex、Cursor、OpenCode、pi，或者只能调用工具的产品运行时。一个命令行，一个 MCP 服务，背后是同一个引擎；所有命令输出 JSON。

## 安装

三种方式任选一种：

```bash
# 1. 装成命令（推荐；库数据随包安装，之后离线可用，每次调用约 0.1 秒）
uv tool install git+https://github.com/zwbao/longevity-skills
longevity version
uv tool upgrade longevity-skills          # 以后更新

# 2. 不安装，直接运行（第一次要下载整个仓库；之后每次调用还会联网检查一次，约多 2 秒）
uvx --from git+https://github.com/zwbao/longevity-skills longevity version

# 3. 已经有仓库检出
python3 longevity version
```

- 需要 Python 3.9 及以上，只用标准库。
- 少数方法要 numpy、pandas 等包：`uv tool install 'longevity-skills[scientific] @ git+https://github.com/zwbao/longevity-skills'`。这个包没有发布到 PyPI，不要直接写 `longevity-skills[scientific]`，那会去 PyPI 找同名的包。
- 固定版本：在地址后面加发布标签，例如 `@v2026.46.0`。命令行从 2026.46.0 起才随发布带上，更早的标签里没有。

## 命令

| 命令 | 作用 |
| --- | --- |
| `longevity find 我的生物年龄是多少` | 把用户的话对到意图和方法 |
| `longevity methods [--intent ID] [--have 肌酐,白蛋白,年龄,性别] [--all]` | 列出 A 类方法。给了手上有的项目，就标出能不能算（`complete`）、还缺什么、还要问用户什么。`--all` 加上 B 类查表和工具 |
| `longevity describe ckd-epi-2021-egfr` | 输入（单位、可换算单位、范围，是否项、文件和文本参数）、输出、验证状态、论文和一行运行示例 |
| `longevity run ckd-epi-2021-egfr --age 62 --sex female -m '肌酐=78 umol/L'` | 运行方法。是否项、文件路径等参数一律用 `--answer 键=值`（例如 `--answer smoker=no`）；也可以 `--input person.json` 或 `--input -` |
| `longevity evidence NMN 雷帕霉素` | 已收录论文对这些对象的说法，按人群、动物、细胞分组，逐条带 DOI 和原文位置；同时列出试验平均效应 |
| `longevity change --marker 收缩压 --before 138 --after 131` | 两次结果的变化是否超出个体正常波动 |
| `longevity trend --marker 空腹血糖 --series 2024-09-03:5.0 2025-09-02:5.3 2026-09-01:5.6` | 多次带日期的结果有没有趋势 |
| `longevity plan` / `predict` / `markers` | 一个人能不能测出某个干预的效果；哪些指标有波动数据 |
| `longevity mcp` | 以 stdio MCP 的方式提供上面的功能（`markers` 除外） |
| `longevity version` | 发布号、库的位置 |

`--input` 的 JSON（以 China-PAR 为例，`describe` 会列出一个方法要的全部是否项）：

```json
{"age": 60, "sex": "male",
 "measurements": [{"item": "收缩压", "value": 130, "unit": "mmHg", "date": "2026-10-01"},
                  {"item": "总胆固醇", "value": 210, "unit": "mg/dL", "date": "2026-10-01"},
                  {"item": "高密度脂蛋白胆固醇", "value": 55, "unit": "mg/dL", "date": "2026-10-01"},
                  {"item": "腰围", "value": 80, "unit": "cm", "date": "2026-10-01"}],
 "arguments": {"treated": "no", "smoker": "no", "diabetes": "yes", "north": "yes", "urban": "yes", "family_history": "no"}}
```

退出码：0 成功；2 用法错误；3 输入没通过检查，或者运行了但一个读数也没算出（`not_computed`）；4 拒绝运行；5 缺依赖；1 其他错误。除了 `--help`，所有输出都是 JSON。

## 引擎替所有宿主执行的规则

- 运行 A 类方法、B 类查表和工具，结果标签分别是「已发表模型」「论文查表（不是对这个人运行论文模型）」「工具」。C 类只收录，拒绝运行。
- 仍在验证（`draft`）的 A 类方法默认拒绝，加 `--allow-draft` 才运行，结果标明仍在验证。
- 测量的采样日期不一致，或者只有一部分写了日期，默认拒绝（`--measurements-file` 里的日期列也算），加 `--allow-mixed-dates` 才运行。
- 声明了输入的方法，由引擎先用库里的 skillkit 对上每一行、按声明的系数换算单位、检查合理范围，再交给脚本；不通过就返回原因，不计算。
- 每个结果都带发布号、方法的分级和标签、验证状态和论文。

宿主自己要做的只有一件事：确认交给引擎的数值确实是这个人、这一次的测量。

## MCP

先装好 `longevity` 命令（见上），再把它配进宿主：

```json
{"mcpServers": {"longevity": {"command": "longevity", "args": ["mcp"]}}}
```

- 在仓库检出里可以不安装：`{"command": "python3", "args": ["<仓库路径>/longevity", "mcp"]}`。
- 也可以用 `uvx`（`{"command": "uvx", "args": ["--from", "git+https://github.com/zwbao/longevity-skills", "longevity", "mcp"]}`），但第一次启动要下载整个仓库，可能超过宿主的启动等待时间。

工具名和 LongPi 的原生工具一致：`find_methods`、`read_method`、`run_method`、`query_evidence`、`review_change`、`review_trend`，另有 `plan_experiment`（`plan` 和 `predict`）。服务是单线程的，一次运行最长 180 秒。

## 精简接入技能

`agent/skills/longevity/SKILL.md` 是一个路由技能，告诉 Agent 用 `longevity` 命令或 MCP 工具，而不是逐个读库里的全部技能目录。

- Claude Code：先装好 `longevity` 命令，再 `/plugin marketplace add zwbao/longevity-skills`，安装插件 `longevity`（`/plugin install longevity@longevity-skills`）。这个插件只含路由技能和 MCP 配置；原来的 `longevity-skills` 插件（全部技能）不变。
- 其他 Agent：`npx skills add zwbao/longevity-skills --skill longevity`，或者把 `agent/skills/longevity/` 复制到 Agent 的技能目录。
