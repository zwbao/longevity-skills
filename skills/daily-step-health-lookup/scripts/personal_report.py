#!/usr/bin/env python3
"""Locate a daily step count in published Table 2, without fitting a curve."""
import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, OUTCOMES, TABLE, STEP_MIN, STEP_MAX,
                     STEP_INCREMENT, REFERENCE_STEPS, output_specs)

TITLE = "日均步数与健康结局查表"


def lookup(steps):
    if not math.isfinite(steps) or not STEP_MIN <= steps <= STEP_MAX:
        raise ValueError("step count outside the printed table")
    lower = math.floor(steps / STEP_INCREMENT) * STEP_INCREMENT
    upper = math.ceil(steps / STEP_INCREMENT) * STEP_INCREMENT
    outputs = {"steps_per_day": steps, "reference_steps_per_day": REFERENCE_STEPS,
               "lower_steps_per_day": lower, "upper_steps_per_day": upper,
               "lookup_mode": "exact" if lower == upper else "bracket"}
    for side, row in (("lower", lower), ("upper", upper)):
        for outcome in OUTCOMES:
            for stat, value in zip(("hr", "ci_low", "ci_high"), TABLE[row][outcome]):
                outputs[f"{outcome}_{side}_{stat}"] = value
    return outputs


def table_lines(outputs):
    rows = sorted({outputs["lower_steps_per_day"], outputs["upper_steps_per_day"]})
    lines = []
    for row in rows:
        lines += [f"### 表 2：{row} 步/日，相对 {REFERENCE_STEPS} 步/日", "",
                  "| 结局 | 人群 HR（95% CI） | 证据确定性 | 区间说明 |",
                  "|---|---|---|---|"]
        for outcome, (label, certainty, _, _) in OUTCOMES.items():
            hr, low, high = TABLE[row][outcome]
            if low is None:
                cell, note = "1（参照）", "参照行未印 CI"
            else:
                cell = f"{hr:.2f}（{low:.2f}–{high:.2f}）"
                note = "跨越或触及 1；按印出的区间不能判为明确差异" if low <= 1 <= high else "印出的区间不含 1"
            lines.append(f"| {label} | {cell} | {certainty} | {note} |")
        lines.append("")
    return lines


def make_levers(current, target):
    out = {
        "schema": "longevity-levers/1", "model": "daily-step-health-lookup",
        "model_zh": TITLE, "current": current,
        "sensitivity": [{"key": "steps_per_day", "unit": "1", "derivative": None,
                         "reason_zh": "原文提供离散表格，未提供可求局部导数的完整系数；不拟合敏感度。"}],
        "levers": [],
        "note_zh": "所有 HR 都以 2000 步/日为共同参照。HR 差仅为表值之差，不是目标相对当前的危险比，也不是个人改变步数后的获益预测。年龄不是杠杆。",
    }
    if target is not None:
        moved = lookup(target)
        exact = current["lookup_mode"] == moved["lookup_mode"] == "exact"
        delta = {key: moved[f"{key}_lower_hr"] - current[f"{key}_lower_hr"]
                 for key in OUTCOMES} if exact else None
        out["targets"] = {"values": {"steps_per_day": target}, "outputs": moved}
        out["levers"] = [{"key": "steps_per_day", "label_zh": "日均步数", "unit": "1",
                          "from": current["steps_per_day"], "to": target, "hr_delta": delta,
                          "note_zh": "仅两端均命中表行时计算 HR 差；相邻表行不作为个人估计区间。"}]
    return out


def collect(path, manifest):
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return {}, [skillkit.Problem("steps_per_day", "日均步数", "file", f"无法读取测量文件：{exc}")]
    # A single-person input, with no extra/unknown target keys silently ignored.
    problems = list(result.problems)
    if result.unmatched:
        problems.append(skillkit.Problem("steps_per_day", "日均步数", "unknown",
                                       "未识别的测量名称：" + "、".join(result.unmatched)))
    return result.values, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="实足年龄（岁），用于核对成人范围")
    parser.add_argument("--sex", help="可选背景信息，不改变合并表值")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json", "levers.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    measured, problems = collect(args.measurements, manifest)
    try:
        age = None if args.age is None else skillkit.parse_number(args.age)
        problems += skillkit.check_scalar(manifest, "age", age)
    except ValueError:
        age = None
        problems.append(skillkit.Problem("age", "实足年龄", "parse", "实足年龄必须是以岁为单位的有限数值。"))
    target = None
    if args.targets is not None:
        target_values, target_problems = collect(args.targets, manifest)
        for problem in target_problems:
            problem.message_zh = "目标表：" + problem.message_zh
        problems += target_problems
        target = target_values.get("steps_per_day")
    lines = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        lines += ["## 输入没有通过检查", "", "这次没有计算。", ""]
        lines += [f"- {p.message_zh}" for p in problems]
        lines += ["", "请提供设备记录的日均步数和实足年龄。单位 1 表示一天内的步数计数；不可填公里、分钟或每周总步数。",
                  "表外步数可能是真实测量，但本方法没有对应表值，不要为了查表修改原始测量。"]
        skillkit.write_result(args.out, manifest, {key: None for key in output_specs()})
        code = skillkit.EXIT_INPUT_PROBLEM
    else:
        outputs = lookup(measured["steps_per_day"])
        skillkit.write_result(args.out, manifest, outputs)
        levers = make_levers(outputs, target)
        (args.out / "levers.json").write_text(json.dumps(levers, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        lines += ["## 你的步数", "", f"日均 {outputs['steps_per_day']:g} 步；实足年龄 {age:g} 岁。",
                  "年龄只用于确认成人适用范围；没有按年龄、性别或设备校准这些合并结果。", ""]
        if outputs["lookup_mode"] == "bracket":
            lines += ["你的步数位于相邻两条已发表表行之间。下面只展示这两行；两行不是你的置信区间，也未算出你的 HR。", ""]
        else:
            lines += ["你的步数命中了已发表的表行。以下是该步数水平的人群合并关联。", ""]
        lines += table_lines(outputs)
        if target is not None:
            lines += ["## 你提供的目标步数", "", f"目标：{target:g} 步/日。", levers["note_zh"], ""]
            if levers["targets"]["outputs"]["lookup_mode"] == "bracket":
                lines += ["目标也在两条表行之间，仅展示相邻原值，不计算变化。", ""]
            lines += table_lines(levers["targets"]["outputs"])
        lines += ["## 如何理解", "",
                  "HR 是随访期间的相对危险率，不是一定时间内的发病概率。不同结局、研究的随访时间不同，不能相加或转成个人延寿年数。",
                  "跌倒的证据来自老年人群，确定性极低；不能用它判断你的行走安全。身体功能没有合并查表值。",
                  "这些是观察性研究；残余混杂、反向因果及研究间差异仍可能影响结果。日均步数应来自设备记录的典型多日平均，而非单次运动或某一天的最高值；论文未规定统一的个人采集天数。",
                  "不同设备与佩戴位置会产生系统性差异；本表没有设备换算系数，也不能覆盖骑行、划船等活动。",
                  "查表保留原表的非单调数值，不把更多步数解释成所有结局都持续改善；7000 步不是个人安全阈值或处方。",
                  "7000 步对应糖尿病的 CI 上限采用表 2 的 1.00，摘要印为 0.99；未以摘要覆盖表格。"]
        code = 0
    lines += ["", f"边界：{BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
