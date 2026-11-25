---
name: alcohol-burden-of-proof
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Uses a person's average daily pure-alcohol intake to look up published relative
  risks and uncertainty intervals for twenty health outcomes in the alcohol Burden of Proof method.
  Triggers on 饮酒量、酒精摄入、喝酒与癌症风险、 alcohol intake and requests to compare user-specified intake
  scenarios. Shows adjacent printed exposure nodes for off-grid inputs without interpolation.
---

# 酒精 Burden of Proof 查表

用户命令：**“用我的每日平均纯酒精摄入量，查一下论文中各疾病的相对风险，并保留不确定性。”**

先确认输入是本人通常的每日平均**纯乙醇克数**，不是饮料毫升数、单次饮酒量或未定义的“杯”。
只需要个人摄入量，不向用户索取论文、补充 PDF、队列数据或作者代码。
数据已经从 Dai 等，Nature Health，2026，表 3 冻结在本技能中，运行无需联网。

把个人数据写入 CSV：

```csv
marker,value,unit
alcohol_g_day,10,g/d
```

这里的 10 是用于演示的论文节点，不是推荐摄入量。只接受 `g/d`；
用户仅提供杯数、每周克数或饮料体积时，先澄清并取得可靠的每日纯酒精克数，不能默认为同一单位。

```bash
python3 scripts/personal_report.py --measurements alcohol.csv --out out
```

用户主动给出另一个摄入量情景时，可加 `--targets targets.csv`，文件列与测量文件相同。
不替用户选目标，不优化饮酒量。年龄和性别不进入这张合并风险表，脚本不要求也不接受相应校正参数。

输出为 `out/report.md`、`out/result.json`、`out/levers.json`。
缺项、错单位、无法读取、非有限数或超出查表范围时退出 3，写 `out/problems.json`，所有结果置空。
不能补零、截断或外推。允许范围 0–100 g/d 是表格覆盖限制，不是正常饮酒范围。

报告开头保留论文卡片。节点 10、20、…、100 g/d 直接返回表 3 的平均 RR 和
计入研究间异质性的 95% UI；零摄入为参照 RR=1，未印出的区间保持空值。
非节点输入只展示两侧摄入量节点，不能称为个人风险范围。
20 种疾病分别展示，乳腺癌注明女性研究，前列腺癌注明男性研究，不合成为总风险。
低于 1 的 RR 不是个人获益证明；同样的日均饮酒量不能区分暴饮、既往饮酒和饮酒年限。

`levers.json` 提供相邻印出节点的离散对照，连续敏感度 `derivative` 为 null。
只有当前与目标都为印出节点或零参照时才提供各结局平均 RR 差，其他情况下差值为 null。
两种情景的区间照原表保留，不拼造差值区间，不解释成干预效果。

每份报告必须原样保留：

> 边界: 本报告按你提供的饮酒量查阅人群观察性研究的关联，不是个人患病概率、因果效应或安全饮酒阈值；不能据此开始饮酒、增加饮酒或开始、停用任何药物，不提供饮酒量或药物剂量建议。

方法范围见 [references/contract.md](references/contract.md)，材料核查见
[references/sources.md](references/sources.md)，研究声明见 [references/claims.md](references/claims.md)。
