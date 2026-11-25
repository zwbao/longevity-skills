#!/usr/bin/env python3
"""Habitual CKB diet score and published mortality associations; stdlib only."""
import argparse
import copy
import csv
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, DERIVATION_AGES, FOODS, FREQUENCY_UNIT,
                     HAZARD_RATIOS, LOW_RISK_MIN, OUTCOMES, POPULATIONS, TABLES)

TITLE = "CKB 饮食评分报告"


def lookup(score, sex="pooled"):
    if score not in range(6) or sex not in TABLES:
        raise ValueError("无效饮食得分或人群")
    return HAZARD_RATIOS[sex][max(0, int(score) - 1)]


def calculate(values, sex="pooled"):
    points = {}
    for key, _label, low, high in FOODS:
        value = values[key]
        if not 0 <= value <= 7:
            raise ValueError("食用天数必须在 0–7 内")
        points[key.removesuffix("_days_per_week") + "_points"] = int(low <= value <= high)
    score = sum(points.values())
    result = dict(points, diet_score=score, diet_category="0-1" if score <= 1 else str(score),
                  low_risk_diet=int(score >= LOW_RISK_MIN),
                  reference_population=POPULATIONS[sex], source_table=TABLES[sex])
    for (outcome, _label), (hr, lower, upper) in zip(OUTCOMES, lookup(score, sex)):
        result.update({outcome + "_hr": hr, outcome + "_ci_lower": lower,
                       outcome + "_ci_upper": upper})
    return result


def delta(after, before):
    keys = ["diet_score", *[x + "_hr" for x, _ in OUTCOMES]]
    return {key: after[key] - before[key] for key in keys}


def levers(values, targets, sex):
    current = calculate(values, sex)
    result = {"schema": "longevity-levers/1", "model": "ckb_diet_score",
              "model_zh": "CKB 饮食得分与分档人群 HR", "current": current,
              "sensitivity": [], "levers": [],
              "note_zh": "分档评分没有连续导数。敏感度为每项单独增减一天（限每周 0–7 天）后的有限差值；HR 差只是表格关联的变化，不是个人风险变化或饮食建议。目标值由用户提供，不自动优化。"}
    for key, label, _low, _high in FOODS:
        entry = {"key": key, "label_zh": label, "unit": FREQUENCY_UNIT, "value": values[key],
                 "scenarios": []}
        for direction in (-1, 1):
            moved_value = min(7, max(0, values[key] + direction))
            if moved_value == values[key]:
                continue
            after = calculate(dict(values, **{key: moved_value}), sex)
            entry["scenarios"].append({"to": moved_value, "step_days": moved_value - values[key],
                                       "outputs": after, "delta": delta(after, current)})
        result["sensitivity"].append(entry)
        if key in targets:
            after = calculate(dict(values, **{key: targets[key]}), sex)
            result["levers"].append({"key": key, "label_zh": label, "unit": FREQUENCY_UNIT,
                                     "from": values[key], "to": targets[key], "outputs": after,
                                     "delta": delta(after, current)})
    if targets:
        after = calculate(dict(values, **targets), sex)
        result["targets"] = {"values": targets, "outputs": after, "delta": delta(after, current)}
    return result


def collect(path, manifest, partial=False):
    spec = copy.deepcopy(manifest)
    if partial:
        for item in spec["inputs"]:
            item["required"] = False
    try:
        collected = skillkit.collect_file(path, spec)
    except (OSError, ValueError, csv.Error, AttributeError) as exc:
        return {}, [skillkit.Problem("diet", "饮食文件", "file", f"无法读取饮食 CSV：{exc}")]
    problems = list(collected.problems)
    for name in collected.unmatched:
        problems.append(skillkit.Problem(name, name, "unknown", f"未识别饮食项目「{name}」，请使用五项饮食指标的名称。"))
    if partial and not collected.values and not problems:
        problems.append(skillkit.Problem("targets", "目标", "missing", "目标表至少需要一项有效的食用天数。"))
    return collected.values, problems


