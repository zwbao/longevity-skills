---
name: interheart-waist-hip-tertiles
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates waist-to-hip ratio from personal circumferences, applies the
  sex-specific INTERHEART control-derived tertiles, and looks up the corresponding population
  myocardial-infarction association. Use for 腰臀比、腰围臀围、INTERHEART 腹部肥胖分组. Reports exact cutpoints as
  unassigned boundaries and supports user-supplied measurement scenarios.
---

# INTERHEART 腰臀比分组

用户说：「用我的腰围、臀围和性别，看看腰臀比在 INTERHEART 研究里属于哪一组。」

采用 Yusuf 等发表于 Lancet（2004）的男女切点和正文表 3。提供腰臀比、三分位组及该组人群关联；不生成个人发病概率。

## 输入和执行

收集同次测量的腰围、臀围及论文所需的性别分层。CSV 表头为 `marker,value,unit`，指标用 `waist_cm`、`hip_cm` 或中文名，单位接受 cm、m、mm、in。以名称而非带单位键名输入时，必须注明单位。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --sex male --out out
```

`--sex` 接受 male/female/男/女，不能默认。`--age` 可选，仅记录成人年龄上下文。用户主动提供假设腰臀围时，加 `--targets targets.csv`，同样的 CSV 格式，可只填其中一项；另一项保持实测值。不要替用户指定目标。

测量方法：不易拉伸的软尺；腰围为肋缘与髂嵴间最窄处裸腹周长，臀围为臀部最宽处薄衣外周长。妊娠、重大慢病及与原测量方法不一致的情况需保留适用性说明。这个工具不评估急性胸痛。

不向用户索取论文、附录、原始队列或公共数据库；参数已经冻结。运行离线，标准库即可。

## 输出与边界

读取 `out/report.md`、`out/result.json` 和 `out/levers.json`。缺项、单位不符、超出软件质量检查范围或文件错误，退出 3 并写 `out/problems.json`，请据此说明需要补测或修正什么。

恰好等于切点属于有效测量，但论文未明确等号归属：保留比值，组号及关联为 null，不用舍入或猜测强行归组。非边界输入按低于、介于、高于切点分组。参照组 OR 定义为 1，CI 未提供，不能填零。

验证复现的是表 3 的分组到 OR/99% CI 查值；腰臀围样例是软件测试数据，并非论文个人病例。摘要把两个 OR 的分组顺序写反，采用表格顺序，详见 references/claims.md。

报告从论文卡片开始，保留群体关联、病例对照设计和测量局限，不把情景变化写成干预获益。每份报告必须原样保留：

边界: 本报告只计算腰臀比、研究分组及对应的人群关联，不是肥胖诊断或个人心梗概率，也不能预测改变腰臀围后的获益；不能据此开始、停用或调整药物。
