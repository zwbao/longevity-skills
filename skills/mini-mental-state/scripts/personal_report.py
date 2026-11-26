"""Offline summation of examiner-recorded original MMSE component scores."""
import argparse
import csv
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BOUNDARY, MAXIMUM_SCORES, PART_ONE, PART_TWO,
    PART_ONE_MAXIMUM, PART_TWO_MAXIMUM, TOTAL_MAXIMUM,
)

TITLE = "MMSE 认知检查得分汇总"


def calculate(values):
    first = sum(values[key] for key in PART_ONE)
    second = sum(values[key] for key in PART_TWO)
    return {"part_one_score": first, "part_two_score": second,
            "mmse_total_score": first + second}


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json"):
        (args.out / name).unlink(missing_ok=True)
    values = {}
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
        values = collected.values
        problems = list(collected.problems)
    except (OSError, ValueError, csv.Error) as exc:
        problems = [skillkit.Problem("measurements", "施测记录", "file",
                    f"无法读取施测记录：{exc}。请提供 marker,value,unit 三列的 CSV 或 TSV。")]
    labels = {s["key"]: s["label_zh"] for s in manifest["inputs"]}
    for key, value in values.items():
        if not float(value).is_integer():
            problems.append(skillkit.Problem(key, labels[key], "integer",
                            f"{labels[key]}必须是整数，不能四舍五入或按比例折算。"))
    if values.get("registration_learned") == 0:
        problems.append(skillkit.Problem("registration_learned", labels["registration_learned"],
                        "protocol", "记录显示记忆材料未全部学会。原文规定此时回忆不能有意义地测量，因此不计算完整总分。"))
    card = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = report.read_text(encoding="utf-8").split("\n", 1)[1]
        report.write_text("\n".join(card) + body, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    result = calculate(values)
    lines = card + [
        "## 你的结果", "",
        f"MMSE 总分：**{result['mmse_total_score']:g} / {TOTAL_MAXIMUM} 分**。",
        f"第一部分（定向、记忆及注意）：{result['part_one_score']:g} / {PART_ONE_MAXIMUM} 分。",
        f"第二部分（语言及图形任务）：{result['part_two_score']:g} / {PART_TWO_MAXIMUM} 分。", "",
        "| 记录项目 | 本次得分 | 满分 |", "|---|---:|---:|",
    ]
    lines += [f"| {labels[key]} | {values[key]:g} | {maximum} |"
              for key, maximum in MAXIMUM_SCORES.items()]
    lines += ["",
        "得分只描述本次完成这些任务的表现。这里没有正常、轻度或重度的诊断分档，也没有年龄、教育程度或中文版本的校正。",
        "本次按施测者已确认学会记忆材料处理；即刻记忆仍使用首次复述得分，注意任务只计一个得分。未完成或无法判断的项目不能填零，也不能折算为完整总分。",
        "本工具核算已记录的得分，不自动判断口语、句子或图形是否正确。原研究来自精神科患者及老年对照；它不提供经验证的中文施测材料。语言、教育、视听及运动条件对本次表现的影响仍需施测者评估。",
        "核对范围：复现了原文满分组合对应的小计和总分；这不是个人诊断准确性的验证。", "",
        f"边界: {BOUNDARY}",
    ]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
