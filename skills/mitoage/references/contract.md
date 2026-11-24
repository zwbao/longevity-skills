# 产品合同

1. 使用者提供本人SomaScan 1.3K对应25个SeqId、经过实验室质控后的自然对数RFU及模型性别；可附实足年龄和同尺度目标值。
2. 技能使用已从期刊Supplementary Data 1冻结的25蛋白权重、截距和性别系数；使用者不负责寻找论文、补充材料或训练数据。
3. 报告只算公开线性式的MitoAge分值及输入替换的数学差异，不算年龄岁数、疾病风险、实测细胞呼吸率、健康分档或干预效果；没有完整个人算例，所以保持draft。

流水线请求已经授权按该范围实现，不另设交互批准步骤。

## 公式与出处

Heimler 等，npj Aging 12:158 (2026)，DOI 10.1038/s41514-026-00449-8。

`score = intercept + sex_male_weight * male + Σ weight_i * ln_rfu_i`。

- `data/coefficients.csv`：Supplementary Data 1，MitoAge工作表，A2:K26；G列为Weight。保留Excel存储的数值精度。
- `data/constants.json`：同表G27=7.4965377585326696，G28=-0.120048854106948。JSON中的前者为相同二进制浮点数的最短往返表示7.49653775853267，不是另行拟合。
- Table 2（期刊PDF第5页）明确写 `Sex (Male)`，对应男性指示变量male=1、女性参照=0。XLSX只写sex01，因此必须同时核对PDF；不能仅凭变量名判断性别编码。
- Methods / Proteomics（PDF第8页）明确写natural log-transformation。输入为已经处理好的自然对数RFU，单位记无量纲`1`，不是ln浓度、log2或Olink NPX。
- 不采用eNetXplorer Results工作表的Coefficient替代MitoAge的Weight，不使用单变量表的beta_coefficient。

## 输入准备及未核验尺度

论文还描述按队列删除4 SD外的离群值并KNN填补。公开XLSX没有88位参与者的蛋白矩阵或KNN参考数据，不能在单人报告中重做队列质控。这里的产品入口限定为实验室已完成同平台质控的个人ln-RFU向量，不接收缺失项，也不实现队列重处理。`--preprocessing somascan-1.3k-ln-qc`要求使用者确认实际处理状态；这不是自动检测真实性。

按公开文字逐字实现自然对数丰度的线性式，不自行加入任何未报告的中心化、z标准化、反向缩放或输出指数变换。由于没有个人输入与预测值配对，无法证明这一绝对数值尺度与作者运行结果相同。尤其不能因为某组输入得到负值，就减均值或加常数去追赶Figure 4的点云。报告保留这一限制以及原始数值，不命名为pmol/min。

`[-20,30]`是ln-RFU的宽松工程防错范围（约对应正RFU的2×10^-9至10^13），不是论文健康参考区间。它能挡住常见直接粘贴的数千RFU，不能识别数值落在范围内的log2或z分数；显式单位、处理状态和SeqId核对仍是必须的。年龄18–120岁同样是输入防错范围；22–92岁才是论文研究范围。没有已验证的跨平台或浓度换算，因此`accept`为空，不填未经核对的LOINC。

## 验证缺口

检索了HTML、10页期刊PDF中的Table 1–4、Figure 1–5及Methods、补充PDF的Figure S1/Table S1、Supplementary Data 1全部三个工作表和所引eNetXplorer仓库。没有完整的25项个人输入、性别和预测分值配对；Figure 4中的参与者编号、均值和误差线没有相应输入表。关联、介导比例和模型性能不能替代个人计算示例。

因此`validation.status=draft`，`inputs_status=draft`，不设置虚构的reproduced例子。测试先于计算脚本编写：核对印出的截距、男性权重和蛋白权重；零向量回到截距、单项变化等仅作合成算术与接口检查，**零向量不是论文中的人**，不声称是生理典型值。没有用第三方输出拟合常数，也没有按图反推常数。

## 输出与目标情景

只输出`mitoage_score`。`levers.json`使用`score_per_unit`表示每增加1个ln-RFU单位的代数敏感度；没有使用years_per_unit。支持部分蛋白目标，逐个计算分值变化，全部目标再一起代入。性别、年龄、药物和其他化验不能作为目标或改变公式。变化仅是模型中的算术，不证明因果关系，不推荐提升或降低某蛋白。

所有失败报告同样带论文卡片和边界句。缺项、错单位、非有限数、未知目标或不符的数据状态都退出3，并清掉旧result.json与levers.json，防止读取历史成功结果。
