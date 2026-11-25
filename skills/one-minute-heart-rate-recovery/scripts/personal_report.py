#!/usr/bin/env python3
"""Read a completed exercise test; never prescribe an exercise test."""
import argparse
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    ABNORMAL_CUTOFF_BPM, BOUNDARY, COOLDOWN_MINUTES, PROTOCOL,
    RECOVERY_MINUTES, TITLE, TREADMILL_GRADE_PERCENT, TREADMILL_SPEED_KMH,
    calculate,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age")
    parser.add_argument("--sex", help="可选背景信息，不进入公式")
    parser.add_argument("--protocol", help="仅在已核实原文测量方案时填写 cole-1999")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, UnicodeError, ValueError) as exc:
        collected = skillkit.Collected(problems=[skillkit.Problem(
            "measurements", "测量文件", "file", f"无法读取测量表：{exc}。请提供 marker,value,unit 三列表格。"
        )])
    problems = list(collected.problems)
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, "age", age)
    except ValueError:
        problems.append(skillkit.Problem("age", "实足年龄", "number", "实足年龄须为有限的岁数。"))
    if args.protocol != PROTOCOL:
        problems.append(skillkit.Problem(
            "protocol", "测量方案", "protocol",
            f"请从已有运动试验报告核实：症状限制性跑台运动达到峰值后，以约 {TREADMILL_SPEED_KMH:g} km/h、"
            f"{TREADMILL_GRADE_PERCENT:g}% 坡度主动恢复至少 {COOLDOWN_MINUTES} 分钟，"
            f"心率取峰值与恢复第 {RECOVERY_MINUTES} 分钟。核实后填写 --protocol {PROTOCOL}；"
            "坐位、卧位、完全静止恢复或普通手环运动记录不能直接套用。"
        ))
    card = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        skillkit.write_problems(args.out, problems, TITLE, BOUNDARY.removeprefix("边界: "))
        skillkit.write_result(args.out, manifest, {s["key"]: None for s in manifest["outputs"]})
        lines = card + ["## 输入没有通过检查", "", "这次没有计算。"]
        lines += [f"- {p.message_zh}" for p in problems]
        lines += ["", "请核对已有报告中的数值、时间点和方案，不要以估计值补齐。", "", BOUNDARY]
        (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    peak = collected.values["peak_hr_bpm"]
    recovery = collected.values["recovery_hr_1min_bpm"]
    outputs = calculate(peak, recovery)
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / "problems.json").unlink(missing_ok=True)
    label = "恢复偏慢（原文 abnormal）" if outputs["hrr_category"] == "abnormal" else "未达到恢复偏慢切点（原文 normal）"
    lines = card + [
        "## 你的结果", "",
        f"峰值心率 {peak:g} 次/分，主动恢复第 {RECOVERY_MINUTES} 分钟心率 {recovery:g} 次/分。",
        f"心率下降量 = {peak:g} − {recovery:g} = {outputs['hrr_1min_bpm']:g} 次/分。",
        f"原文分档：**{label}**。下降量 ≤{ABNORMAL_CUTOFF_BPM} 次/分属于恢复偏慢，等于切点也计入。", "",
        "## 怎样理解", "",
        "这是运动试验中的一项预后标志。未达到切点不等于没有心血管风险，也不表示已经排除疾病。",
        "原研究来自单中心转诊接受诊断性运动试验的成年人；切点在同一队列选出并评估，未报告独立验证队列。",
        "既往冠状动脉造影、心脏手术或血运重建、起搏器、心力衰竭或地高辛使用、先天性或瓣膜性心脏病、"
        "预激综合征、左束支传导阻滞均涉及原研究排除条件；有这些情况时，不可沿用该研究的预后解释。",
        "年龄用于确认成年人范围，性别不改变这个切点；现用药及完整运动试验结果应由医生结合解读。",
        "技能为暂定版：已核对计算定义和切点，但原文没有可复现的个人输入—输出示例。",
    ]
    if outputs["hrr_1min_bpm"] <= 0:
        lines += ["这次心率未下降；保留原始有符号差值。请核对时间点、测量记录及恢复方案，并交由医生结合完整试验解读。"]
    lines += ["", BOUNDARY]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
