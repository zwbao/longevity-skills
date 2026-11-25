# 产品合同

1. 用户提供自己完整饮食记录的蔬菜日均克数（按论文食物定义），可另给一个想比较的日均摄入情景。
2. 技能使用已核查并冻在 `scripts/presets.py` 的正文端点，无需用户收集论文、补充材料、作者代码或公开数据，运行不下载数据。
3. 报告只允许比较个人记录与论文人群参考范围，输出克数差距及位置；不提供个人绝对风险、相对风险、寿命、营养诊断或用药决策。

本流水线任务已授权实现以上 triage 所述摄入差距读出，不另设确认步骤。

## 可行性与数值来源

Stanaway 等，Nature Medicine 28，2066–2074（2022），doi:10.1038/s41591-022-01970-5。
所需全部论文常数只有下端点 306 和上端点 372 克/日。
出处为 Results → Minimum risk level of vegetable intake，Table 1 亦印出同一范围。
该范围是从研究暴露分布选择的人群参考范围，不是个体风险曲线的极小点或膳食安全上限。
Methods → Estimating the TMREL/minimum risk exposure level：跨研究最高摄入组下界的
第 85 百分位作下端点，最高摄入组区间中点的第 85 百分位作上端点。

本文食物口径见 Methods → Systematic review。包括新鲜、冷冻、烹调、罐装和干制蔬菜；
排除 legumes、salted or pickled vegetables、juices、nuts and seeds、starchy vegetables
（如 potatoes 或 corn）。不等同于通常所有“蔬菜”的总重，也不等同于蔬果合计。

对个人输入 x（g/d），定义下端点差值 L−x、上端点差值 U−x；低于下端点的距离
max(0,L−x)。x<L 为 below，L≤x≤U 为 within，x>U 为 above。
这些算术与包含端点的分类规则是本技能产品定义，不冒充论文验证过的个人评分公式。
论文端点的精度是整数克，内部保留输入精度，报告用可读数值呈现；不反推更精确端点。

`--targets` 接收同口径用户情景 t，计算同样输出及新旧差值。
`levers.json` 的 sensitivity 针对有符号 L−x，导数为 −1 g/d 每 g/d；
不对 max 的折点求导，不把摄入差距导数称为风险敏感度。

0–3000 g/d 是宽松的文件防错范围，不是论文阈值；1177 g/d 是 Results Overview
描述的最高观测摄入量，仅触发“超出观测范围”的提示。未指定年龄或性别截点。
只接受仓库单位表已有的 g/d（因子1）；不增加 kg/d、杯或份的隐含换算。
年龄、性别、药物和其他体检资料不改变结果。

## 验证状态

`validation.status=draft`，`inputs_status=draft`。全文、补充表1–7、图1–6、
Reporting Summary、作者蔬菜代码及 VizHub 数据中，没有独立印出的个人摄入差距算例。
Table 1 的零摄入对照和正文的两个端点可以核对零点算术，但直接回显端点不是独立复现。
先编写的 `tests/test_manifest.py::test_printed_reference_endpoints_and_zero_comparator`
仅用论文的 0、306、372 检查抄录与零点算术；因此不登记为 reproduced。
其他测试检查恒等关系、端点包含、错误输入拒绝、目标和文件重跑清理，不声称其合成值来自论文。

未重估 TMREL 的第85百分位、未重新训练 MR-BRT，也未实现疾病风险曲线。
作者 `veg_TMREL.R` 的输入是 FILEPATH 占位符，未附具体输入表；正文端点已够完成本合同，
这个缺口不影响本技能。补充表7和当前 VizHub 可见研究数据，不应因此说“论文没发表数据”。
当前 VizHub 的 IHD 研究数据行数与正文观察数不一致，未证实为发表时冻结版本，不用于替换2022端点。

## 固定边界

边界: 这里只比较饮食记录与论文的人群参考范围，不预测个人疾病风险，不证明改变摄入会带来相应获益，也不能据此开始或停止药物。
