"""Offline scoring of complete, unrecoded UCLA Loneliness Scale V3 responses."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, ITEM_NUMBERS, LANGUAGE_NOTE, MEASUREMENTS,
                     RESPONSE_LABELS, REVERSE_ITEMS, REVERSE_POINTS, TOTAL_RANGE)

TITLE = "UCLA 第三版孤独感量表"


def item_points(item, response):
    if item not in ITEM_NUMBERS or response not in RESPONSE_LABELS:
        raise ValueError("需要第三版的题号及规定的原始回答编码")
    return REVERSE_POINTS[response] if item in REVERSE_ITEMS else int(response)


def calculate(values):
    scores = {f"item_{i:02d}_score": item_points(
        i, values[f"ucla_v3_item_{i:02d}_response_score"])
        for i in ITEM_NUMBERS}
    return {**scores, "ucla_v3_total_score": sum(scores.values())}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="第三版原始回答 CSV：marker,value,unit")
    parser.add_argument("--age", help="可选实足年龄（岁），不参与计分")
    parser.add_argument("--sex", help="可选性别，不参与计分")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError, csv.Error, AttributeError, TypeError) as exc:
        collected = skillkit.Collected(problems=[skillkit.Problem(
            "measurements", "回答表", "file",
            f"回答表无法读取，请提供 marker,value,unit 格式的 CSV：{exc}")])
    problems = list(collected.problems)
    for key in MEASUREMENTS:
        if key in collected.values and not collected.values[key].is_integer():
            spec = skillkit.spec_by_key(manifest, key)
            problems.append(skillkit.Problem(key, spec["label_zh"], "integer",
                                             "回答必须为 1、2、3、4 中的整数；不要输入平均值或已反向计分的值。"))
    for name in collected.unmatched:
        problems.append(skillkit.Problem(name, name, "unknown",
                                         "无法识别题号，请使用第三版回答模板中的题号；本表不接收其他版本或额外指标。"))
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
    report = heading + [
        "## 你的结果", "",
        f"孤独感总分：**{outputs['ucla_v3_total_score']} 分**。",
        f"理论范围为 {TOTAL_RANGE[0]}–{TOTAL_RANGE[1]} 分，由各题得分相加得到；分数越高表示自报孤独感越强。",
        "论文没有给出个人诊断阈值，因此此处不划分轻、中、重度，也不计算百分位。", "",
        "| 题号 | 原始回答 | 计分方向 | 得分 |", "| --- | --- | --- | --- |",
    ]
    for i in ITEM_NUMBERS:
        response = int(collected.values[f"ucla_v3_item_{i:02d}_response_score"])
        direction = "反向" if i in REVERSE_ITEMS else "原值"
        report.append(f"| {i} | {response} · {RESPONSE_LABELS[response]} | {direction} | {outputs[f'item_{i:02d}_score']} |")
    report += [
        "", "填写依据：第三版完整问卷的原始回答；缺题不能按从不处理，也不能用总分或短版答案补齐。",
        "原文没有限定过去几天或几周，本工具不添加回顾时间窗。年龄与性别不改变计分。",
        "", LANGUAGE_NOTE,
        "本研究包括大学生、护士、教师和老年人；教师使用短版，其统计量不用于解释这里的完整量表分数。",
        "", f"边界: {BOUNDARY}", "",
    ]
    (args.out / "report.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
