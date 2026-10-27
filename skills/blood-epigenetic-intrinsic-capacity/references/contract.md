用户提供 91 个 CpG 的血液甲基化 β 值（Illumina EPIC），可附现用药和体检。
技能自带补充表 1 的截距 0.7852837523517947 和 91 个弹性网系数（逐项与补充表 1 核对一致），按 截距 + Σ 系数 × β 算甲基化内在能力；不向用户要 GEO、STRING、PDF。
任一位点缺失、β 不在 0 到 1、单位不是 β 时不计算，退出码 3。
论文正文、扩展数据和补充表 1–8 都没有印出个人 β 值与对应预测值，作者仓库 msfuentealba/IC_clock 也没有示例数据，所以 validation 是 reproduced_secondary（显示为“已与独立实现核对”）：在 6 个合成样本（随机 β 值，不是真人）上与 pyaging 0.5.7 的 dnamic 时钟（Hugging Face pyaging/dnamic 修订 9a759c2）和 FALCONAge（commit 86db10d）的 dnamic.csv 线性模型逐例比对，误差要求 1e-6 以内，见 `tests/test_validation.py`。FALCONAge 的系数是它自己从补充表 1 转录的，这一条核对的主要是系数转录和截距。
报告不做死亡预测，不能写成开始或停止任何药物。