def render(outputs, values, age, sex, scenarios):
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的饮食得分", "",
             f"总分：**{outputs['diet_score']} / 5**；查表分档：{outputs['diet_category']}。",
             f"是否达到论文的低风险饮食定义：{'是' if outputs['low_risk_diet'] else '否'}。这只是研究标签，不是营养诊断。", "",
             "以下输入应代表过去 12 个月通常每周有多少天食用，而非进食次数或某一周的偶然记录。", "",
             "| 食物 | 通常食用天数/周 | 本项得分 |", "|---|---:|---:|"]
    for key, label, _low, _high in FOODS:
        point_key = key.removesuffix("_days_per_week") + "_points"
        lines.append(f"| {label} | {values[key]:g} | {outputs[point_key]} |")
    lines += ["", "## 对应分组的人群关联", "",
              f"来源：{TABLES[sex]}，{POPULATIONS[sex]}；参照组为同一张表中饮食得分 0–1 分的人。",
              "HR 是随访中的相对危险率；95% 置信区间反映该人群估计的不确定性，不是你的个人预测区间。",
              "这是 Cox 模型的 HR，不是补充表 S7 的竞争风险模型结果。", "",
              "| 结局 | 调整后 HR | 95% 置信区间 |", "|---|---:|---|"]
    for key, label in OUTCOMES:
        lower, upper = outputs[key + "_ci_lower"], outputs[key + "_ci_upper"]
        interval = "参照组，未报告区间" if lower is None else f"{lower:.2f}–{upper:.2f}"
        lines.append(f"| {label} | {outputs[key + '_hr']:.2f} | {interval} |")
    lines += ["", "适用背景：中国成人前瞻性队列，入组年龄 30–79 岁，主分析排除基线冠心病、脑卒中和癌症。这里未核实你的这些病史；有相关病史时，表中关联不代表该疾病人群。"]
    if age is None:
        lines += ["未提供年龄，尚未核对研究年龄范围。"]
    elif not DERIVATION_AGES[0] <= age <= DERIVATION_AGES[1]:
        lines += [f"你的年龄 {age:g} 岁超出研究入组范围，得分仅作规则演示，不能据此推断该年龄人群的死亡关联。"]
    else:
        lines += [f"提供年龄：{age:g} 岁；年龄不参与饮食加分，也不改变这张表的 HR。"]
    lines += ["饮食分数不包含份量、能量和完整营养结构。红肉项在这套研究规则中两端均不得分，不能据此要求素食者开始吃肉。"]
    if "targets" in scenarios:
        after = scenarios["targets"]["outputs"]
        lines += ["", "## 你提供的目标情景", "",
                  f"全部目标同时达到时，规则得分为 {after['diet_score']} / 5，分档为 {after['diet_category']}；对应表格的全因死亡 HR 为 {after['all_cause_hr']:.2f}。",
                  "每个目标单独达成时的得分和查表变化见 levers.json。这里仅比较同一研究规则下的情景，不估计因果收益或增加的寿命。"]
    lines += ["", f"边界：{BOUNDARY}", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--diet", type=Path, help="marker,value,unit CSV")
    parser.add_argument("--targets", type=Path, help="同列的部分目标 CSV")
    parser.add_argument("--age", help="实足年龄，仅核对研究范围")
    parser.add_argument("--sex", default="pooled", help="male / female / pooled（默认合并表）")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "levers.json", "problems.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.diet, manifest)
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, partial=True)
        for problem in target_problems:
            problem.message_zh = "目标表：" + problem.message_zh
        problems += target_problems
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems += skillkit.check_scalar(manifest, "age", age)
        except ValueError:
            problems.append(skillkit.Problem("age", "年龄", "parse", "年龄必须是有限数值，单位为岁。"))
    if args.sex not in TABLES:
        problems.append(skillkit.Problem("sex", "性别分层", "category", "性别分层只接受 male、female 或 pooled。"))
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        text = report.read_text(encoding="utf-8")
        title, body = text.split("\n", 1)
        report.write_text(title + "\n\n" + "\n".join(paper_card_lines()) + "\n" + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    outputs = calculate(values, args.sex)
    scenarios = levers(values, targets, args.sex)
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / "levers.json").write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.out / "report.md").write_text(render(outputs, values, age, args.sex, scenarios), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
