# 产品合同

1. **用户提供**：一份 Olink Explore NPX 表（每行一个蛋白，至少含 PAC 的 128 个蛋白）和采血那天的实足年龄；可选同一个人更早的一份 NPX 和那时的年龄；可选现用药、体检（只作背景）。
2. **技能自带**：PAC 的 128 个蛋白系数、年龄系数和两组 Gompertz 参数（`scripts/presets.py`，取自 kuo-lab-uchc/PAC `pac_proteomic_age.R` commit e15edb6，与论文所用 proteoclock commit d078b24 的 kuo_2024 权重核对过）。不需要下载任何文件。
3. **报告能说什么**：
   - 能算：PAC 蛋白质组年龄；PAC 减实足年龄；同一模型的 10 年全因死亡风险估计（英国生物银行人群模型，不是个人预测）；给了基线样本时，本次减基线的 PAC 变化（论文的 ΔBioAge）。
   - 不能算：ProtAge（权重未公开，要与作者合作）；ipfP3GPT（权重受英国生物银行限制）；OrganAge chrono 与 mortality（Methods 要按一批样本的均值和 SD 标准化，单个人没有这一批）；PAOPAC（只有编译模块和另行下载的模型文件，没有印出权重）；任何药物对这个人的作用。

## 计算

与 `pac_proteomic_age.R` 相同：

- b(x) = 0.029353964 × 年龄 + Σ β_i × NPX_i（128 个蛋白，原始 NPX，不缩放、不中心化）
- 累积风险 H = rate × e^{b(x)} / shape × (e^{10·shape} − 1)，10 年死亡风险 = 1 − e^{−H}
- PAC = ln( shape0 × (−H) / (rate0 × (1 − e^{10·shape0})) ) / beta_age0

脚本把 R 代码里的 log(1 − cdf) 直接写成 −H，数学上相同，在 cdf 接近 1 时更稳定。常数没有反推或拟合，全部照代码抄。

## 操作定义

- **缺蛋白**：R 代码缺任何一个就不算；proteoclock 会用训练均值补。本技能照原始 R 代码，缺就停（退出 3），不用 0 或均值补。
- **单位**：NPX 是 log2 相对量，`unit` 列留空或写 NPX/log2 NPX；浓度单位不能换算，拒绝。合理范围 −10 到 20 NPX，用来抓出把浓度填进 NPX 列的错误。
- **重叠检测 IL6**：Olink Explore 的几个面板各测一次 IL6，长表导出可能有几行 IL6。skillkit 遇到同一蛋白数值不同的两行会停下，请用户只保留一行；论文和 PAC 代码都没写用哪一个面板的 IL6，所以技能不替用户选。
- **FUT3-FUT5**：Olink 的一个合并检测；R 代码写作 fut3_fut5，proteoclock 写作 FUT3-FUT5，两种写法都认。
- **年龄**：PAC 在 39–70 岁的英国生物银行人群里拟合（kuo-lab-uchc/PAC README）；范围外照算，报告注明是外推。
- **批次**：论文 Methods 写明没有做桥接或锚定。PAC 系数是在英国生物银行的 NPX 上拟合的，别的实验室、别的批次的 NPX 有系统偏移，所以报告把单次绝对值的意义写得有限，并说明同一批次前后比较更可比。
- **没有 `--targets` 和 levers.json**：输入是 128 个血浆蛋白的相对丰度，不是一个人能对着定目标、直接调节的量，所以不提供“如果达到目标”的模型估计。

## 核对

论文补充表 S2 印了 42 名受试者各时间点的 PAC 预测，但输入 NPX 存在 OMIX008341，访问受控，无法重跑，所以 `validation` 是 `reproduced_secondary`，不是复现论文印出的例子：

- 7 个合成 NPX 样本（`tests/fixtures/synthetic_npx.csv`，不是真人；syn_7 全为 0）在 2026-11-09 用 Rscript 跑原始 `pac_proteomic_age.R`，本技能在 1e-5 岁内一致。
- 同样 7 个样本跑 proteoclock 的 `GompertzClock.predict_age(scaling=None)`（为了只加载计算代码，测试时替换了绘图依赖的导入，没有改它的计算代码），结果都比 R 高 0.018 岁；这是 proteoclock 把 rate 印成 2.32E-04 的结果（ln(2.32e-4/2.31560557596016e-4)/0.1087932 = 0.0175 岁），测试同时核对这一偏移。
- 另外发现：proteoclock 自带的测试数据 `kuo_test_data.tsv` 把那个检测写成 FUT3_FUT5，而权重文件写成 FUT3-FUT5，库会把它当缺失并补均值；本技能两种写法都认。
