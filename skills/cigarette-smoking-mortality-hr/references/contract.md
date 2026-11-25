# 产品合同与可行性核对

1. 用户提供自己的卷烟吸烟史（从未、既往、目前）；目前吸烟者再提供每日整数支数，可附年龄、性别及自己提出的每日支数目标。
2. 技能已从论文正文 Table 2 和补充 eTable 1 冻结所有所需分档、HR 和 95% CI，运行时不要求用户寻找公共文件，也不下载或拟合队列。
3. 报告只给个人匹配的吸烟分组及对应人群关联；不能给个人绝对死亡概率、寿命、戒烟因果收益、饮食分位数或五因素生活方式总分。

流水线已授权按可行的人体查表部分实现，因此没有另外要求交互确认。目录按方法命名。

## 可行性先于实现

2026-11-25 完成读取后才创建复现测试，随后实现脚本。
原始材料仅保留在临时目录，未将整篇论文或 PDF 加入仓库。

| 材料 | 打开情况及内容 |
|---|---|
| [DOI / 出版社文章页](https://www.ahajournals.org/doi/10.1161/CIRCULATIONAHA.117.032047) | HTTP 403；浏览器 CDP 连接失败，不能据此声称补充材料不存在 |
| [PMC 作者稿](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6207481/) | 旧 NCBI 路径成功读取完整正文、Table 1、Table 2、Figure 1–2 图注、参考文献和补充文件链接；直接新 PMC 路径触发验证 |
| [Europe PMC](https://europepmc.org/articles/PMC6207481) 及 fullTextXML 接口 | 页面访问失败，XML 接口返回 500；未作为数值来源 |
| [OpenAlex 元数据](https://api.openalex.org/works/https://doi.org/10.1161/circulationaha.117.032047) | 成功取得作者存档地址，用于发现文件，不作为计算来源 |
| [PMC Final Supplement](https://pmc.ncbi.nlm.nih.gov/articles/instance/6207481/bin/NIHMS949333-supplement-Final_Supplement.pdf) | 附件路径返回下载验证页；旧路径为 404，出版社附件路径 403，Europe PMC 附件路径 403 |
| [Cambridge 作者存档](https://www.repository.cam.ac.uk/handle/1810/275861) | 页面列出正文 CIRCULATIONAHA_2017_032047R2.pdf 和唯一补充 PDF CIRCULATIONAHA_2017_032047R2_Supplement.pdf |
| [Supplementary Appendix](https://www.repository.cam.ac.uk/bitstreams/acf48157-a4bd-4ec7-9413-a091e37fb17d/download) | 全部 16 页已打开：目录、eMethod pp.2–5、eTable 1 p.6、eFigures 1–8 pp.7–16；图像页另行渲染检查 |
| 代码、数据 | 正文 Methods 明确为向通讯作者合理申请 data, analytic methods, study materials；正文与该补充材料未点名公开 GitHub、Zenodo、OSF 或其他成品代码文件。NHANES 2013–2014、CDC WONDER 是群体生命表的数据来源，并不是吸烟 HR 查表的输入；本实现不下载、拟合或重建这些数据 |

## 逐项来源

正文 Table 2 列名为 Person Years、Deaths from any cause / Cases / RR (95% CI)、Cancer deaths / Cases / RR (95% CI)、Cardiovascular deaths / Cases / RR (95% CI)。尽管列头印 RR，表题、脚注及方法明确定义为 Cox hazard ratio，输出称 HR，不称风险概率。
补充 eTable 1 p.6 列名相同，但结局限于 participants prior to 75 years；是另一套敏感性分析，不能按用户当前年龄自动取代主分析。

两表的 Cigarette smoking 分档均为 Never、Past、Current 1–14/day、Current 15–24/day、Current ≥25/day。
`presets.py` 中 TABLE2、ETABLE1 的每个非参照行均按上述三个结局逐一冻结 (HR, CI下限, CI上限)。参照行原表只有 1.0(ref.)，CI 保持空值。
正文 Statistical Analysis 说明：吸烟史结合最近状态，每两年更新；本技能只把用户提供的当前史和支数映射到表格，不假装拥有其长期队列记录。

补充 eFigure 8 p.16 给出了吸烟单项分数，但缺饮食个人分位数的绝对切点，所以不输出总分，也不由图形反推精确常数。eMethod p.2 仅称 AHEI divided in quintiles，正文只称 top 40% of each cohort distribution。Table 1 的平均饮食分数不能替代切点。
群体生命表还使用按年龄、性别和暴露组的死亡率与患病/暴露频率及 Cox 年龄交互项；本技能未取得可直接完整复算该模型的逐项输入，也不从图像拟合或从外部来源猜值。

## 操作定义与输入护栏

- `cigarettes_per_day` 用无量纲计数单位 `1`，含义固定为每日卷烟支数。无获准转换单位；拒绝 pack/day、包年等，因每包数量没有固定个人值。
- 只接受整数，避免把 14.5、24.5 或少于一支的日均量擅自归档；不四舍五入。
- 0–200 是工程输入护栏，不是论文提供的生物学范围或阈值。当前吸烟至少一支；其他状态只能零支或省略。
- 年龄输入护栏 18–110 岁，仅背景；性别也只作背景。没有基于个人年龄、性别重新拟合 HR。
- 非卷烟、偶尔吸烟等不能外推，不从 NHANES 问卷的终生 100 支问题给 NHS/HPFS 强行补一个 Never 定义。
- 目标只改变当前吸烟者的支数；目标零支时对照 Past，不重写成 Never。表内差值没有联合置信区间，不能据现有 CI 拼装变化的 CI；敏感度不计算连续导数。

## 复现范围

测试先于实现创建，期望值直接抄自正文 Table 2 的 Current 15–24/day 和补充 eTable 1 对应行，包含三个结局及各自 CI。以 15 或 24 支进入印出的分档，返回全部印出值，精确一致。
另测 Never、Past、1、14、24、25 支的主分析全因 HR/CI，验证上下边界；目标比较使用两组印出的 HR，相减只属算术，不作为额外论文印刷示例。
没有拟合、反推常数或声称验证个人预测准确性；validation.reproduced 仅指分档查表复现。
