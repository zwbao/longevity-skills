# 产品合同：SASP 评分（GAET）

1. **用户提供**：一份 38 个血浆蛋白的 Olink Explore 3072 NPX 值表（`marker,value,unit`，单位写 NPX），与 UK Biobank Pharma Proteomics Project（UKB-PPP）同一标准化。名称可以是基因符号（GDF15）、常用名（GDF-15、PAI-1、YKL-40）或键名（`gdf15_npx`）。不需要年龄：模型训练时用年龄引导，算分时不用年龄。
2. **技能自带**：作者在 GitHub 公开的预训练模型 `tgae_pre_trained.pth`（shangshuzhao/sasp，提交 34d5f1becd2f9d7378feec870b59e459fe451d0c，MIT；sha256 b34230d4…41c5）。只取算分用到的编码器、`latent_proj` 和 `regressor` 张量，原值存成 `data/gaet_pretrained_encoder.npz`（float32）。`scripts/gaet.py` 用 NumPy 重写 `TGAE.predict`；在 200 组随机输入上与作者 PyTorch 代码的最大差 0.00023。解码器只做重建，不参与算分。UKB-PPP 每个蛋白的均值和标准差取自作者代码 `proteins_info.match_ukb_dist`，只用来检查标度和描述单个蛋白，不进入评分。
3. **报告能说**：SASP 评分（一个数）；是否高于论文的 65 分切点（论文：训练样本中基线没有主要慢病者的第 90 百分位）；哪些蛋白离 UKB-PPP 平均值至少 3 个标准差（描述，不是模型贡献）；论文的人群数字（单列，不当作个人结果）。
   **报告不能说**：年龄差或“衰老加速”（论文没有定义）；单个蛋白对分数的 SHAP 贡献（需要训练集做参照，没有公开）；个人的死亡或患病概率（论文只报告每 1 SD 的风险比和 C 指数，没有基线风险）；其他平台（Olink Target、Luminex、浓度单位）的分数（论文在 MEDEX 里对整组数据做 Cycloess 标准化、插补并微调模型，一个人的样本做不到）。

## 输入检查

- 38 项全部必需。论文和作者 README 都用完整的 38 项（UKB 用 KNN 插补后的完整数据），所以缺一项就停，不用模型的“可变长度”去跳过。
- 单位列必须写 NPX（键名 `*_npx` 本身表示 NPX，可以不写）。写 pg/mL、ng/mL 等浓度单位或没写单位的，停下并说明原因：浓度不能换成 NPX；IL-6、瘦素、VEGF 这类在普通化验单上也会出现的名称，读错单位后仍会落在 NPX 范围内。
- 每项合理范围 −10 到 15 NPX。
- 标度检查：38 项相对 UKB-PPP 均值的 |z| 中位数大于 3 就停。UKB-PPP 的 NPX 以 0 附近为中心；Olink Target 96、未按 UKB-PPP 标准化的 NPX 或线性值会远离。这一阈值是本技能的工程选择，论文没有给。

## 验证状态

`validation.status = draft`。论文正文和 Data S1 没有印出任何个人输入和对应分数；作者仓库的 `example.ipynb` 没有保存运行输出。测试只断言：论文印出的 38 个蛋白名单和 65 分切点；NumPy 实现与作者 PyTorch 代码在三组固定输入（UKB 均值、均值 ±1 SD）上的输出一致（这些期望值是作者代码的输出，不是论文印出的数字）。

## 已知性质

模型是非线性的，分数不随每个蛋白单调变化：38 项都设为 UKB 均值 +1 SD 时作者代码输出约 65.4，+2 SD 时约 64.0。所以报告不说“某个蛋白降下来分数就会降”，也不提供 `--targets` 或 `levers.json`。
