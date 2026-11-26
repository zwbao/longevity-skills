"""FIB-4 personal report; standard library only, all measurements via skillkit."""
import argparse
import copy
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, HIGH_CUTOFF, LABELS, LOW_CUTOFF, SCENARIO_NOTE, classify, fib4

TITLE = "FIB-4 肝纤维化指数"


def read_measurements(path, manifest, targets=False):
    spec = copy.deepcopy(manifest)
    if targets:
        for item in spec["inputs"]:
            item["required"] = False
    try:
        collected = skillkit.collect_file(path, spec)
    except (OSError, ValueError, TypeError) as exc:
        return skillkit.Collected(problems=[skillkit.Problem(
            "targets" if targets else "measurements", "输入文件", "file",
            f"无法读取输入表：{exc}。请提供 marker,value,unit 列的 CSV。")])
    if targets:
        for name in collected.unmatched:
            collected.problems.append(skillkit.Problem("targets", name, "unknown", f"情景表中「{name}」不是可改变的化验项；年龄保持不变。"))
        if not collected.values and not collected.problems:
            collected.problems.append(skillkit.Problem("targets", "情景表", "missing", "情景表没有可计算的化验项。"))
    return collected


def levers(values, targets, manifest):
    score = fib4(values)
    slopes = {"age_years": score / values["age_years"],
              "ast_u_l": score / values["ast_u_l"],
              "alt_u_l": -score / (2 * values["alt_u_l"]),
              "platelets_10e9_l": -score / values["platelets_10e9_l"]}
    specs = {s["key"]: s for s in manifest["inputs"]}
    result = {"schema": "longevity-levers/1", "model": "fib4_index",
              "model_zh": TITLE, "current": {"fib4_index": score},
              "note_zh": SCENARIO_NOTE, "sensitivity": [], "levers": []}
    for key, slope in slopes.items():
        result["sensitivity"].append({"key": key, "label_zh": specs[key]["label_zh"],
            "unit": specs[key]["unit"], "value": values[key], "score_per_unit": slope,
            "modifiable": key != "age_years"})
    for key, value in targets.items():
        moved = fib4(dict(values, **{key: value}))
        result["levers"].append({"key": key, "label_zh": specs[key]["label_zh"],
            "unit": specs[key]["unit"], "from": values[key], "to": value,
            "fib4_index": moved, "fib4_delta": moved - score})
    if targets:
        moved = fib4(dict(values, **targets))
        result["targets"] = {"values": targets, "fib4_index": moved,
                             "fib4_delta": moved - score, "fib4_category": classify(moved)}
    return result


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="采样时实足年龄，岁")
    parser.add_argument("--targets", type=Path, help="仅作数学情景的化验值 CSV")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("report.md", "problems.json", "result.json", "levers.json"):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    collected = read_measurements(args.measurements, manifest)
    problems = list(collected.problems)
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
    except ValueError:
        problems.append(skillkit.Problem("age_years", "实足年龄", "parse", "年龄必须是以岁为单位的有限数值。"))
    else:
        problems.extend(skillkit.check_scalar(manifest, "age_years", age))
    target_values = {}
    if args.targets is not None:
        target = read_measurements(args.targets, manifest, targets=True)
        problems.extend(target.problems)
        target_values = target.values
    header = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        report = skillkit.problems_markdown(problems, TITLE, BOUNDARY).split("\n", 2)[2]
        (args.out / "report.md").write_text("\n".join(header) + "\n" + report, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    values = dict(collected.values, age_years=age)
    score = fib4(values)
    category = classify(score)
    scenario = levers(values, target_values, manifest)
    interpretations = {
        "low": "处于论文较低值区间，不能由此确认没有进展期纤维化。",
        "indeterminate": "该分数落在论文无法明确区分的区间，不能仅凭此分档判断是否存在进展期纤维化。",
        "high": "处于论文较高值区间，提示应结合既有病史和其他检查由医生评估，不能由此确诊。",
    }
    lines = header + ["## 你的结果", "", f"FIB-4 指数：**{score:.6g}**（{LABELS[category]}）。",
        "", interpretations[category], "", "本方法用于成人非酒精性脂肪肝背景；若病因尚未明确或有其他肝病，分档的适用性需要另行评估。",
        "", f"表 5：低值 < {LOW_CUTOFF:.2f}，不确定 {LOW_CUTOFF:.2f}–{HIGH_CUTOFF:.2f}（含两端），高值 > {HIGH_CUTOFF:.2f}；分档使用未舍入的数值。",
        "", "## 本次输入", "", "| 项目 | 数值 | 单位 |", "| --- | ---: | --- |"]
    for item in manifest["inputs"]:
        lines.append(f"| {item['label_zh']} | {values[item['key']]:.8g} | {item['unit']} |")
    if target_values:
        moved = scenario["targets"]
        lines += ["", "## 输入情景", "", f"若仅将指定化验替换为情景值，指数为 {moved['fib4_index']:.6g}，变化为 {moved['fib4_delta']:+.6g}。", "", SCENARIO_NOTE]
    else:
        lines += ["", SCENARIO_NOTE]
    lines += ["", "队列中的阳性与阴性预测值依赖人群患病率，不能作为你的患病概率。", "", f"边界: {BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, {"fib4_index": score, "fib4_category": category})
    (args.out / "levers.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
