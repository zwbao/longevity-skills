"""Offline short IPAQ pace-specific arithmetic, Craig et al. (2003)."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (ACTIVITIES, BOUNDARY, LABELS, METS, MIN_BOUT_MIN,
                     PACE_LABELS, TITLE, WALKING_METS)


def collect(path, manifest, target=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError, AttributeError) as exc:
        return {}, [skillkit.Problem("measurements", "问卷文件", "file", f"文件无法读取：{exc}")]
    problems = [p for p in collected.problems if not (target and p.kind == "missing")]
    if collected.unmatched:
        problems.append(skillkit.Problem("measurements", "问卷项目", "unknown", "无法识别项目：" + "、".join(collected.unmatched)))
    if target and not collected.values and not problems:
        problems.append(skillkit.Problem("targets", "目标", "missing", "目标文件至少需要一个已知项目的有效值。"))
    if target:
        for problem in problems:
            problem.message_zh = "目标文件：" + problem.message_zh
    return collected.values, problems


def consistency(values):
    problems = []
    for activity in ACTIVITIES:
        days, minutes = values.get(f"{activity}_days"), values.get(f"{activity}_min")
        if days is not None and not float(days).is_integer():
            problems.append(skillkit.Problem(f"{activity}_days", LABELS[activity], "integer", f"{LABELS[activity]}天数必须是整数。"))
        if days is None or minutes is None:
            continue
        if (days == 0) != (minutes == 0):
            problems.append(skillkit.Problem(f"{activity}_min", LABELS[activity], "inconsistent", f"{LABELS[activity]}的天数和时长须同时为零，或同时为正；没有活动须明确填写两个零。"))
        elif 0 < minutes < MIN_BOUT_MIN:
            problems.append(skillkit.Problem(f"{activity}_min", LABELS[activity], "bout", f"{LABELS[activity]}仅统计每次持续至少 {MIN_BOUT_MIN} 分钟的活动，活动日平均时长小于此值。请核对，不能自动凑整。"))
    return problems


def weights(pace):
    return {**METS, "walking": WALKING_METS[pace]}


def score(values, pace):
    met = weights(pace)
    result = {f"{a}_met_min_week": values[f"{a}_days"] * values[f"{a}_min"] * met[a] for a in ACTIVITIES}
    result["total_met_min_week"] = sum(result.values())
    result["walking_pace"] = pace
    result["sitting_weekday_min"] = values.get("sitting_weekday_min")
    return result


def levers(values, targets, pace, manifest):
    current = score(values, pace)
    specs = {s["key"]: s for s in skillkit.input_specs(manifest)}
    sensitivity = []
    for activity, met in weights(pace).items():
        for suffix, other in (("days", "min"), ("min", "days")):
            key = f"{activity}_{suffix}"
            sensitivity.append({"key": key, "label_zh": specs[key]["label_zh"],
                                "unit": specs[key]["unit"], "value": values[key],
                                "met_min_week_per_unit": met * values[f"{activity}_{other}"],
                                "method": "exact_partial_slope_fixed_other_input"})
    if "sitting_weekday_min" in values:
        sensitivity.append({"key": "sitting_weekday_min", "unit": "min",
                            "value": values["sitting_weekday_min"], "met_min_week_per_unit": 0,
                            "method": "excluded_from_activity_total"})
    result = {"schema": "longevity-levers/1", "model": manifest["name"], "model_zh": TITLE,
              "current": current, "sensitivity": sensitivity, "levers": [],
              "note_zh": "固定步行速度；敏感度是公式斜率，天数只能取整数。目标需保持同一回忆口径；只比较活动量，不预测健康效应，也不推荐目标。零活动变为有活动需同时改变天数和时长。"}
    if targets:
        together = score({**values, **targets}, pace)
        result["targets"] = {"values": targets, "outputs": together,
                             "total_delta": together["total_met_min_week"] - current["total_met_min_week"]}
        for key, target in targets.items():
            moved = {**values, key: target}
            problems = consistency(moved)
            output = None if problems else score(moved, pace)
            result["levers"].append({"key": key, "label_zh": specs[key]["label_zh"],
                                     "unit": specs[key]["unit"], "from": values.get(key), "to": target,
                                     "outputs": output,
                                     "total_delta": None if output is None else output["total_met_min_week"] - current["total_met_min_week"],
                                     "reason_zh": "；".join(p.message_zh for p in problems)})
    return result


def render(values, result, scenarios):
    pace = result["walking_pace"]
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的活动量", "",
             "口径：过去七天短表，使用 2003 年论文的步行速度分支。仅计每次持续至少十分钟的活动；工作、交通、家务和休闲都包括在内，同一活动不要重复填入不同强度。", "",
             f"步行速度：{PACE_LABELS[pace]}。总活动量为 **{result['total_met_min_week']:g} MET·分钟/周**。", "",
             "| 项目 | 活动天数 | 活动日平均分钟 | MET 权重 | MET·分钟/周 |", "|---|---:|---:|---:|---:|"]
    for a in ACTIVITIES:
        lines.append(f"| {LABELS[a]} | {values[f'{a}_days']:g} | {values[f'{a}_min']:g} | {weights(pace)[a]:g} | {result[f'{a}_met_min_week']:g} |")
    sitting = result["sitting_weekday_min"]
    lines += ["", "未提供工作日坐姿时长；这不影响活动量汇总。" if sitting is None else f"工作日平均坐姿时长：{sitting:g} 分钟，单列记录，不加入总活动量。"]
    lines += ["", "论文没有提供可复现的个人总分算例，因此尚未复现个人总分，验证状态仍为暂定。论文用于成年人群监测，个人自报可能有回忆偏差；本实现限正文讨论的十八至六十五岁范围。",
              "", "作者发现加入步行速度没有明显改善测量表现，并建议后续问卷删除速度问题；本结果对应其按速度计分分析，与后来版本的标准 IPAQ 分数口径不同。"]
    if "targets" in scenarios:
        target = scenarios["targets"]
        lines += ["", "## 你指定的目标情景", "", f"固定步行速度，所有目标一起实现时：{target['outputs']['total_met_min_week']:g} MET·分钟/周；与当前相差 {target['total_delta']:+g} MET·分钟/周。仅作算术比较，不代表建议达到这个活动量。"]
    lines += ["", f"边界: {BOUNDARY}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--walking-pace", help="slow / moderate / vigorous；按原问卷自报速度，不推断速度")
    parser.add_argument("--age", help="正文适用范围 18–65 岁")
    parser.add_argument("--sex", help="可选 male/female；不影响计算")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("report.md", "result.json", "problems.json", "levers.json"):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    problems += consistency(values)
    try:
        age = None if args.age is None else skillkit.parse_number(args.age)
        problems += skillkit.check_scalar(manifest, "age", age)
    except ValueError:
        problems.append(skillkit.Problem("age", "年龄", "parse", "年龄必须为有限数值。"))
    if args.walking_pace not in WALKING_METS:
        problems.append(skillkit.Problem("walking_pace", "步行速度", "missing" if args.walking_pace is None else "category", "请明确提供 --walking-pace slow（慢）、moderate（中等）或 vigorous（快／高强度）；本版本固定使用按步行速度计分的分支。"))
    if args.sex is not None and args.sex not in ("male", "female"):
        problems.append(skillkit.Problem("sex", "性别", "category", "性别可省略；如提供只接受 male/female，不影响分数。"))
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, target=True)
        problems += target_problems
        problems += consistency({**values, **targets})
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        skillkit.write_result(args.out, manifest, {s["key"]: None for s in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    result = score(values, args.walking_pace)
    scenarios = levers(values, targets, args.walking_pace, manifest)
    skillkit.write_result(args.out, manifest, result)
    (args.out / "report.md").write_text(render(values, result, scenarios), encoding="utf-8")
    (args.out / "levers.json").write_text(json.dumps(scenarios, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
