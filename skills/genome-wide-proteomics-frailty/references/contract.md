用户提供诊断编码，或已经算好的医院衰弱风险分，以及现用药和体检。
技能不向用户索取 GEO、STRING 或 PDF。编码权重来自补充表，不来自 saige-pipelines。
报告把这次的合计放进低、中间或高。队列人数留在 claims。这是回顾性分组，不能写成开始或停止任何药物。

核对方式（validation: reproduced_secondary，显示为“已与独立实现核对”）：论文和 Gilbert 2018 都没有印出个人示例，所以在合成诊断清单（不是真人）上与两个独立实现逐例比对，见 `tests/test_validation.py`：comorbidipy 0.8.0（PyPI）的 `hfrs`，以及 m4（hannesill/m4，commit 5f6688a）的 `calculate_hfrs.py`。comorbidipy 把同一三位码组下的不同细码（如 G81.8 和 G81.4）各算一次，HFRS 每组只算一次，所以它只比没有重复组的清单。

补充表 18 第 24 行把“Care involving use of rehabilitation procedures”（康复操作，权重 2.1）印成 Z51。ICD-10 里这个名称对应 Z50（Z51 是“其他医疗照护”），表 18 照搬的 Gilbert 2018 附录表印的也是 Z50、权重 2.1，两个独立实现都用 Z50。脚本改用 Z50；109 个编码和合计 173.2 不变。
