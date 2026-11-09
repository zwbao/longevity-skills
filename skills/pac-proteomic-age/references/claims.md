# Claims

论文：Zhavoronkov 等，Integration of proteomic aging clocks in a phase 2a clinical trial supports simultaneous geroprotective assessment，Nature Biotechnology，2026（2026-09-07 在线，开放获取），doi:10.1038/s41587-026-03286-y。

- **研究设计**：rentosertib（TNIK 抑制剂）治疗特发性肺纤维化的多中心、双盲、安慰剂对照、随机 2a 期试验（NCT05938920，中国 22 个中心，2023-07-19 至 2024-06-11）的蛋白质组**事后探索分析**。试验的主要结局不是衰老时钟；正文称这些结果为 “exploratory findings”。
- **全部样本组**：试验随机 71 人（30 mg QD 18、30 mg BID 18、60 mg QD 18、安慰剂 17）；完成试验 55 人，43 人签署蛋白组知情同意，1 人因第 12 周缺测排除，蛋白组分析 42 人：30 mg QD 11、30 mg BID 11、60 mg QD 9、安慰剂 11（补充表 S1）。平均年龄 67.1（SD 6.65）岁，范围 52–81 岁；男 38、女 4；全部为亚洲人。每人在基线、第 2、4、12 周各采一次血清，用 Olink Explore 3072 测，质控后 2,841 个蛋白。另用英国生物银行 55,319 名老年人的年龄相关蛋白作对照（正文）。
- **物种**：人（Homo sapiens）。没有动物或细胞实验数据进入本技能。
- **利益冲突**（原文 Competing interests）：A.Z. 是 Insilico Medicine（3696.HK）创始人兼 CEO；F.G.、S.C.、F.R.、A.A.、M.D.、D.S.、H.C. 为 Insilico Medicine 雇员；Insilico Medicine 开发了 rentosertib 等抗纤维化管线。proteoclock 库和 ipfP3GPT 时钟也出自 Insilico。其他作者声明无利益冲突。

| 论文声称什么 | 补充表里实际有什么 | 代码仓库实际算什么 | 同名的另一个项目 |
| --- | --- | --- | --- |
| 比较六个蛋白质组时钟：ProtAge、OrganAge mortality、OrganAge chrono、PAC、ipfP3GPT、PAOPAC（摘要、正文）。 | S2：每人每时间点六个时钟及各器官 OrganAge 的预测值，行用 NPX 行的 SHA256 匿名；输入 NPX 在 OMIX008341，受控访问。 | proteoclock（commit d078b24，MIT）实现 ipfP3GPT（权重受英国生物银行限制，仓库只有 feature_order.txt）、OrganAge 和 PAC（kuo_2024 权重文本）。 | — |
| PAC 来自 Kuo 等 Aging Cell 2024（参考文献 36），原始代码在 kuo-lab-uchc/PAC（Code availability）。 | S2 列名 `Kuo_2024(none)`：原始 NPX，不缩放。 | `pac_proteomic_age.R`（commit e15edb6）：128 个蛋白 + 年龄的 Gompertz 系数，shape、rate、shape0、rate0、beta_age，全部印在代码里；要求 128 个蛋白齐全，缺就停。proteoclock 的 kuo_conventinal.txt 同一组 129 个系数逐位一致，只有 rate 四舍五入成 2.32E-04。 | 本仓库 `proteomic-aging-clock` 是 Argentieri 2024 的 ProtAge（B 类，权重未公开），不是 PAC。 |
| OrganAge：先按均值和标准差标准化，再乘 Goeminne 2025 补充表 3 的 SD（Methods）。 | S2 列名却写 `Goeminne_2025(chrono_conventional_none)`，与 Methods 的标准化描述不一致。 | proteoclock 的 `standard` 变换用**这一批样本**的均值和 SD，单个人做不了。 | 本仓库 `organ-specific-proteomic-aging` 是另一篇器官时钟论文（Nature Aging 2025），不是 Goeminne 2025。 |
| ProtAge：MinMaxScaler 后按人群中位数中心化，权重“通过直接合作获得”（Methods）。 | — | proteomic-age-ukb 仓库不含权重（论文自述）。 | — |
| PAOPAC：JackieHanLab/PAOPAC（Code availability）。 | — | 仓库只有编译好的 Windows 模块 `pre.cp39-win_amd64.pyd` 和空的 `model/model.bin`，真模型在 Releases 另行下载；没有可读的权重。 | — |
| 六个时钟都显示治疗组 ΔBioAge 低于安慰剂；54 个比较中 21 个 q<0.10，集中在第 4 周（正文、S4、S5）。 | S5：PAC（Kuo）9 个比较中 2 个通过（30 mg QD 1、30 mg BID 1、60 mg QD 0）。S3：PAC 各组基线中位误差 −8.55 至 −15.62 岁。 | — | — |
| PAC 与 OrganAge mortality 是按死亡训练的时钟，与实足年龄只弱相关（r 0.16–0.23），对较年轻的受试者高估年龄（正文、Extended Data Fig. 1）。 | — | — | — |
| 时钟本身分不清是衰老变慢还是纤维化减轻（摘要）。最重要的特征 LTBP2 是纤维化调节因子，也是唯一出现在全部六个时钟里的重要特征（正文、S9）。 | S9：PAC 的重要贡献蛋白包括 LTBP2、AGER 等。 | — | — |

摘要和正文的差别：摘要列 “PAC”，正文第一次写成 “Kuo 2024”；同一个时钟。正文 “Han 2026” 与 S2 的 `Han_2025(Conventional)` 指同一个 PAOPAC。

打开过的材料：出版社全文页（开放获取）；补充表 xlsx（MOESM3，S1–S15 全部打开）；Reporting Summary（MOESM1）；Peer Review File（MOESM2）；GitHub：Insilico-org/proteoclock、kuo-lab-uchc/PAC、ludgergoeminne/organAging、JackieHanLab/PAOPAC；OMIX008341 页面（Controlled-access）。没有打开：miargentieri/proteomic-age-ukb（论文自述不含权重）、OSF 457w8（ipfP3GPT，权重受限）。
