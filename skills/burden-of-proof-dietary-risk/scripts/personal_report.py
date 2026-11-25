"""Offline, exact-point readout of the published Burden of Proof dietary tables."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, GRIDS, INPUT_LABELS, INPUT_UNITS, LEVER_NOTE,
                     PAIRS, TABLE_ROWS, TABLES, TITLE)


def lookup(pair, intake):
    if intake == 0:
        return (1.0, None, None)
    return TABLES[pair].get(intake)


def outputs(values):
    result = {}
    for pair, (key, *_) in PAIRS.items():
        row = lookup(pair, values[key]) if key in values else None
        for suffix, value in zip(("rr", "ui_lower", "ui_upper"), row or (None, None, None)):
            result[f"{pair}_{suffix}"] = value
    return result


def collect(path, manifest):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError) as exc:
        return {}, [skillkit.Problem("measurements", "摄入量文件", "format", f"无法读取摄入量文件：{exc}")]
    problems = list(collected.problems)
    for name in collected.unmatched:
        problems.append(skillkit.Problem(name, name, "unknown", f"无法识别项目“{name}”，请使用清单中的摄入量名称。"))
    if not collected.values and not problems:
        problems.append(skillkit.Problem("intake", "摄入量", "missing", "请提供至少一项真实的日常摄入量；缺项不能按零处理。"))
    for key, value in collected.values.items():
        if value not in GRIDS[key]:
            points = "、".join(f"{x:g}" for x in GRIDS[key])
            problems.append(skillkit.Problem(key, INPUT_LABELS[key], "unsupported", f"{INPUT_LABELS[key]} {value:g} {INPUT_UNITS[key]} 没有已发表的表格点。本工具支持 {points} {INPUT_UNITS[key]}；这不是测量错误，请保留原值，不要为了运行而四舍五入或修改饮食。"))
    return collected.values, problems


def delta(before, after):
    return {key: after[key] - value if value is not None and after[key] is not None else None
            for key, value in before.items() if key.endswith("_rr")}


def levers(values, targets):
    current = outputs(values)
    sensitivity = []
    for key, x in values.items():
        adjacent = []
        for pair, details in PAIRS.items():
            if details[0] != key or lookup(pair, x) is None:
                continue
            grid = sorted({0.0} | set(TABLES[pair]))
            i = grid.index(x)
            for j in (i - 1, i + 1):
                if 0 <= j < len(grid):
                    y = grid[j]
                    a, b = lookup(pair, x)[0], lookup(pair, y)[0]
                    adjacent.append({"output": f"{pair}_rr", "from": x, "to": y,
                                     "rr_from": a, "rr_to": b, "rr_delta": b - a,
                                     "rr_per_unit_secant": (b - a) / (y - x)})
        sensitivity.append({"key": key, "label_zh": INPUT_LABELS[key], "unit": INPUT_UNITS[key],
                            "value": x, "derivative": None, "adjacent_table_comparisons": adjacent})
    result = {"schema": "longevity-levers/1", "model": "burden-of-proof-dietary-risk",
              "model_zh": TITLE, "current": current, "sensitivity": sensitivity,
              "levers": [], "note_zh": LEVER_NOTE}
    for key, target in targets.items():
        moved = outputs(dict(values, **{key: target}))
        result["levers"].append({"key": key, "label_zh": INPUT_LABELS[key], "unit": INPUT_UNITS[key],
                                 "from": values[key], "to": target, "outputs": moved,
                                 "delta": delta(current, moved)})
    if targets:
        moved = outputs(dict(values, **targets))
        result["targets"] = {"values": targets, "outputs": moved, "delta": delta(current, moved)}
    return result


def result_lines(values, heading):
    lines = [f"## {heading}", "", "| 食物与结局 | 摄入量 | 相对风险 RR | 95% 不确定区间 | 出处 |", "|---|---:|---:|---|---|"]
    for pair, (key, label, table, stars, dense) in PAIRS.items():
        if key not in values:
            continue
        x = values[key]
        row = lookup(pair, x)
        if row is None:
            rr, ui, source = "未计算", "该摄入量未列出此结局", f"附表 {table}"
        else:
            rr = f"{row[0]:.2f}"
            ui = "参照定义，不另估计区间" if x == 0 else f"{row[1]:.2f}–{row[2]:.2f}"
            source = "零摄入参照" if x == 0 else f"附表 {table}"
        lines.append(f"| {label} | {x:g} {INPUT_UNITS[key]} | {rr} | {ui} | {source} |")
    lines += ["", "RR 以同类食物零摄入为参照，1 表示参照水平；不是发病百分比。区间包含研究间异质性。"]
    for pair, (key, label, table, stars, dense) in PAIRS.items():
        if key in values and dense and values[key] > dense[1]:
            lines += [f"{label}：你的输入超过论文概括证据时使用的摄入量密集区间上端（{dense[1]:g} {INPUT_UNITS[key]}）。有表格读数不代表这一水平证据充分。"]
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--age", help="实足年龄（岁），只核对成人适用范围，不进入风险计算")
    parser.add_argument("--sex", help="可选上下文；论文读数不按性别调整")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json", "levers.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    try:
        problems += skillkit.check_scalar(manifest, "age", args.age)
    except (ValueError, TypeError):
        problems.append(skillkit.Problem("age", "实足年龄", "parse", "实足年龄必须是以岁为单位的数值。"))
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest)
        for p in target_problems:
            p.message_zh = "目标文件：" + p.message_zh
        problems += target_problems
        for key in targets.keys() - values.keys():
            problems.append(skillkit.Problem(key, INPUT_LABELS[key], "missing", f"目标文件包含{INPUT_LABELS[key]}，但缺少该项当前摄入量，无法比较。"))
    header = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join(header) + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    current = outputs(values)
    skillkit.write_result(args.out, manifest, current)
    lever = levers(values, targets)
    (args.out / "levers.json").write_text(json.dumps(lever, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = header + result_lines(values, "你的摄入量对应的表格读数")
    missing = [INPUT_LABELS[key] for key in INPUT_UNITS if key not in values]
    if missing:
        lines += ["", "未提供：" + "、".join(missing) + "；未计算相关读数，也未按零摄入处理。"]
    lines += ["", "论文中加工肉与缺血性心脏病为一星关联，其余五项为二星关联；反映证据较弱或研究间不一致，不是你的风险等级。", "年龄仅用于确认成人适用范围；这些读数没有按年龄、性别或地区个体化。"]
    if targets:
        lines += ["", *result_lines(dict(values, **targets), "用户给定目标对应的表格读数"), "", LEVER_NOTE]
        for item in lever["levers"]:
            for pair, details in PAIRS.items():
                key = f"{pair}_rr"
                if details[0] == item["key"]:
                    change = item["delta"][key]
                    text = "缺少对应表格点，未计算差值" if change is None else f"RR 差 {change:+.2f}"
                    lines.append(f"{details[1]}：仅把该项从 {item['from']:g} 改为 {item['to']:g} {item['unit']}，{text}。")
    lines += ["", "这些摄入量点是论文的报告位置，不是推荐摄入量。保留真实记录，不用较接近的表格点替代实际摄入量。", "", f"边界：{BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
