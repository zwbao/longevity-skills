"""Original seven-item Diabetes Risk Score; standard-library-only CLI."""
from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    AGE_CUTS, BMI_CUTS, WAIST_CUTS, BINARY_KEYS, BOUNDARY, CATEGORY_LABELS,
    CUTOFF, MODIFIABLE, OUTPUT_KEYS, POINTS, TARGET_NOTE, TITLE,
)


def category_indices(values, age, sex):
    return {
        "age": bisect_right(AGE_CUTS, age),
        "bmi_kg_m2": bisect_left(BMI_CUTS, values["bmi_kg_m2"]),
        "waist_cm": bisect_right(WAIST_CUTS[sex], values["waist_cm"]),
        **{k: int(values[k]) for k in POINTS if k not in ("age", "bmi_kg_m2", "waist_cm")},
    }


def score(values, age, sex):
    categories = category_indices(values, age, sex)
    outputs = {OUTPUT_KEYS[key]: POINTS[key][index] for key, index in categories.items()}
    total = sum(outputs.values())
    outputs["total_score"] = total
    outputs["cutoff_category"] = "at_or_above_cutoff" if total >= CUTOFF else "below_cutoff"
    return outputs


def category_labels(key, sex):
    if key == "waist_cm":
        low, high = WAIST_CUTS[sex]
        return (f"<{low} cm", f"≥{low}至<{high} cm", f"≥{high} cm")
    return CATEGORY_LABELS[key]


def levers(values, age, sex, targets, manifest):
    """Exact category contrasts: derivatives would misrepresent a step score."""
    current = score(values, age, sex)
    categories = category_indices(values, age, sex)
    sensitivity = []
    for spec in manifest["inputs"]:
        key = spec["key"]
        item = {"key": key, "label_zh": spec["label_zh"], "unit": spec.get("unit", ""),
                "value": age if key == "age" else sex if key == "sex" else values[key],
                "modifiable": key in MODIFIABLE}
        if key in POINTS:
            index = categories[key]
            item.update({
                "method": "exact_category_contrast", "current_category": category_labels(key, sex)[index],
                "current_score": POINTS[key][index],
                "categories": [{"category": label, "score": points,
                                "score_delta": points - POINTS[key][index]}
                               for label, points in zip(category_labels(key, sex), POINTS[key])],
            })
        elif key == "sex":
            alternate = "female" if sex == "male" else "male"
            item.update({"method": "fixed_profile_contrast", "alternate": alternate,
                         "score_delta": score(values, age, alternate)["total_score"] - current["total_score"],
                         "note_zh": "只显示腰围阈值对性别资料的依赖，不是可改变目标。"})
        else:
            item.update({"method": "eligibility_only", "score_delta": None,
                         "note_zh": "接受降糖药治疗时不计算本评分，不作为用药目标。"})
        sensitivity.append(item)
    output = {"schema": "longevity-levers/1", "model": "finnish-diabetes-risk-score",
              "model_zh": TITLE, "current": current, "sensitivity": sensitivity,
              "levers": [], "note_zh": TARGET_NOTE + BOUNDARY}
    for key, target in targets.items():
        moved = score(dict(values, **{key: target}), age, sex)
        spec = skillkit.spec_by_key(manifest, key)
        output["levers"].append({"key": key, "label_zh": spec["label_zh"], "unit": spec["unit"],
                                 "from": values[key], "to": target, "outputs": moved,
                                 "score_delta": moved["total_score"] - current["total_score"]})
    if targets:
        moved = score(dict(values, **targets), age, sex)
        output["targets"] = {"values": targets, "outputs": moved,
                              "score_delta": moved["total_score"] - current["total_score"]}
    return output


def input_problem(key, kind, text, manifest):
    spec = next((s for s in manifest["inputs"] if s["key"] == key), {})
    return skillkit.Problem(key, spec.get("label_zh", key), kind, text)


