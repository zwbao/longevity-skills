"""Score eight completed ESS items using Johns 1991, entirely offline."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BOUNDARY, ITEM_KEYS, ITEM_LABELS, ITEM_RANGE, MAX_TOTAL,
    PATIENT_AGE_RANGE, RESPONSE_LABELS,
)

TITLE = "Epworth 日间嗜睡量表（ESS）计分"


def calculate(values):
    """All eight responses are required; every response contributes unchanged."""
    scores = {}
    for key in ITEM_KEYS:
        value = values[key]
        if value not in RESPONSE_LABELS:
            raise ValueError(f"{key}: expected an integer in {ITEM_RANGE}")
        scores[key] = int(value)
    return {**scores, "ess_total_score": sum(scores.values())}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="可选实足年龄（岁），仅用于适用人群提示")
    parser.add_argument("--sex", help="可选男/女/其他/未知或male/female/other/unknown，不进入计分")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json"):
        (args.out / name).unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError, csv.Error, AttributeError, TypeError) as exc:
        collected = skillkit.Collected(problems=[skillkit.Problem(
            "measurements", "ESS单项分数表", "file",
            f"无法读取表格，请提供 marker,value,unit 格式的 CSV：{exc}",
        )])
    problems = list(collected.problems)
    for key in ITEM_KEYS:
        if key in collected.values and not collected.values[key].is_integer():
            spec = skillkit.spec_by_key(manifest, key)
            problems.append(skillkit.Problem(key, spec["label_zh"], "integer",
                "本技能按1991年表1接收整数单项分数；请确认原作答，不四舍五入或补值。"))
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, "age", age))
        except ValueError:
            problems.append(skillkit.Problem("age", "实足年龄", "parse", "年龄须为有限数值（岁）。"))
    if args.sex is not None and args.sex.casefold() not in {
        "male", "female", "other", "unknown", "男", "女", "其他", "未知",
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
        f"ESS 总分：**{outputs['ess_total_score']} / {MAX_TOTAL} 分**。", "",
        "分数越高，表示在这组日常情境中自报的入睡倾向越强；分数低也不能排除睡眠疾病。", "",
        "| 已完成问卷的条目 | 单项分数 | 回答含义 |", "| --- | --- | --- |",
        *[f"| {label} | {outputs[key]} | {RESPONSE_LABELS[outputs[key]]} |"
          for key, label in zip(ITEM_KEYS, ITEM_LABELS)], "",
        "这里的条目简称仅用于核对已完成问卷的分数，不是经过验证的中文版问卷。", "",
        "评分针对近期通常生活中的打瞌睡或睡着的可能性，不是仅仅疲劳、每日睡眠时长或此刻困倦。"
        "未经历某情境时应由本人参照原问卷估计，程序不会将未作答记为零。", "",
        "原研究为成人量表开发与验证，患者来自澳大利亚单一睡眠专科；"
        "本报告只相加单项分数，不将研究组间差异换成个人疾病概率或轻中重诊断分档。",
    ]
    if age is not None and age > PATIENT_AGE_RANGE[1]:
        report += ["", f"你提供的年龄超出原文患者年龄范围 {PATIENT_AGE_RANGE[0]}–{PATIENT_AGE_RANGE[1]} 岁；"
                   "对照组未单列年龄范围，本分数在你所在年龄人群中的解释需另行评估。"]
    report += ["", f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
