"""Offline SARC-F scoring from the original 2013 questionnaire."""

import argparse
import csv
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (ANSWER_LABELS, BOUNDARY, CATEGORY_ZH, DIRECT_SCORE_KEYS,
                     FALLS_HIGH_THRESHOLD, FALLS_POINTS, LABELS, MAX_SCORE,
                     MEASUREMENTS, POSITIVE_CUTOFF)

TITLE = "SARC-F 肌少症风险筛查"


def falls_points(count):
    if count == 0:
        return FALLS_POINTS[0]
    return FALLS_POINTS[2] if count >= FALLS_HIGH_THRESHOLD else FALLS_POINTS[1]


def classify(total):
    return "screen_positive" if total >= POSITIVE_CUTOFF else "below_cutoff"


def calculate(values):
    scores = {key: int(values[key]) for key in DIRECT_SCORE_KEYS}
    scores["falls_score"] = falls_points(values["falls_past_year_count"])
    total = sum(scores.values())
    return {**scores, "sarc_f_total_score": total, "sarc_f_category": classify(total)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="可选实足年龄；不参与计分")
    parser.add_argument("--sex", help="可选性别；不参与计分")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json"):
        (args.out / name).unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError, csv.Error, AttributeError) as exc:
        collected = skillkit.Collected(problems=[skillkit.Problem(
            "measurements", "问卷表", "file", f"无法读取问卷表，请提供 marker,value,unit 格式的 CSV：{exc}"
        )])
    problems = list(collected.problems)
    for key in MEASUREMENTS:
        if key in collected.values and not collected.values[key].is_integer():
            spec = skillkit.spec_by_key(manifest, key)
            problems.append(skillkit.Problem(key, spec["label_zh"], "integer",
                                             f"{spec['label_zh']}必须填写规定范围内的整数。"))
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, "age", age))
        except ValueError:
            problems.append(skillkit.Problem("age", "实足年龄", "parse", "年龄必须是有限数值（岁）。"))
    if args.sex is not None and args.sex.casefold() not in {
        "male", "female", "other", "unknown", "男", "女", "其他", "未知"
    }:
        problems.append(skillkit.Problem("sex", "性别", "category", "性别请填男、女、其他或未知，也可不提供。"))
    heading = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 2)[2]
        path.write_text("\n".join(heading) + "\n" + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    outputs = calculate(collected.values)
    skillkit.write_result(args.out, manifest, outputs)
    rows = [f"| {LABELS[key]} | {ANSWER_LABELS[key][outputs[key]]} | {outputs[key]} |"
            for key in DIRECT_SCORE_KEYS]
    rows.append(f"| {LABELS['falls_score']} | {int(collected.values['falls_past_year_count'])} 次 | {outputs['falls_score']} |")
    report = heading + [
        "## 你的结果", "",
        f"SARC-F 总分：**{outputs['sarc_f_total_score']} / {MAX_SCORE}**。",
        f"筛查分层：**{CATEGORY_ZH[outputs['sarc_f_category']]}**。", "",
        "| 项目 | 你的回答 | 得分 |", "| --- | --- | --- |", *rows, "",
        f"总分达到 {POSITIVE_CUTOFF} 分即达到本文筛查界值。结果是功能困难的筛查信号，不是确诊结论。",
        "中文题意为原文的说明性翻译，未声称完成中文量表的语言学验证；请按日常情况回答，无需为填写问卷尝试可能导致跌倒的动作。",
        "原文面向老年人的肌少症问题，但没有给出初步研究的具体年龄范围、样本量或分性别界值；年龄和性别不改变分数。",
        "", f"边界: {BOUNDARY}", "",
    ]
    (args.out / "report.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
