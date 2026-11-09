# 可能骨肌减少症（OSTA 加握力）：合同、数值来源与核对

## 产品合同

1. 用户提供自己的体重、握力（优势手两次平均）、年龄和性别。
2. 技能自带论文印出的 OSTA 公式、切点和 AWGS 2019 握力切点，以及论文人群的关联结果；不向用户要论文、PDF 或补充材料。
3. 报告给出 OSTA 指数和分档、可能骨质疏松、可能肌少症、可能骨肌减少症（是或否），并把论文的内在能力、认知关联和筛查表现写成人群结果。不诊断骨质疏松、肌少症或认知障碍，不预测个人认知，不给药物建议。不能算的：DXA 定义的骨肌减少症（需要骨密度 T 值和 DXA 四肢瘦体重，用户一般没有）、内在能力总分（需要 MoCA、PHQ-9、步速、视听自评，论文没有给出个人可用的预测方程）。

## 来源

| 代号 | 出处 | 用到什么 |
| --- | --- | --- |
| [P] | Koh 等. Possible osteosarcopenia is associated with loss in intrinsic capacity and early cognitive deficits: a longitudinal study of older adults in Singapore. J Gerontol A Biol Sci Med Sci. 2026;81(11):glag211. doi:10.1093/gerona/glag211 | 方法“Possible osteoporosis”“Possible sarcopenia”“Possible osteosarcopenia”的公式和切点；表 2–4 和结果部分的人群数 |
| [S] | 同文 Supplementary data（glag211_supplementary_data.docx，期刊页面 Supplementary data 链接） | 补充表 2（DXA 金标准定义）、补充表 3（筛查表现）、补充表 11、12 |

全文从出版社开放获取页面读取；补充材料 docx 从期刊页面下载并逐表查看（补充表 1–19、补充图 1–2）。

## 方法（照原文）

- OSTA：“The OSTA index was calculated as: 0.2 × [Body weight (kg) - Age (years)]”。分档：“high (OSTA < –4), moderate (OSTA –4 to –1), and low (OSTA > –1)”；中、高风险合并为可能骨质疏松，即 OSTA ≤ −1。
- 论文没有说对指数取整。原始 OSTA 文献常把结果截去小数；按向零截断时，(−1, 0) 截成 0 仍是低风险，(−2, −1] 截成 −1 仍是中风险，所以“可能骨质疏松”是或否不受影响，只有 −4 附近的中、高风险分档可能差一档。脚本不取整，照论文写法。
- 握力：“Handgrip strength was measured twice in each hand with a Smedley spring-type dynamometer … The mean of the two measurements from the dominant hand was used. Possible sarcopenia was defined as handgrip strength <18 kg for women and <28 kg for men.” 正好 18 kg（女）或 28 kg（男）不算低。论文没有做 5 次起坐试验。
- 补充表 2 的 DXA 金标准写的是“maximum grip strength”，与正文可能肌少症用的“优势手两次平均”不同；本技能照正文的可能肌少症定义。
- 可能骨肌减少症：两项都符合；其余都归为没有。

## 人群结果（照印出的数，只作说明）

- 患病率 50.3%（1153/2291，11 人无法判定）。
- 表 3：内在能力总分 β −0.21（−0.29 到 −0.14）。补充表 11：基线认知能力完好的比值比 0.45（0.34 到 0.60）。
- 表 4：6 个月简版 MoCA，交互项 −0.59（−1.16 到 −0.03），与两者都没有者合计 −1.74。补充表 12 预测均值：认知下降组 11.64 对 11.08，认知完好组 12.84 对 12.82。
- 补充表 3：灵敏度 92.3%、特异度 71.4%、阳性预测值 48.6%、阴性预测值 96.9%、ROC 0.82；脚注写基于 515 人，正文写 895 人做了 DXA（两数不同，本技能照补充表写 515）。

## 核对

论文正文和补充材料都没有印出某个人的体重、年龄、握力对应的 OSTA 值或分类，也没有分组的体重、握力或 OSTA 均值（OSTA 是线性的，若印了分组均值本可核对），所以没有可复现的例子；`validation` 保持 `draft`。测试核对：常数与方法原文一致；OSTA 边界（正好 −1 和 −4 都是中风险）；握力边界（正好 18、28 kg 不算低）；lb 换算；单位缺失、超范围、缺性别或年龄时退出码 3、不输出数。

## 没有做的

- 不输出 `levers.json`：这是筛查分类，不是可以对着定目标的风险方程；OSTA 里体重越高分越高，把“增重”当目标会误导。
- 不估算个人认知下降或骨折风险：论文只给了人群关联。
