---
name: hotspot-somatic-sweep
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Calculates the variant allele fraction of one quality-controlled blood SNV from
  total and alternate read counts, then checks the published clonal-haematopoiesis hotspot
  somatic-sweep screen. Use for a blood sequencing report with a gene, protein substitution and read
  counts, or questions about a hotspot VAF above 30%. Reports a record-level research classification,
  not an AML diagnosis or personal cancer probability.
---

# 血液热点变异的克隆扫荡筛查条件

用户提供自己的一条血液测序记录：基因、蛋白替换、同一位点总读段数、该替换支持读段数。适用于已由实验室质控并注释的 SNV；不把普通遗传检测、肿瘤组织、原始 FASTQ 或未注释 VCF 直接当作这种输入。

```bash
python3 scripts/personal_report.py --measurements measurements.csv --variant "SF3B1 p.K700E" --out out
```

`measurements.csv` 是 `item,value,unit` 三列表。例如补充表 6 的公开示例：

```csv
item,value,unit
Total depth,1671,1
Variant depth,134,1
```

单位 `1` 表示读段计数，必须为整数；不能把 VAF 百分比填进计数列。两个计数须来自同一位点、同一条替换和相同过滤口径。可选 `--age`（岁）和 `--sex`（女/female 或男/male）只补充人群背景，不改变结果。

读取 `out/report.md` 与 `out/result.json`。缺项、错单位、非整数、超范围或相互矛盾的输入退出 3，并写 `out/problems.json`；把具体问题交还用户，不补零、不猜单位。只缺读段计数时，应说明需要实验室提供该记录的计数，不能由四舍五入的 VAF 反推。

方法名单和阈值已随技能冻结，不要求用户寻找补充表、代码、EGA、UK Biobank 或参考基因组。公开数值复现只覆盖读段计数到 VAF；没有重跑受控 UK Biobank 队列。

每次只核对一条记录：指定热点替换、至少三条支持读段、VAF 严格大于 30% 才满足论文筛查条件。恰好 30% 不满足。名单外返回不适用；支持不足返回被过滤，不称为阴性。不同蛋白替换不能因位于同一基因或密码子而合并。高 VAF 本身不能区分胚系与体细胞来源。

不提供 `--targets`：突变读数是测序观察，不是可制定健康目标的模型输入。不得将降低 VAF 的假设改写成干预目标或处方。不得从单次观察推断克隆扩张速度、适应度、突变发生年龄或距发病年数。

每份报告先放论文卡片，保留以下原句：

> 边界: 这是单条血液变异的论文筛查条件核对，不是白血病诊断或个人发病概率；高 VAF 不能单独证明体细胞来源，未命中不能排除其他克隆或未来白血病，也不能据此开始或停止药物。

材料核查、版本差异与复现范围见 [references/contract.md](references/contract.md)、[references/claims.md](references/claims.md) 和 [references/sources.md](references/sources.md)。
