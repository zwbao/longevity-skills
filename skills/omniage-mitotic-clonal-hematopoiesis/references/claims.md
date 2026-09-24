# 论文、代码、另一套同名东西

Du 等，Nature Communications 17:9130（2026），doi:10.1038/s41467-026-76038-w。全文由本地 PDF 抽出，16 页。

| | 内容 |
| --- | --- |
| 论文声称 | OmniAge 收了 413 个衰老组学标志、12 类。有丝分裂时钟（包括 epiTOC1/2 和 stemTOC）与克隆性造血、AdaptAge 相关；低甲基化时钟并不一致。EPIC-Italy 队列 845 人被用来看肿瘤风险。正文抽文本没有给出可单独引用的相关系数或比值比。 |
| 这份 Skill 实际算 | epiTOC2 的 tnsc。对上的探针才进入均值，缺失探针不填补。这与 `OmniAgePy` 里 `EpiTOC2.predict` 使用交集的做法一致。同一仓库的 R 函数在覆盖不到一半时返回空值，这里不跟那道门槛。有年龄时 irS = tnsc / 年龄。 |
| 代码实际算 | 仓库还有其余时钟的系数。本命令不调用它们。 |
| 同名的另一套 | epiTOC2 原论文是 Teschendorff 等，Genome Medicine 2020。pyaging 也能算一部分时钟，但不是这 413 个标志的合集。 |
