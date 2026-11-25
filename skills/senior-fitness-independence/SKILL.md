---
name: senior-fitness-independence
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Compares standardized Senior Fitness Test measurements with age- and sex-specific
  criterion standards for physical independence in adults aged 60–94. Use for chair stand, arm curl,
  six-minute walk, two-minute step, or eight-foot up-and-go results, their distance from published
  standards, and hypothetical target comparisons.
---

# 老年体能与独立生活参考标准

适用于已有标准化 SFT 测量的 60–94 周岁成人。读取年龄、论文分组性别和至少一项已测成绩，逐项比较正文表 4。年龄按整数周岁分入五岁组，不插值，不外推。分组仅支持论文的 male/female，可输入男/女；不自行推断。

用户命令：

> 用我的 SFT 体能测量、年龄和性别，对照晚年独立生活参考标准，说明哪些项目达到标准、哪些还存在差距。

## 运行

用 `scripts/personal_report.py --measurements measurements.csv --age 73 --sex male --out out`。
目标成绩可加 `--targets targets.csv`，表头同测量表。目标仅限已提供当前成绩的项目。

CSV 表头为 `marker,value,unit`，可用下列键或清单中的中英文名称：

| 键 | 测量 | 单位 |
|---|---|---|
| chair_stand_count | 30 秒椅子起立次数，双臂交叉于胸前 | 1（整数次数） |
| arm_curl_count | 30 秒弯举次数；测试负重女性 5 磅、男性 8 磅 | 1（整数次数） |
| walk_6min_m | 6 分钟步行距离，按 SFT 的 50 码路线完成 | m，也接受 cm |
| step_2min_count | 2 分钟内右膝达到规定高度的次数 | 1（整数次数） |
| up_go_s | 起立、走 8 英尺、转身并返回坐下的时间 | s，也接受 min |

踏步高度为髌骨与髂嵴之间的中点；不要把双腿合计次数作为输入。8 英尺等于 2.4384 米，3 米 TUG 不可替代。这里列的是测量条件；完整施测程序应由熟悉 SFT 的测评人员执行，不把测试负重转成训练处方。只改变单位不代表可以改变测试程序。

五项可交一项或多项。两种耐力测试互为替代项，均提供时分别呈现，不选最好的一项作为综合结论。未测项目留空，不用零补齐；实际测得零次数或零距离可以输入。不能完成计时项目时不要用零秒代替。

## 输出和输入问题

- `out/report.md`：中文论文卡片、年龄组、逐项测量/切点/差距/达标情况与边界。
- `out/result.json`：每项 `value`、`cutoff`、`margin`、`status`；未测项目的成绩、差距和分档为 null。
- `out/levers.json`：当前差距对本项成绩的敏感度、单项目标和同时达到全部目标的查表结果；不是训练效果预测。
- 缺年龄、性别、全部成绩，或任一已提供输入无效：退出 3，写 `out/problems.json`；说明需要补充或纠正的测量。部分项目未提供时仅报告已测项目。

次数、距离越高越好，起立行走时间越低越好；恰好达到切点算达标。差距以有利方向为正，不合并成总分。合理范围是输入防错范围，不是论文正常值范围。

不向用户索要论文、公开表格、队列数据或代码。所有计算切点已在 `scripts/presets.py` 固定，离线可用；不下载完整论文到技能目录。出处、完整材料核查和复现说明见 `references/contract.md` 与 `references/claims.md`。

每份报告必须保留：

> 边界：本报告只比较标准化 SFT 测量与论文参考切点，不诊断失能，不预测你能否独立生活到 90 岁，也不估计寿命或给出运动、用药处方。

不要把达标解释成未来独立生活的保证，也不要把未达标解释成当前失能。不给药物剂量，不提出开始或停止用药。
