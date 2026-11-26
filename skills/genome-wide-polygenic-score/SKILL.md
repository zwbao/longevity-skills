---
name: genome-wide-polygenic-score
description: >-
  Tier A draft: the paper's printed example is not reproduced yet, so treat the readout as
  provisional. 按 Khera 等的公开逐变异权重，从个人基因型剂量计算冠状动脉疾病、心房颤动、2
  型糖尿病、炎症性肠病或乳腺癌的原始多基因分数。在用户提供基因型剂量并要求计算这些疾病的多基因评分时使用。检查坐标、等位基因与完整性，不把原始分数转换为个人患病概率。
---

# 全基因组多基因评分

用 Python 3 标准库运行：

```bash
python3 scripts/personal_report.py --genotypes /path/to/my-dosages.csv.gz --disease bc --build hg19 --sex female --age 55 --out out
```

疾病参数：`cad` 冠状动脉疾病、`af` 心房颤动、`t2d` 2 型糖尿病、`ibd` 炎症性肠病、`bc` 乳腺癌。一次选一种，不自行扩大用户要求的遗传分析范围。`bc` 仅接收 `--sex female`；其他疾病的性别、年龄可省略，只用于背景和适用范围说明。

## 用户提供自己的数据

CSV/TSV，可 gzip，单个人、每个位点一行，列名为 `variant,dosage_allele,dosage_copies,unit`。

- `variant`：`染色体:hg19位置:等位基因1:等位基因2`，只接收常染色体和正链 DNA 字母。支持 `chr` 前缀，等位基因顺序可交换。必须声明 `--build hg19` 或 `--build GRCh37`。
- `dosage_allele`：本行计数的等位基因，必须属于该位点的等位基因对。若它是权重文件中的另一等位基因，程序使用 `2 - dosage` 转到效应等位基因。
- `dosage_copies`：0–2 拷贝，直接分型可以为 0、1、2，填补剂量可以有小数。列名也接受 `DS`、`dosage`、`等位基因剂量`、`效应等位基因剂量`。
- `unit`：每行都写 `1`，表示拷贝计数；不接受百分比、浓度、风险分数。

需要所选模型的全部位点。消费级芯片原始导出通常不足；不能把未出现的变异解释为纯合参考、不能用零或均值补缺项。输入应来自已做质量控制的基因型或填补结果，论文验证集对填补质量使用 INFO > 0.3。本技能不做填补、不检查原始测序质量、不做基因组版本或链方向转换，也不读 PDF、VCF、BGEN 或多样本矩阵。不要推测这些格式中的剂量方向；需要明确的单样本剂量表。

## 技能自己取得公开数据

自动从 Broad 下载所选疾病的 v3 权重并核对 SHA-256。地址、完整行数、压缩包及解压文本校验和在 `references/weights.json`。完整文件不随仓库分发，默认缓存到 `$XDG_CACHE_HOME/longevity-skills/genome-wide-polygenic-score`；未设环境变量时为 `~/.cache/longevity-skills/genome-wide-polygenic-score`。可用 `--cache /path/to/cache` 指定缓存；`--offline` 只使用已校验缓存。

不要向用户要补充表、论文 PDF、Broad 权重、UK Biobank 队列或 Hail 项目。下载失败属于公开资源问题，退出 2；缺少或错误的个人输入退出 3，读取 `out/problems.json` 告诉用户缺什么。基因型只在本地读取，临时磁盘索引结束后删除。四个大型模型需要百万级位点和足够的临时磁盘空间；乳腺癌模型较小。

## 输出与解释

`out/report.md` 先放论文卡片，再写所选疾病的完整原始加权分数、纳入位点数与额外位点数。`out/result.json` 是相同结果；`out/provenance.json` 记录公开权重版本。失败时所有结果为 null，不留下旧分数。

这是 `sum(dosage × effect_weight)`，不除以位点数，不对权重取指数。没有个人输入与总分配对的论文示例，因此仍在验证。测试中的合成剂量只用于工程检查，不能宣传为复现了论文的个人风险。参照分布、标准化参数及个人概率模型参数未充分公开，不能凭分数正负、大小或论文人群比例判定这个人属于“风险三倍”人群，也不能把风险比直接套给个人。不同疾病的原始分数不可比较。

欧洲祖源研究不能直接给中国人校准风险；乳腺癌结果仅在女性中研究。遗传剂量不是生活方式目标，不提供 `--targets` 或 `levers.json`。

每份报告保留原句：

> 边界: 这是研究用的原始遗传加权分数，不是个人患病概率、风险百分位或单基因突变诊断；不能据此开始或停止用药，也不能据此决定筛查方案。

证据、材料清单及复现缺口见 `references/claims.md`、`references/contract.md`。完整权重的用途遵循 Broad 下载页列出的学术研究条款。
