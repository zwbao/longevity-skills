"""Offline BMI category lookup; standard library runtime only."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (AGE_MIN, AGE_MAX_EXCLUSIVE, BMI_ROWS, BOUNDARY,
                     INPUT_UNITS, REFERENCE, SCENARIO_NOTE, TITLE)


def lookup(bmi):
    for row in BMI_ROWS:
        if row[0] <= bmi < row[1]:
            return row
    raise ValueError("BMI 不在论文 15≤BMI<60 kg/m² 的范围内，不能外推。")


def compute(values):
    bmi = values["weight_kg"] / (values["height_cm"] / 100) ** 2
    lower, upper, hr, low, high = lookup(bmi)
    return {"bmi_kg_m2": bmi, "bmi_category": f"{lower:.1f}–<{upper:.1f}",
            "category_hr": hr, "category_hr_ci_low": low, "category_hr_ci_high": high}


def levers(values, targets):
    current = compute(values)
    at_cut = any(current["bmi_kg_m2"] == row[0] for row in BMI_ROWS)
    sensitivity = []
    for key, unit in INPUT_UNITS.items():
        slope = (1 / (values["height_cm"] / 100) ** 2 if key == "weight_kg"
                 else -2 * current["bmi_kg_m2"] / values["height_cm"])
        sensitivity.append({"key": key, "unit": unit, "value": values[key],
                            "bmi_per_unit": slope,
                            "category_hr_per_unit": None if at_cut else 0.0,
                            "modifiable": key == "weight_kg"})
    payload = {"schema": "longevity-levers/1", "model": "bmi-mortality-category",
               "model_zh": TITLE, "current": current, "sensitivity": sensitivity,
               "levers": [], "note_zh": SCENARIO_NOTE}
    if targets:
        for key, value in targets.items():
            result = compute({**values, key: value})
            payload["levers"].append({"key": key, "unit": INPUT_UNITS[key],
                                      "from": values[key], "to": value, **result,
                                      "category_hr_delta": result["category_hr"] - current["category_hr"],
                                      "bmi_delta": result["bmi_kg_m2"] - current["bmi_kg_m2"]})
        result = compute({**values, **targets})
        payload["targets"] = {"values": targets, **result,
                              "category_hr_delta": result["category_hr"] - current["category_hr"],
                              "bmi_delta": result["bmi_kg_m2"] - current["bmi_kg_m2"]}
    return payload


def problem(key, message, kind="invalid"):
    return skillkit.Problem(key, key, kind, message)


def collect(path, manifest):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        return {}, [problem("file", f"无法读取测量文件：{exc}")]
    issues = list(collected.problems)
    for name in collected.unmatched:
        issues.append(problem("file", f"未识别项目「{name}」，请检查表头和项目名。"))
    return collected.values, issues


def fail(out, manifest, issues):
    path = skillkit.write_problems(out, issues, TITLE, BOUNDARY)
    text = path.read_text(encoding="utf-8")
    first, rest = text.split("\n", 1)
    path.write_text(first + "\n\n" + "\n".join(paper_card_lines()) + "\n" + rest, encoding="utf-8")
    skillkit.write_result(out, manifest, {x["key"]: None for x in manifest["outputs"]})
    return skillkit.EXIT_INPUT_PROBLEM


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="测量时年龄（岁）")
    parser.add_argument("--sex", help="可选上下文，不改变男女合并表值")
    parser.add_argument("--smoking", help="never/former/current/unknown；仅 never 可查表")
    parser.add_argument("--chronic-disease", help="no/yes/unknown；相关既往慢病，详见 SKILL.md")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "result.json", "levers.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    values, issues = collect(args.measurements, manifest)
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        issues.extend(skillkit.check_scalar(manifest, "age", age))
        if age is not None and not AGE_MIN <= age < AGE_MAX_EXCLUSIVE:
            issues.append(problem("age", "本工具限测量时 20 至未满 90 岁；附录与正文上限表述有差异，采用较窄范围。", "not_applicable"))
    except (ValueError, TypeError):
        issues.append(problem("age", "测量时年龄必须是有限数值，单位为岁。"))
    for key, value, allowed, accepted, label in (
        ("smoking", args.smoking, ("never", "former", "current", "unknown"), "never", "吸烟史"),
        ("chronic_disease", args.chronic_disease, ("no", "yes", "unknown"), "no", "相关既往慢病史"),
    ):
        if value is None or value == "unknown":
            issues.append(problem(key, f"请确认{label}；不能默认满足原研究人群条件。", "missing"))
        elif value not in allowed:
            issues.append(problem(key, f"{label}接受：{'/'.join(allowed)}。"))
        elif value != accepted:
            issues.append(problem(key, f"{label}不符合表 2 的从不吸烟、无相关既往慢病人群；不提供外推 HR。", "not_applicable"))
    if args.sex is not None and args.sex not in ("男", "女", "male", "female", "other", "unknown"):
        issues.append(problem("sex", "性别上下文接受：男/女/male/female/other/unknown。"))
    targets = {}
    if args.targets:
        target_manifest = {**manifest, "inputs": [{**x, "required": False} for x in manifest["inputs"]]}
        targets, target_issues = collect(args.targets, target_manifest)
        issues.extend(target_issues)
        if not targets and not target_issues:
            issues.append(problem("targets", "目标文件没有可读取的目标体重。", "missing"))
        if "height_cm" in targets:
            issues.append(problem("targets", "目标仅接受体重；身高保持实测值，不作为干预目标。"))
    if issues:
        return fail(args.out, manifest, issues)
    try:
        result = compute(values)
        scenario = levers(values, targets)
    except ValueError as exc:
        return fail(args.out, manifest, [problem("bmi_kg_m2", str(exc), "not_applicable")])
    skillkit.write_result(args.out, manifest, result)
    (args.out / "levers.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的测量", "",
             f"身高 {values['height_cm']:g} cm；体重 {values['weight_kg']:g} kg；测量时年龄 {age:g} 岁。",
             "已确认：从不吸烟，测量时无本工具列出的相关既往慢病。",
             f"BMI：{result['bmi_kg_m2']:.4f} kg/m²；分档：{result['bmi_category']} kg/m²（使用未四舍五入的 BMI 分档）。",
             "", "## 该档对应的研究结果", "",
             f"该档人群 HR：{result['category_hr']:.2f}；95% 组别置信区间：{result['category_hr_ci_low']:.2f}–{result['category_hr_ci_high']:.2f}。",
             f"参照档：{REFERENCE}。这是表 2 全地区、男女合并、年龄和性别调整后的关联；年龄和性别不用于个体校准。",
             "区间采用浮动方差法，反映组别估计的不确定性，不是你的个人风险范围；参照档也有区间。",
             "原分析排除了随访最初 5 年。这里不能确认未来存活，也不据此预测今后 5 年或 10 年的死亡概率。",
             "论文发现关联随年龄、性别和地区不同；合并结果不能替代这些亚组的专门估计。",
             "BMI 不区分肌肉与脂肪，也不表示内脏脂肪或脂肪分布。"]
    if targets:
        target = scenario["targets"]
        lines += ["", "## 你指定的目标体重情景", "",
                  f"体重 {targets['weight_kg']:g} kg 时，BMI 为 {target['bmi_kg_m2']:.4f} kg/m²，落在 {target['bmi_category']} 档；表中人群 HR 为 {target['category_hr']:.2f}。",
                  SCENARIO_NOTE]
    lines += ["", f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
