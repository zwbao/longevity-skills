"""Offline AAH/BLSA SARC-F scoring; validated through the local manifest."""

import argparse
import csv
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, CATEGORY_ZH, COMPONENTS, FALLS_HIGH_THRESHOLD,
                     MAX_SCORE, MEASUREMENTS, NO_POINTS, POSITIVE_THRESHOLD,
                     SEVERE_POINTS, SOME_POINTS)

TITLE = "SARC-F 肌少症相关功能风险筛查"


def falls_points(count):
    if count >= FALLS_HIGH_THRESHOLD:
        return SEVERE_POINTS
    return SOME_POINTS if count > 0 else NO_POINTS


def classify(total):
    return "screen_positive" if total >= POSITIVE_THRESHOLD else "screen_negative"


def calculate(values):
    scores = {f"{item}_score": int(values[f"{item}_response_score"])
              for item in COMPONENTS if item != "falls"}
    scores["falls_score"] = falls_points(values["falls_past_year_count"])
    total = sum(scores.values())
    return {**scores, "sarc_f_total_score": total, "sarc_f_category": classify(total)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="可选年龄（岁），不改变分数")
    parser.add_argument("--sex", help="可选男/女/其他/未知或male/female/other/unknown，不改变分数")
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
            "measurements", "问卷表", "file", f"问卷表无法读取，请提供 marker,value,unit 格式的 CSV：{exc}")])
    problems = list(collected.problems)
    for key in MEASUREMENTS:
        spec = skillkit.spec_by_key(manifest, key)
        if key in collected.values and not collected.values[key].is_integer():
            problems.append(skillkit.Problem(key, spec["label_zh"], "integer",
                            f"{spec['label_zh']}必须填写整数。{spec['note_zh']}"))
        elif any(p.key == key and p.kind == "missing" for p in problems):
            problems = [skillkit.Problem(p.key, p.label, p.kind,
                        p.message_zh + spec["note_zh"]) if p.key == key and p.kind == "missing" else p
                        for p in problems]
    if args.age is not None:
        try:
            problems.extend(skillkit.check_scalar(manifest, "age", skillkit.parse_number(args.age)))
        except ValueError:
            problems.append(skillkit.Problem("age", "年龄", "parse", "年龄须为有限数值（岁）。"))
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
        f"SARC-F 总分：**{outputs['sarc_f_total_score']} / {MAX_SCORE}**；"
        f"**{CATEGORY_ZH[outputs['sarc_f_category']]}**。", "",
        "| 项目 | 得分 |", "| --- | --- |",
        *[f"| {label} | {outputs[item + '_score']} |" for item, label in COMPONENTS.items()], "",
        f"过去一年报告跌倒 {int(collected.values['falls_past_year_count'])} 次。",
        f"总分 ≥{POSITIVE_THRESHOLD} 为筛查阳性；未达到切点也不能排除肌少症。",
        "筛查阳性可将结果交给医生，结合实际肌力、体能和肌肉量等进一步评估。", "",
        "采用本文 AAH/BLSA 题干及跌倒次数规则。中文题干为解释性翻译，未经本研究中文量表验证。",
        "研究来自美国社区中晚年及老年人群；AAH 入组时为中晚年非裔成年人，BLSA 为入组健康的志愿者。",
        "年龄与性别不改变问卷得分；其他人群的适用性需另行评估。", "",
        f"边界: {BOUNDARY}", "",
    ]
    (args.out / "report.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
