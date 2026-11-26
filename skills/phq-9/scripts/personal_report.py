"""Offline PHQ-9 severity scoring; no diagnosis or medication decision."""

import argparse
import csv
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, CATEGORY_ZH, ITEM_KEYS, ITEM_LABELS, MAX_SCORE,
                     RESPONSE_ZH, SEVERITY_BANDS, SUPPORT_LINES)

TITLE = "PHQ-9 抑郁症状严重度"


def classify(total):
    for low, high, category, _ in SEVERITY_BANDS:
        if low <= total <= high:
            return category
    raise ValueError("PHQ-9 总分超出范围")


def calculate(values):
    total = sum(int(values[key]) for key in ITEM_KEYS)
    return {"phq9_total_score": total, "phq9_severity": classify(total),
            "item9_followup_needed": int(values[ITEM_KEYS[-1]] > 0)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="可选年龄（岁）；仅限成人，不参与计分")
    parser.add_argument("--sex", help="可选 male/female/other/unknown 或 男/女/其他/未知")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError, csv.Error, AttributeError) as exc:
        collected = skillkit.Collected(problems=[skillkit.Problem(
            "measurements", "问卷回答表", "file",
            f"无法读取问卷回答表，请提供 marker,value,unit 格式的 CSV：{exc}")])
    problems = list(collected.problems)
    for key in ITEM_KEYS:
        if key in collected.values and not collected.values[key].is_integer():
            spec = skillkit.spec_by_key(manifest, key)
            problems.append(skillkit.Problem(key, spec["label_zh"], "integer",
                                             f"{spec['label_zh']}必须填写整数选项得分。"))
    if args.age is not None:
        try:
            problems.extend(skillkit.check_scalar(manifest, "age", skillkit.parse_number(args.age)))
        except ValueError:
            problems.append(skillkit.Problem("age", "年龄", "parse", "年龄必须是有限数值（岁）。"))
    if args.sex is not None and args.sex.casefold() not in {
        "male", "female", "other", "unknown", "男", "女", "其他", "未知"
    }:
        problems.append(skillkit.Problem("sex", "性别", "category", "性别请填男、女、其他或未知，也可不填。"))

    heading = [f"# {TITLE}", "", *paper_card_lines(), ""]
    q9 = collected.values.get(ITEM_KEYS[-1])
    if q9 in (1, 2, 3):
        heading += SUPPORT_LINES
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 2)[2]
        path.write_text("\n".join(heading) + "\n" + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    outputs = calculate(collected.values)
    skillkit.write_result(args.out, manifest, outputs)
    report = heading + [
        "## 你的结果", "",
        f"过去两周 PHQ-9 总分：**{outputs['phq9_total_score']} / {MAX_SCORE}**。",
        f"抑郁症状严重度分档：**{CATEGORY_ZH[outputs['phq9_severity']]}**。", "",
        "分档描述症状负担；分数低也不能排除抑郁症或安全问题。", "",
        "| 题目 | 回答 | 得分 |", "| --- | --- | --- |",
        *[f"| {i}. {label} | {RESPONSE_ZH[int(collected.values[key])]} | {int(collected.values[key])} |"
          for i, (key, label) in enumerate(zip(ITEM_KEYS, ITEM_LABELS), 1)], "",
        "以上得分须来自同一次、针对过去两周的完整 PHQ-9 回答。"
        "附加的生活困难问题不计入总分；工作、家庭或人际功能受影响的情况可另向专业人员说明。",
        "如果症状持续、加重或影响生活，可以携带回答记录寻求专业评估。"
        "年龄和性别不改变分数。本研究没有验证中文译文或未成年人应用。", "",
        f"边界: {BOUNDARY}", "",
    ]
    (args.out / "report.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
