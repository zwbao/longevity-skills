"""Offline original SATED scoring; all measurements are read by skillkit."""
import argparse
import copy
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, ITEMS, QUESTIONS_ZH, RESPONSE_SCORES, RESPONSE_ZH, score_answers

TITLE = "SATED 睡眠健康自评"


def collect(path, manifest, partial=False):
    specs = copy.deepcopy(manifest)
    if partial:
        for item in specs["inputs"]:
            item["required"] = False
    try:
        data = skillkit.collect_file(path, specs)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return {}, [skillkit.Problem("file", "回答文件", "file", f"无法读取回答表：{exc}")]
    problems = list(data.problems)
    for key, value in data.values.items():
        if value not in RESPONSE_SCORES.values():
            problems.append(skillkit.Problem(key, key, "response", "回答必须为 0、1 或 2 的整数，不能填写小时、分钟或连续平均值。"))
    for name in data.unmatched:
        problems.append(skillkit.Problem(name, name, "unknown", f"无法识别项目「{name}」；请使用原始 SATED 五项名称。"))
    if partial and not data.values and not problems:
        problems.append(skillkit.Problem("targets", "目标回答", "missing", "目标表至少需要一项回答。"))
    return data.values, problems


def levers(values, targets):
    current = score_answers(values)["sated_total_score"]
    result = {
        "schema": "longevity-levers/1", "model": "sated", "model_zh": "原始 SATED 五项计分",
        "current": {"sated_total_score": current},
        "sensitivity": [], "levers": [],
        "note_zh": "仅描述回答档位变化带来的算术分差；不是干预效果、健康收益或睡眠时长建议。离散量表不计算小时或分钟的导数。",
    }
    for key, label, unit in ITEMS:
        value = int(values[key])
        alternatives = []
        for option in RESPONSE_SCORES.values():
            if option != value:
                score = score_answers({**values, key: option})["sated_total_score"]
                alternatives.append({"to": option, "sated_total_score": score, "sated_total_score_delta": score - current})
        result["sensitivity"].append({"key": key, "label_zh": label, "unit": unit, "value": value, "alternatives": alternatives})
        if key in targets:
            score = score_answers({**values, key: targets[key]})["sated_total_score"]
            result["levers"].append({"key": key, "label_zh": label, "unit": unit, "from": value, "to": int(targets[key]), "sated_total_score": score, "sated_total_score_delta": score-current})
    if targets:
        total = score_answers({**values, **targets})["sated_total_score"]
        result["targets"] = {"values": targets, "sated_total_score": total, "sated_total_score_delta": total-current}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--age", help="可选成人年龄；不参与计分")
    parser.add_argument("--sex", help="可选背景信息；不参与计分")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json", "levers.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, "age", age)
    except ValueError:
        problems.append(skillkit.Problem("age", "年龄", "parse", "年龄必须是有效的成人年龄数值。"))
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, partial=True)
        for problem in target_problems:
            problem.message_zh = "目标表：" + problem.message_zh
        problems += target_problems
    header = [f"# {TITLE}", ""] + paper_card_lines() + [""]
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join(header) + body.replace("边界: ", "边界："), encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    scores = score_answers(values)
    lines = header + ["## 你的回答", "", "| 维度 | 题意（中文工作译文） | 回答 | 分数 |", "| --- | --- | --- | --- |"]
    for (key, label, _), question in zip(ITEMS, QUESTIONS_ZH):
        lines.append(f"| {label} | {question} | {RESPONSE_ZH[scores[key]]} | {scores[key]} |")
    lines += ["", f"**SATED 总分：{scores['sated_total_score']} / 10 分。**", "", "总分是五项相加，分数较高表示按原量表回答的睡眠健康特征较多。原论文没有提供中间分数的诊断阈值、正常参考区间或个体疾病风险换算。", "", "本次复现的是原图的选项计分对应关系，不代表量表已经获得临床验证。题目的时长范围是历史量表的题面，不是给你的睡眠时长处方。"]
    scenario = levers(values, targets)
    if targets:
        lines += ["", f"若目标回答全部实现，量表总分为 {scenario['targets']['sated_total_score']} / 10，分差为 {scenario['targets']['sated_total_score_delta']:+d}。仅为回答变化情景，不预测健康改善。"]
    lines += ["", "边界：" + BOUNDARY, ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    skillkit.write_result(args.out, manifest, scores)
    (args.out / "levers.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
