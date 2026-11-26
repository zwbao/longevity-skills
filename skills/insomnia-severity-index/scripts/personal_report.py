"""Offline scoring of seven completed ISI self-report items."""

import argparse
import csv
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BANDS, BOUNDARY, CATEGORY_ZH, ITEM_COUNT, ITEM_LABELS, STUDY_AGES, TOTAL_MAX

TITLE = "ISI 失眠严重程度指数"


def sum_scores(scores):
    """Same additive rule for individual responses and the printed mean check."""
    scores = list(scores)
    if len(scores) != ITEM_COUNT:
        raise ValueError("必须提供完整七项，缺项不能补零。")
    return math.fsum(scores)


def classify(total):
    if not math.isfinite(total) or int(total) != total:
        raise ValueError("个人总分必须是整数。")
    for low, high, code, _ in BANDS:
        if low <= total <= high:
            return code
    raise ValueError("总分超出图1范围。")


def calculate(values):
    total = int(sum_scores(values[k] for k in ITEM_LABELS))
    return {"isi_total_score": total, "isi_category": classify(total)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="七项已完成的自评得分 CSV")
    parser.add_argument("--age", help="可选年龄，岁；只作适用范围提示")
    parser.add_argument("--sex", help="可选男/女/其他/未知或 male/female/other/unknown")
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
            "measurements", "自评分表", "file", f"请提供可读取的 marker,value,unit CSV：{exc}")])
    problems = list(collected.problems)
    for key in ITEM_LABELS:
        if key in collected.values and not collected.values[key].is_integer():
            problems.append(skillkit.Problem(key, ITEM_LABELS[key], "integer",
                                            f"{ITEM_LABELS[key]}必须是0至4的整数得分，不能填群体均分。"))
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, "age", age))
        except ValueError:
            problems.append(skillkit.Problem("age", "年龄", "parse", "年龄必须是有限数值，单位为岁。"))
    if args.sex is not None and args.sex.casefold() not in {
        "male", "female", "other", "unknown", "男", "女", "其他", "未知"
    }:
        problems.append(skillkit.Problem("sex", "性别", "category", "性别请填男、女、其他、未知或对应英文，也可不提供。"))
    heading = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = report.read_text(encoding="utf-8").split("\n", 2)[2]
        report.write_text("\n".join(heading) + "\n" + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    outputs = calculate(collected.values)
    skillkit.write_result(args.out, manifest, outputs)
    report = heading + [
        "## 你的结果", "",
        f"过去两周 ISI 总分：**{outputs['isi_total_score']} / {TOTAL_MAX}**。",
        f"按论文图1归入：**{CATEGORY_ZH[outputs['isi_category']]}**。", "",
        "| 自评项目 | 得分 |", "| --- | --- |",
        *[f"| {label} | {int(collected.values[key])} |" for key, label in ITEM_LABELS.items()],
        "", "七项直接相加，分数越高表示自觉失眠困扰越重。睡眠满意度项中，完全满意为0分，完全不满意为4分。", "",
        "低分不能排除其他睡眠问题；中度、重度是问卷分档名称，不表示已经确诊。",
        "本研究来自失眠临床人群，未建立普通人群或中文译本的独立诊断准确性。",
        "复测时应使用同一自评版本和过去两周的时间窗；本报告不判定治疗是否有效。",
    ]
    if age is not None and not any(lo <= age <= hi for lo, hi in STUDY_AGES):
        report += ["", "你的年龄超出本文两个样本的观察年龄范围，分数仍按同一规则相加，适用性证据有限。"]
    report += ["", f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
