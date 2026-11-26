---
name: apoe-genotype-ad-association
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Uses a confirmed APOE genotype to look up printed Alzheimer disease association
  ORs or HRs by study population and sex, or ORs for global ancestry above the published threshold.
  Triggers on APOE 基因型、ε4、阿尔茨海默病遗传风险 and requests to interpret an APOE report. Returns population
  associations and confidence intervals; age only checks applicability.
---

# APOE 基因型分层关联查表

用户命令：**“用我的 APOE 基因型报告，查询对应研究分组的阿尔茨海默病关联值和置信区间。”**

数据来自 Belloy 等，JAMA Neurology，2023 的正文表和补充表，已冻在
`data/associations.json`。无需联网，不向用户要论文、补表、研究队列或代码。
用户需提供已确认的 APOE 双等位基因型、当前年龄，以及要查询的研究分组。
这是基因型报告数据，不是常规血液 APOE 蛋白浓度；不根据单个 SNP、家族史或“ε4 阳性”补全基因型。

默认查询病例对照 OR，例如用户明确提供 ε3/ε4、65 岁、女性、非西班牙裔白人分组：

```bash
python3 scripts/personal_report.py --genotype '3/4' --age 65 --sex female --group nhw --out out
```

参数按用户资料选择：

| 参数 | 接受值与范围 |
| --- | --- |
| `--genotype` | 22、23、24、33、34、44；也接受 ε3/ε4、E3/E4、APOE*34 及反向排列 |
| `--age` | 当前年龄，岁；严格大于 55；120 为输入质量上限，不是论文最大年龄 |
| `--sex` | male、female；明确要看男女合并时选 pooled；不默认推断 |
| `--group` | nhw 非西班牙裔白人；nhb 非西班牙裔黑人；hispanic 西班牙裔（含各种族）；east_asian 日、韩汇总研究 |
| `--analysis` | case-control（默认 OR）；survival（HR）；ancestry（祖源分组 OR） |

`survival` 使用 eTable 13，保守限未满 90 岁，并仅支持 nhw、nhb、hispanic。
`east_asian` 只能选 case-control 与 pooled，ε2/ε2、ε2/ε3 返回明确标注的合并组值。
不从中文、国籍、姓名或出生地推断研究分组；东亚值不能说成中国人群的专属估计。

若用户已有**全基因组祖源报告**，可选 ancestry 模式：不填 `--group`，
填 `--ancestry european`、`african` 或 `amerindian`，并明确选择 `--sex pooled`。
使用 `--measurements ancestry.csv` 提供所选祖源比例：

```csv
marker,value,unit
ancestry_percent,80,%
```

该模式严格要求比例 >75%，使用 eTable 16；不是 APOE 局部祖源，不能用自报种族代替。
只接受百分数单位 `%`，不猜测无单位小数的含义。原表美洲原住民祖源组 ε2/ε2、ε2/ε4
印为无限置信区间，工具拒绝输出零风险。其他未印出的组合也拒绝外推。

**年龄窗口曲线没有完整数值表。** 所有输出明确标注“年龄未分层”，年龄仅作范围检查；
不生成联合年龄、性别、祖源的个体风险，不从图上读近似点，不相乘不同分析的 OR/HR。
本方法无可调节输入，不提供 `--targets` 或健康目标敏感度。

输出 `out/report.md` 和 `out/result.json`。缺项、错单位、超范围或不可查询的组合时退出 3，
写 `out/problems.json`，结果全部置空。错误报告也保留论文卡片和边界句。
报告用中文，先放论文卡片，再说明输入和原表分层、参照 ε3/ε3、OR/HR 与置信区间。
OR 不是风险比；HR 不是从当前年龄开始的患病概率；参照值 1 不表示不会患病。

每份报告必须原样保留：

> 边界: 这是研究人群相对 APOE ε3/ε3 的关联查表，不是个人患病绝对概率、诊断或治疗建议；不能据此开始、停用或调整药物。

方法合同见 [references/contract.md](references/contract.md)，材料核查与出处见
[references/sources.md](references/sources.md)，研究设计与原文不一致处见
[references/claims.md](references/claims.md)。
