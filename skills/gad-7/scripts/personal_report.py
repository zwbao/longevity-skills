"""Offline, manifest-validated GAD-7 symptom scoring."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, ITEMS, RESPONSE_ZH, SCREENING_CUTOFF,
                     SEVERITY_BANDS, SEVERITY_ZH, STUDY_AGE_RANGE, TOTAL_RANGE)

TITLE = "GAD-7 焦虑症状评分"


def classify(total):
    for low, high, category in SEVERITY_BANDS:
        if low <= total <= high:
            return category
    raise ValueError("总分超出量表范围")


def calculate(values):
    scores = {}
    for key in ITEMS:
        value = values[key]
        if value not in RESPONSE_ZH:
            raise ValueError("每题必须是规定的整数分值")
        scores[key] = int(value)
    total = sum(scores.values())
    return {**scores, "gad7_total_score": total, "anxiety_severity": classify(total),
            "screening_threshold_status": "at_or_above_cutoff" if total >= SCREENING_CUTOFF else "below_cutoff"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="可选实足年龄（岁），只提示研究适用范围")
    parser.add_argument("--sex", help="可选 male/female/other/unknown 或 男/女/其他/未知")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ("result.json", "problems.json"):
        (args.out / filename).unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError, csv.Error, AttributeError) as exc:
        collected = skillkit.Collected(problems=[skillkit.Problem(
            "measurements", "回答表", "file", f"回答表无法读取，请提供 marker,value,unit 格式的 CSV：{exc}")])
    problems = list(collected.problems)
    for key in ITEMS:
        if key in collected.values and collected.values[key] not in RESPONSE_ZH:
            problems.append(skillkit.Problem(key, ITEMS[key], "integer",
                                             f"{ITEMS[key]}：必须按频度选择一个整数分值，不能填小数或平均分。"))
    age = None
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
        "## 你的结果", "", "以下结果对应过去两周的本人回答。", "",
        f"GAD-7 总分：**{outputs['gad7_total_score']} / {TOTAL_RANGE[1]}**；"
        f"焦虑症状程度：**{SEVERITY_ZH[outputs['anxiety_severity']]}**。", "",
        "| 项目 | 你的回答 | 得分 |", "| --- | --- | --- |",
        *[f"| {label} | {RESPONSE_ZH[outputs[key]]} | {outputs[key]} |" for key, label in ITEMS.items()], "",
    ]
    if outputs["gad7_total_score"] >= SCREENING_CUTOFF:
        report += [f"已达到原文进一步评估切点（≥{SCREENING_CUTOFF} 分），可带着回答与专业人员讨论；筛查结果不是确诊。"]
    else:
        report += [f"未达到原文进一步评估切点（≥{SCREENING_CUTOFF} 分），但低分不能排除焦虑障碍或其他心理困扰。"]
    report += ["", "若症状影响工作、家务或人际相处，可一并说明；原量表的功能困难附加题不计入总分。",
               "", "本研究为横断面验证，未建立治疗收益、症状改善目标或个人患病概率模型。",
               "", "中文题干为原文的解释性翻译，不声称是经中文人群验证的正式译本。"]
    if age is not None and not STUDY_AGE_RANGE[0] <= age <= STUDY_AGE_RANGE[1]:
        report += ["", f"你提供的年龄不在本研究 {STUDY_AGE_RANGE[0]}–{STUDY_AGE_RANGE[1]} 岁范围内；分数仍按原规则计算，适用性证据有限。"]
    report += ["", f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
