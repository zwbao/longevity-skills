---
name: red-meat-burden-of-proof
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Queries printed Burden of Proof estimates for unprocessed red meat intake and six
  chronic disease outcomes. Use when a person provides habitual daily unprocessed red meat intake and
  asks what the published population associations mean. Supports only the nine printed intake points
  from 0 to 200 g/day in 25 g/day steps, with conservative uncertainty intervals and optional
  comparisons of user-selected intake points.
---

# 未加工红肉摄入与慢病相对风险查表

用户提供习惯性日均未加工红肉摄入量、年龄和性别。技能使用已冻结的补充表7，返回对应摄入点的相对风险和保守95%不确定区间。只查询2022年论文，不表示最新膳食共识。

```bash
python3 scripts/personal_report.py --measurements intake.csv --age 50 --sex female --out out
```

`intake.csv` 表头为 `marker,value,unit`；例如一行为 `unprocessed_red_meat_g_d,50,g/d`。这是论文的测试摄入点，不是饮食建议。

- 只接受0、25、50、75、100、125、150、175、200 g/d。其他摄入量报“不支持”，不插值、不取整、不外推，也不要让用户修改真实摄入量来迁就工具。
- 未加工红肉包括牛、羊、猪肉；不能输入总肉量或包括香肠、培根的加工肉量。不把单顿量当日均量，不自动换算份量或生熟重量。单位必须为g/d，键名已含单位时可省略单位单元格。
- 年龄至少25岁；年龄只检查适用人群，不调整RR。`--sex`接受female、male、unknown；只有female显示乳腺癌表值。其他结局不分性别。
- 用户明确提供另一个摄入点时，可加`--targets targets.csv`，表头与摄入文件相同。`levers.json`包含当前值、相邻表点、单个目标和全部目标（本方法仅一个可改输入）的表值及差。没有连续敏感度或目标差值的置信区间，不推断因果效应。

成功写出`report.md`、`result.json`和`levers.json`。缺项、错误单位、超范围、非表点或格式错误时退出3并写`problems.json`，不返回计算结果。不要向用户要论文、补充表、公共队列或作者代码。

报告必须以论文卡片开头，注明：保守区间含研究间异质性；星级属于人群证据，不是个人危险分级；缺血性卒中的表值不能统一解读为相对零摄入（补充表7中零摄入值并非1）。不把0克视作已证实的最佳饮食目标，不给用药或饮食处方。

每份报告必须保留：

> 边界：这是观察性人群研究的表值查询，不是个人患病概率，也不能证明改变摄入量会改变你的风险；不提供饮食处方或药物剂量，不能据此开始或停用药物。

来源、表格列名、参照点异常和范围约定见`references/contract.md`及`references/claims.md`。论文数值集中在`scripts/presets.py`；不要另写一套模型系数。
