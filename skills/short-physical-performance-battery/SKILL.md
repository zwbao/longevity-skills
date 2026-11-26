---
name: short-physical-performance-battery
description: >-
  Tier A personal readout: computes one person's value with the paper's printed method and reproduces
  a printed example. Computes the original 1994 Short Physical Performance Battery (SPPB) from
  standing-balance records, two usual-speed 8-foot walks, and five repeated chair stands. Use when a
  person asks to score their SPPB, lower-extremity physical performance, walking and chair-rise tests,
  or 简易体能测试. Reports three component scores and their sum in Chinese, with optional target-score
  scenarios and explicit protocol and input checks.
---

# 原版简易体能测试组合（SPPB，8英尺）

用户命令：用我的平衡、8英尺步行和五次起立记录，计算原版 SPPB 得分。

读取 `skill.json` 的输入合同，用 `scripts/personal_report.py --measurements <CSV> --out <目录>` 生成 `report.md`、`result.json` 和 `levers.json`。可以用 `--age` 提供实足年龄，仅作适用人群提示。三项评分不按年龄或性别调整，不需要性别。

测量文件列为 `item,value,unit`。从用户已有的标准化记录录入，不要求用户找论文、附录、数据集或代码。所有计分常数已在 `scripts/presets.py` 中冻结。

## 原文测量流程与输入

- 先测半串联站立，填写 `semi_tandem_s`。不足 10 秒时填写 `side_by_side_s`；满 10 秒时填写 `full_tandem_s`。不属于本分支的那一项省略。半串联指一只脚的脚跟置于另一只脚大脚趾的侧面；全串联指一只脚的脚跟紧接另一只脚的脚趾。移动脚或抓住他人支撑时停止，最多计 10 秒。
- `walk_completed`：完成原文常速步行方案填 1；确认无法完成或因安全原因未尝试填 0。填 1 时提供 `walk_8ft_trial1_s` 和 `walk_8ft_trial2_s`，脚本取较快的一次。路径为 8 英尺，两端各留 2 英尺无障碍空间，可使用助行器。不要填 4 米、6 米、最快速度步行的结果。
- `chair_completed`：按原文完成五次起立填 1，确认不能完成或因安全原因未尝试填 0。填 1 时提供 `five_chair_stands_s`。直背椅靠墙，双臂在胸前交叉，先确认能完成一次起立，再尽快连续完成五次。从坐位开始，到第 5 次完全站直停止计时；不是第 5 次坐下。不得把用手撑起的成绩当成完成。
- 完成状态填 0 时省略该项用时。平衡的 0 秒可编码确认无法完成或因安全原因未尝试；缺测、拒测、器材问题和不清楚结果不能填 0。
- 为严格使用原文印出的区间，平衡只收整秒记录，步行与起立只收 0.1 秒精度记录。不自行舍入更精细的秒数，不插补区间。单位为 `s`，也接受 `ms` 和 `min` 精确换算；别名未注明单位会停止。

这些是计分所需的协议说明，不代替现场测试培训。论文采用受过训练的访员现场评估；不要让有跌倒风险的人独自尝试，不能安全完成的项目不强行进行。

## 可选目标情景

若用户明确给出想比较的成绩，用 `--targets <CSV>`，列与测量文件相同。目标覆盖本次相应字段，遗漏字段保留现值；只比较覆盖后仍符合协议的记录。不能以空白删除旧字段，因此变更平衡分支需重新提供一份完整测量文件。

`levers.json` 给出当前得分、每项输入在记录精度下的一步敏感度、每个目标单独变化和同时变化的得分。单独变更导致缺项或协议冲突时，变化值为 null 并解释原因。分数离散，不给连续导数，不把加分解释为治疗效果、寿命延长或风险下降。

## 输出和失败处理

输出平衡、8英尺步行、五次起立各 0–4 分及总分 0–12 分，不另设“衰弱/正常”分档。仅有三项完整且一致的记录才计算。缺项、错单位、越界、记录精度不符或协议矛盾时，退出码为 3，写 `problems.json` 和含论文卡片的中文说明，不保留旧的计算结果。

每份报告保留论文卡片和下述原样边界：

边界: 本报告仅按 1994 年原版 8 英尺方案描述下肢体能，不诊断失能或衰弱，不预测你的死亡、入住养老机构或跌倒概率，不据此决定照护安置，也不能据此开始或停用药物。

原文依据、材料访问记录及验证范围见 `references/contract.md`、`references/claims.md`。
