# 产品合同

1. **用户提供**：一个人的血液甲基化芯片 β 值表（`item,value,unit`，item 是 cg 号）；可选实足年龄、现用药、体检。
2. **技能自带**：`data/table_s15_dmp_dvp_epic.csv`（补充表 S15 原样转写，EPIC 模型，789 个不同位点）和 `data/DVP_DMP_450K.csv`（作者仓库 oliversion/epg-aging 提交 6a3cb4443c8d5d6bda59b21b0a87cbe44a179517 的同名文件，450K 限定模型，598 个不同位点）。来源和 sha256 写在 `skill.json` 的 `data_files`。
3. **报告允许说什么**：
   - 能算：两个模型各自的整合 DMP-DVP 评分（年刻度），位点交齐才算。
   - 不能算：论文的最终指标“表观年龄偏差”（分数对实足年龄回归的残差）——回归截距和斜率不在正文、补充表 S1–S18、补充说明 1–2 或代码仓库里；每一项方法学健康分（FI、CF、PF）的单独预测——弹性网训练式写了 age + sex，但 S15 和仓库都没有年龄、性别的系数，单项预测不完整，所以只报告合成后的分数；任何个人死亡或疾病风险——论文只给了队列里的风险比和 C 指数。

## 计算

与作者脚本 `eScores.R` 相同：

```
M        = log2(β) − log2(1 − β)
s_k      = 截距_k + Σ w_k,cpg × M_cpg            k = FI, CF, PF
raw      = COX_FI × s_FI + COX_CF × s_CF + COX_PF × s_PF
score    = (raw − mean_bio) / sd_bio × sd_age + mean_age
```

与作者脚本不同的一处：`eScores.R` 把缺的位点按 0（M 值 0，即 β = 0.5）补上；本技能不补，缺任何一个位点就不算那个模型（paper-to-skill 规则“缺特征就不要用 0 去补”）。

## 和正文写法的差别

正文方法写“每个健康分先按年龄均值和标准差缩放，再对年龄回归取残差”，然后 Cox 加权。补充表 S15 和作者脚本实际做的是：三个原始健康分直接按 COX 权重相加，再整体按 `mean_bio`、`sd_bio` 换到年龄刻度（`mean_age` 63.243813015582，`sd_age` 10.214001261888），不取残差。S15 只印了一组 `mean_bio`/`sd_bio`，与脚本一致，所以技能照 S15 和脚本做。

## 复现

论文正文和补充材料没有印任何个人的 β 值和对应分数。作者在正文 Code availability 点名的仓库里，`demo/output.csv` 印出了 `demo/demo_data.csv` 每个样本的 `DVP_DMP_450K` 分数，`README.md` 印出第一个样本（ID001 = 2013）四位小数的分数。`tests/test_manifest.py::test_reproduces_author_demo_output_450k` 用这三个样本的原始 β 值（`tests/fixtures/epg_aging_demo_450k.csv`，从 demo_data.csv 原样截取 598 列）复现：2025 → 69.7652073414805，2090 → 60.9704121365349（误差 < 1e-9），2013 → 55.6395（4 位小数）。

EPIC 模型没有可复现的印出例子；它与 450K 模型走同一段代码，只换权重文件，测试核对 S15 的截距、COX 权重和换算常数原值，以及每项位点数与表 S14（212、254、342）和补充说明 2（789 个不同位点）一致。

## 输入的操作定义

- 论文训练时用去除免疫细胞比例后的残差 M 值（Methods: Statistics and reproducibility）；作者脚本对用户数据直接用 β 换 M，不做细胞校正。技能照脚本做，报告写明这会带来偏移。
- β 值等于 0 或 1 时 M 值无穷大，技能当作输入问题停下。
