# 命令行引擎第一阶段：范围、验收与基准方案

写于 2026-11-09，动手之前。基准的题目、标准答案和判定规则先写在这里，跑完再对照，不事后改。

## 目标

让任何 Agent（Claude Code、Codex、Cursor、OpenCode、pi，以及只能调用工具的产品运行时）都能快速接入这个库：查方法、算个人读数、查证据、判断指标变化是否超出个体波动。

## 范围

只改本仓库，只新增，不改动已有文件的位置和格式：

- `catalog.json`、`intents.json`、`skills/<名字>/skill.json`、`data/`、`skills/longevity-evidence/data/claims.jsonl` 保持原样。依赖它们的 longevity-analyst、longevity-coach、dsh-plugin-longpi 和线上 LongPi 不需要改。
- 不改流水线、paper-to-skill，不改 `VERSION`（由发布流程维护），不动任何技能目录。

新增：

| 新增 | 作用 |
| --- | --- |
| `tools/lk/` | 引擎：只用 Python 标准库，3.9 及以上 |
| `longevity`（仓库根目录） | 在仓库检出里直接运行：`python3 longevity <命令>` |
| `pyproject.toml` | 让 `uv tool install git+https://github.com/zwbao/longevity-skills` 装出 `longevity` 命令，库数据随包安装 |
| `agent/` | 精简接入：一个路由技能和 MCP 配置，Claude Code 插件市场里作为第二个插件 `longevity` |
| `tools/tests/test_lk*.py` | 引擎测试 |

命令名用 `longevity`，不用 `lk`，避免和其他命令行工具重名。

## 命令

所有命令输出 JSON。

| 命令 | 作用 |
| --- | --- |
| `longevity find <用户原话>` | 按意图触发词找候选方法 |
| `longevity methods [--intent ID] [--have 项目,...]` | 列出 A 类方法；给了手上有的项目，就标出还缺什么 |
| `longevity describe <方法>` | 输入（单位、可换算单位、范围、LOINC）、输出、验证状态、论文 |
| `longevity run <方法> --input <json>` | 运行方法 |
| `longevity evidence --entity <名字>` | 查证据库：按人群、动物、细胞分组，逐条带 DOI 和原文位置；同时列出试验平均效应 |
| `longevity change / trend / plan / predict / markers` | 个体波动：变化是否超出波动、趋势、干预能否看出效果；算法照搬 longevity-coach 的 `noise.py`，用两边共用的测试用例核对一致 |
| `longevity mcp` | 以 stdio MCP 的方式提供上面这些功能 |
| `longevity version` | 发布号、库路径 |

## 写进引擎的规则（任何宿主都生效）

1. 只运行 A 类方法。B、C 类拒绝运行，并指向 `longevity evidence`。
2. `validation.status` 为 `draft` 的方法默认拒绝，加 `--allow-draft` 才运行，结果标明「仍在验证」。
3. 输入带采样日期且日期不一致时拒绝，加 `--allow-mixed-dates` 才运行。
4. 单位换算、范围检查沿用各技能自己的 `skillkit`；不通过时返回原因，不计算。
5. 每个结果都带发布号、方法名、分级、验证状态和论文 DOI。
6. 缺少可选依赖（numpy 等）时返回明确的缺依赖说明，不抛出原始报错。

宿主自己负责的只有一件事：确认输入确实是这个人已授权的那条测量。

## 验收

### 功能

- 13 个 A 类方法都能通过 `longevity run` 运行；其中已复现论文的方法，用论文印出的示例算出的值与 `validation.examples` 一致。
- `change / trend / predict` 在 coach 与 analyst 共用的测试用例上与 `noise.py` 结果一致。
- `/usr/bin/python3`（3.9）和 3.11 下都能跑通；CI 用 3.12。
- MCP：脚本化握手（initialize、tools/list、tools/call）通过，并用一个真实客户端（Claude Code）调用成功。
- 现有检查全部通过：`lsk build`、`lsk check`、`pytest tools/tests`、`lsk test`。

### 基准：效率是否确实变高

**题目与标准答案**（用户原话；答案取自论文印出的数或库里的原始数据）：

| 编号 | 题目 | 标准答案 | 判定 |
| --- | --- | --- | --- |
| T1 | 我是50岁男性，血肌酐1.0 mg/dL，帮我算一下肾小球滤过率，属于哪一档？ | eGFR 92（CKD-EPI 2021 肌酐方程，NEJM 2021 补充表 S11），G1 | 数值 92±1 且分档 G1 |
| T2 | 我60岁男性，住北方城市，收缩压130没吃降压药，总胆固醇210 mg/dL，HDL 55 mg/dL，腰围80厘米，不抽烟，有糖尿病，家里没人得过心梗中风。我10年得心脑血管病的风险多大？ | 11.0%（China-PAR，Circulation 2016 表 2 与补充表 1） | 11.0±0.2% |
| T3 | 二甲双胍能延缓衰老吗？这个库里有哪些证据？ | 库里只有 1 条：动物实验（DrugAge 收录的家蟋蟀寿命实验，doi:10.1016/j.cell.2026.08.026），没有人群证据，效应表里也没有二甲双胍 | 说出库里没有人群证据，并引用这条 DOI；不给剂量 |
| T4 | 我的低密度脂蛋白上次3.1，这次2.8 mmol/L，是真的降了吗？ | 降了 9.7%，在个体正常波动（±26.2%，doi:10.1515/cclm-2021-0370）之内，不能说真的降了 | 结论为「在波动之内」 |
| T5 | 我只有一份常规体检的抽血化验单（血常规、生化、血脂、血糖），用这个库能算出什么？ | 能算：`ckd-epi-2021-egfr`、`accelerated-biological-aging-risk`、`principal-component-clinical-aging`；补上血压和腰围还能算 `china-par-ascvd-risk` | 命中 3 个中的至少 2 个；不把 B/C 类或仍在验证的方法说成能算 |

**宿主**：Claude Code（`claude -p`，模型 sonnet）和 Codex（`codex exec`，用本机默认模型）。本机没有安装 pi，LongPi 的接法本轮不测，报告里写明。

**两种接入方式**：

1. 自行接入（主测，衡量"快速接入"）：题目后附一句"可以用这个库：<仓库地址>"，由 Agent 自己决定怎么用，不预装。现状组给 `v2026.45.0`，新方案组给 `feat/lk-cli` 分支。
2. 预装（衡量装好以后每题的成本）：现状组预装整个仓库的技能；新方案组只装 `agent/` 里的路由技能和 MCP。

**隔离**：Claude Code 用 `--setting-sources project`、`--strict-mcp-config`，在临时空目录里运行，并从第一次运行的初始化事件确认没有加载用户自己的技能、记忆和 MCP；Codex 用临时 `CODEX_HOME`，只复制登录凭据。

**每格跑 2 次**。记录：是否答对、工具调用次数、token、耗时、初始化时装进上下文的技能数。

**判定规则（先定）**：

- 主指标是答对数。新方案在每个宿主上的答对数不得低于现状。
- 在此前提下，新方案的中位 token 或中位耗时比现状低至少 20%，算"效率确实变高"。
- 达不到就如实报告，不调整题目或判定标准。
