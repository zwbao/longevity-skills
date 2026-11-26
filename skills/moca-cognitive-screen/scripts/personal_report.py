#!/usr/bin/env python3
"""Audit scored original full MoCA tasks, without administering the test."""
import argparse
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, MAX_TOTAL, NORMAL_CUTOFF, TASK_MAXIMA, score

TITLE = "MoCA 认知筛查计分核对"


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path,
                        help="原版完整 MoCA 已评分任务及教育年限，CSV item,value,unit")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    manifest = skillkit.load_manifest(__file__)
    for filename in ("problems.json", "result.json", "report.md"):
        (out / filename).unlink(missing_ok=True)
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
    except (OSError, ValueError, UnicodeError) as exc:
        collected = skillkit.Collected(problems=[skillkit.Problem(
            "measurements", "测评记录", "file", f"无法读取测评文件：{exc}")])
    problems = list(collected.problems)
    labels = {item["key"]: item["label_zh"] for item in manifest["inputs"]}
    for key, value in collected.values.items():
        if key in TASK_MAXIMA and not float(value).is_integer():
            problems.append(skillkit.Problem(key, labels[key], "integer",
                                            "任务得分必须为整数；请提供施测人员确认的得分。"))
    for name in collected.unmatched:
        problems.append(skillkit.Problem("measurements", "测评记录", "unknown",
                                        f"无法识别项目“{name}”。请提供规定的任务得分和教育年限；总分不能替代缺失任务。"))
    if problems:
        path = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        rows = path.read_text(encoding="utf-8").splitlines()
        path.write_text("\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n",
                        encoding="utf-8")
        skillkit.write_result(out, manifest, {item["key"]: None for item in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    result = score(collected.values)
    interpretation = (
        "得分低于原文切点，可把本次测评记录交给临床人员结合症状、日常功能及施测情况进一步评估。"
        if result["adjusted_score"] < NORMAL_CUTOFF else
        "得分未低于原文切点，但不能排除认知问题；若本人或家属持续担心记忆或日常功能，仍需结合临床评估。"
    )
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的结果", "",
             f"原始任务合计：**{result['raw_score']} / {MAX_TOTAL} 分**。",
             f"教育年限：{collected.values['education_years']:g} 年；本次教育校正加分：{result['education_bonus']} 分。",
             f"校正后总分：**{result['adjusted_score']} / {MAX_TOTAL} 分**。",
             f"筛查分档：**{result['screening_category']}**（切点为 {NORMAL_CUTOFF} 分）。", "",
             interpretation, "", "## 输入核对", "",
             "| 已评分任务 | 得分 | 满分 |", "|---|---:|---:|"]
    lines.extend(f"| {labels[key]} | {collected.values[key]:g} | {maximum} |"
                 for key, maximum in TASK_MAXIMA.items())
    lines.extend(["", "这里只合计施测人员已经评定的任务得分，不自动判断答题、图形、症状或各认知域是否受损。",
                  "", "原研究在加拿大记忆门诊患者和健康老年对照中验证英文与法文版本；此切点不是所有年龄、语言和教育背景的统一诊断标准。中文任务标签仅方便录入，不表示完成了中文版验证。",
                  "", "本结果只适用于原版完整量表。简版、盲人版、电话版、Basic 版及未完成施测的记录不能套用；语言、听视力和施测条件需要由施测人员核对。",
                  "", "重复练习可能影响测评表现，不能把提高测试分数当作改善健康结局的目标。",
                  "", f"边界: {BOUNDARY}"])
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(out, manifest, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
