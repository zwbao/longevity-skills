#!/usr/bin/env python3
"""MEDAS 2011 Table 2: fourteen binary items and an unweighted total."""

import argparse
import csv
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import AGE_RANGE, BOUNDARY, ITEMS, TITLE, TOTAL_RANGE


def score_item(key, value):
    rule = ITEMS[key]
    if rule["op"] == "eq":
        return int(value == rule["cutoff"])
    if rule["op"] == "ge":
        return int(value >= rule["cutoff"])
    return int(value < rule["cutoff"])


def score(values):
    points = {f"item_{n:02d}_score": score_item(key, values[key])
              for n, key in enumerate(ITEMS, 1)}
    return {"medas_total": sum(points.values()), **points}


def criterion(key):
    item = ITEMS[key]
    if item["op"] == "eq":
        return "回答是"
    op = {"ge": "≥", "lt": "<"}[item["op"]]
    return f"{op}{item['cutoff']:g} {item['display_unit']}"


def collect(path, manifest, partial=False):
    if partial:
        manifest = {**manifest, "inputs": [{**s, "required": False} for s in manifest["inputs"]]}
    try:
        got = skillkit.collect_file(path, manifest)
    except (OSError, UnicodeError, csv.Error, AttributeError) as e:
        return {}, [skillkit.Problem("measurements", "问卷文件", "file", f"无法读取问卷表：{e}")]
    problems = list(got.problems)
    for name in got.unmatched:
        problems.append(skillkit.Problem(name, name, "unknown", f"不认识问卷项目「{name}」，请使用说明中的项目名。"))
    for key, value in got.values.items():
        if ITEMS[key]["op"] == "eq" and value not in (0, 1):
            problems.append(skillkit.Problem(key, ITEMS[key]["label_zh"], "category", "是/否题只能填 1 或 0，不能填小数。"))
    if partial and not got.values and not problems:
        problems.append(skillkit.Problem("targets", "目标问卷", "missing", "目标表至少需要一项有效数值。"))
    return got.values, problems


def levers(values, targets):
    current = score(values)["medas_total"]
    sensitivity = []
    for key, item in ITEMS.items():
        point = score_item(key, values[key])
        sensitivity.append({
            "key": key, "label_zh": item["label_zh"], "unit": item["unit"],
            "display_unit": item["display_unit"], "value": values[key],
            "item_score": point, "criterion": criterion(key),
            "delta_if_criterion_met": 1 - point,
            "delta_if_criterion_not_met": 0 - point,
        })
    out = {
        "schema": "longevity-levers/1", "model": "medas_2011",
        "model_zh": "MEDAS 饮食依从性评分（2011）",
        "current": {"medas_total": current}, "sensitivity": sensitivity, "levers": [],
        "note_zh": "敏感度是跨越二元计分条件时的离散分数变化，不是连续导数或健康收益预测。仅展示原量表和用户提交的目标，不生成饮食或饮酒目标。酒类分数不代表安全性。",
    }
    for key, target in targets.items():
        changed = dict(values, **{key: target})
        out["levers"].append({
            "key": key, "label_zh": ITEMS[key]["label_zh"], "unit": "1",
            "display_unit": ITEMS[key]["display_unit"], "from": values[key], "to": target,
            "item_score": score_item(key, target),
            "medas_total": score(changed)["medas_total"],
            "medas_total_delta": score(changed)["medas_total"] - current,
        })
    if targets:
        total = score(dict(values, **targets))["medas_total"]
        out["targets"] = {"values": targets, "medas_total": total, "medas_total_delta": total - current}
    return out


def profile_problems(manifest, raw_age, sex):
    age = None
    problems = []
    if raw_age is not None:
        try:
            age = skillkit.parse_number(raw_age)
            problems += skillkit.check_scalar(manifest, "age", age)
        except ValueError:
            problems.append(skillkit.Problem("age", "年龄", "parse", "年龄必须是有限数值（岁）。"))
    if sex is not None and sex not in ("male", "female"):
        problems.append(skillkit.Problem("sex", "性别", "category", "性别参数接受 male 或 female；不参与计分，可省略。"))
    return age, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--age")
    parser.add_argument("--sex")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    # Remove only this program's machine outputs, so a failed rerun cannot
    # leave stale success data for an assistant to mistake for a fresh score.
    for name in ("result.json", "levers.json", "problems.json"):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    age, profile_errors = profile_problems(manifest, args.age, args.sex)
    problems += profile_errors
    targets = {}
    if args.targets is not None:
        targets, target_errors = collect(args.targets, manifest, partial=True)
        problems += [skillkit.Problem(p.key, p.label, p.kind, "目标表：" + p.message_zh) for p in target_errors]
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        text = path.read_text(encoding="utf-8")
        head, rest = text.split("\n", 1)
        path.write_text(head + "\n\n" + "\n".join(paper_card_lines()) + "\n" + rest, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    outputs = score(values)
    changes = levers(values, targets)
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的结果", "",
             f"MEDAS 总分：**{outputs['medas_total']} / {TOTAL_RANGE[1]} 分**。",
             "这是与原问卷饮食模式的符合程度；不另外划分高低风险，也不换算为健康收益。", "",
             "| 项目 | 你的回答 | 原论文得 1 分条件 | 本项得分 |",
             "| --- | --- | --- | --- |"]
    for n, (key, item) in enumerate(ITEMS.items(), 1):
        value_text = ("是" if values[key] == 1 else "否") if item["op"] == "eq" else f"{values[key]:g} {item['display_unit']}"
        lines.append(f"| {n}. {item['label_zh']} | {value_text} | {criterion(key)} | {outputs[f'item_{n:02d}_score']} |")
    lines += ["", "原研究对象为西班牙冠心病高风险中老年人；这套问卷在其他年龄、地区和饮食习惯下的测量表现不能由本研究保证。"]
    if age is not None and not AGE_RANGE[0] <= age <= AGE_RANGE[1]:
        lines.append(f"你的年龄超出本文报告的 {AGE_RANGE[0]}–{AGE_RANGE[1]} 岁研究范围；算术得分可计算，但不代表已在你所属人群验证。")
    lines += ["", "份数与版本：配菜按半份计入蔬菜摄入量；酒和饮料按论文小杯记录。鲜榨果汁没有统一毫升换算，鱼及红肉的份量是区间；本报告按你已确认的问卷份数计算。"]
    if targets:
        lines += ["", "## 你提供的目标对应的分数", "",
                  f"全部目标同时成立时：{changes['targets']['medas_total']} 分；相对当前变化 {changes['targets']['medas_total_delta']:+g} 分。",
                  "以下只改变每行指定的一项，其他回答保持当前值："]
        for change in changes["levers"]:
            lines.append(f"- {change['label_zh']}：{change['from']:g} → {change['to']:g}（{change['display_unit']}）；总分变化 {change['medas_total_delta']:+g} 分。")
        lines.append("目标来自你提交的表格；这些分数差不是该改变的因果效果或安全性判断。")
    lines += ["", f"边界：{BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / "levers.json").write_text(json.dumps(changes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