def collect(path, manifest, partial=False):
    try:
        data = skillkit.collect_file(Path(path), manifest) if path else skillkit.collect_measurements([], manifest)
    except (OSError, ValueError) as exc:
        return {}, [input_problem("measurements", "file", f"无法读取输入表：{exc}", manifest)]
    problems = [p for p in data.problems if not (partial and p.kind == "missing")]
    for key in BINARY_KEYS:
        if key in data.values and data.values[key] not in (0, 1):
            problems.append(input_problem(key, "category", "问卷答案只能填0或1；不知道时请留空，不要估计。", manifest))
    if partial:
        for key in data.values:
            if key not in MODIFIABLE:
                problems.append(input_problem(key, "target", "这项是病史或适用条件，不能作为评分目标修改。", manifest))
        if not data.values and not problems:
            problems.append(input_problem("targets", "missing", "目标表至少需要一项BMI、腰围、活动或饮食目标。", manifest))
    # Unknown rows are surfaced, so a misspelled or unsupported target cannot disappear.
    for key in data.unmatched:
        problems.append(input_problem(key, "unknown", f"无法识别输入项目：{key}。请按技能清单提供项目名称。", manifest))
    return data.values, problems


def write_failure(out, problems):
    skillkit.write_problems(out, problems, TITLE, BOUNDARY)
    path = out / "report.md"
    text = path.read_text(encoding="utf-8")
    heading, body = text.split("\n", 1)
    path.write_text(heading + "\n\n" + "\n".join(paper_card_lines()) + "\n" + body, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="周岁，原研究适用35–64岁")
    parser.add_argument("--sex", help="male或female，仅决定腰围阈值")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "levers.json", "problems.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
    except ValueError:
        problems.append(input_problem("age", "parse", "年龄需要有限的数值，按周岁填写。", manifest))
    problems.extend(skillkit.check_scalar(manifest, "age", age))
    if age is not None and age != int(age):
        problems.append(input_problem("age", "category", "年龄按已满周岁填写整数。", manifest))
    sex = {"男": "male", "女": "female"}.get(args.sex, (args.sex or "").lower())
    if sex not in WAIST_CUTS:
        problems.append(input_problem("sex", "category", "请提供male（男）或female（女），用于原文的腰围阈值。", manifest))
    if values.get("antidiabetic_treatment") == 1:
        problems.append(input_problem("antidiabetic_treatment", "population", "原研究排除评估时接受降糖药治疗的人，本次不计算。", manifest))
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, partial=True)
        problems.extend(target_problems)
    if problems:
        write_failure(args.out, problems)
        return skillkit.EXIT_INPUT_PROBLEM
    outputs = score(values, age, sex)
    scenarios = levers(values, age, sex, targets, manifest)
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的结果", "",
             f"你的总分：**{outputs['total_score']}分**。", ""]
    if outputs["cutoff_category"] == "at_or_above_cutoff":
        lines.append(f"达到论文的≥{CUTOFF}分筛查切点。这表示进入原研究的风险升高组，不等于已患糖尿病。")
    else:
        lines.append(f"低于论文的{CUTOFF}分筛查切点，不能据此排除糖尿病或省略已有的检查安排。")
    lines += ["", "| 项目 | 你的类别 | 得分 |", "|---|---|---:|"]
    for key, index in category_indices(values, age, sex).items():
        label = skillkit.spec_by_key(manifest, key)["label_zh"]
        lines.append(f"| {label} | {category_labels(key, sex)[index]} | {outputs[OUTPUT_KEYS[key]]} |")
    lines += ["", "这是原版七项评分，不包含家族史，也不输出个人五年或十年患病概率。",
              "活动项按原文问卷类别填写：闲暇轻体力活动、活动不足每周4小时且工作以坐位为主时，填低活动=1。",
              "蔬果项按正文说明，每天吃记零分；是否用过降压药和血糖升高史均不能被当前正常测量抹去。"]
    if targets:
        lines += ["", "## 你提供的目标情景", "", TARGET_NOTE,
                  f"所有目标同时代入：{scenarios['targets']['outputs']['total_score']}分；"
                  f"相对当前变化{scenarios['targets']['score_delta']:+g}分。", "",
                  "| 单独代入的项目 | 当前值 | 目标值 | 单位 | 总分变化 |", "|---|---:|---:|---|---:|"]
        for item in scenarios["levers"]:
            lines.append(f"| {item['label_zh']} | {item['from']:g} | {item['to']:g} | {item['unit']} | {item['score_delta']:+g} |")
    lines += ["", f"边界：{BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / "levers.json").write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
