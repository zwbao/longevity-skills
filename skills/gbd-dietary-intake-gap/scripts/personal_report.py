"""Offline arithmetic comparison with the printed GBD 2017 dietary Table."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, FACTORS

TITLE = "GBD饮食摄入差值"
POSITION = {"below": "低于参考范围", "within": "在参考范围内", "above": "高于参考范围"}


def calculate(values):
    outputs = {}
    for key, factor in FACTORS.items():
        value, reference = values[key], factor["reference"]
        lower, upper = factor["reference_range"]
        prefix = factor["output"]
        outputs[prefix + "_delta"] = value - reference
        outputs[prefix + "_ratio_pct"] = value / reference * 100
        outputs[prefix + "_range_position"] = (
            "below" if value < lower else "above" if value > upper else "within")
    return outputs


def levers(values, targets):
    current = calculate(values)
    sensitivities = []
    individual = []
    for key, factor in FACTORS.items():
        prefix = factor["output"]
        sensitivities.append({
            "key": key, "label_zh": factor["label_zh"], "unit": factor["unit"],
            "value": values[key], "output": prefix + "_ratio_pct",
            "percentage_points_per_unit": 100 / factor["reference"],
            "delta_per_unit": 1.0,
        })
        if key in targets:
            changed = calculate(dict(values, **{key: targets[key]}))
            individual.append({
                "key": key, "label_zh": factor["label_zh"], "unit": factor["unit"],
                "from": values[key], "to": targets[key], "outputs": changed,
                "changes": {k: changed[k] - current[k] for k in changed
                            if not k.endswith("_range_position")},
            })
    payload = {
        "schema": "longevity-levers/1", "model": "gbd-dietary-intake-gap",
        "model_zh": TITLE, "current": current, "sensitivity": sensitivities,
        "levers": individual,
        "note_zh": "仅显示输入变化后的算术差值及比例；不是健康收益、风险降低或推荐目标。各项不相加、不加权，不模拟食物替代或能量补偿。钠情景表示尿钠测量值变化。",
    }
    if targets:
        moved = calculate(dict(values, **targets))
        payload["targets"] = {
            "values": targets, "outputs": moved,
            "changes": {k: moved[k] - current[k] for k in moved
                        if not k.endswith("_range_position")},
        }
    return payload


def read_input(path, manifest, *, targets=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError) as exc:
        return {}, [skillkit.Problem("targets" if targets else "measurements", "摄入表", "file",
                                     f"无法读取摄入表：{exc}")]
    problems = [p for p in collected.problems if not (targets and p.kind == "missing")]
    for name in collected.unmatched:
        problems.append(skillkit.Problem(name, name, "unknown", f"无法识别项目「{name}」，请按清单里的名称整理。"))
    if targets and not collected.values and not problems:
        problems.append(skillkit.Problem("targets", "目标表", "missing", "目标表至少需要一个可识别的摄入项目。"))
    return collected.values, problems


def consistency_problems(values):
    keys = ("omega6_energy_pct", "trans_fat_energy_pct")
    if all(key in values for key in keys) and sum(values[key] for key in keys) > 100:
        return [skillkit.Problem("omega6_energy_pct", "脂肪酸供能比", "inconsistent",
                                "Omega-6和反式脂肪供能比之和超过100%，请核对是总能量百分比而不是克数。")]
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="周岁；适用25岁及以上")
    parser.add_argument("--sex", help="可选上下文；参考表对男女相同，不参与计算")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("report.md", "result.json", "problems.json", "levers.json"):
        (args.out / name).unlink(missing_ok=True)
    values, problems = read_input(args.measurements, manifest)
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, "age", age)
    except ValueError:
        problems.append(skillkit.Problem("age", "年龄", "parse", "年龄需要可计算的有限数值，单位为周岁。"))
    targets = {}
    if args.targets is not None:
        targets, target_problems = read_input(args.targets, manifest, targets=True)
        for p in target_problems:
            p.message_zh = "目标表：" + p.message_zh
        problems += target_problems
    problems += consistency_problems(values)
    if targets:
        problems += consistency_problems(dict(values, **targets))
    card = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        problem_text = skillkit.problems_markdown(problems, TITLE, BOUNDARY).splitlines()[2:]
        (args.out / "report.md").write_text("\n".join(card + problem_text) + "\n", encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    outputs = calculate(values)
    skillkit.write_result(args.out, manifest, outputs)
    scenario = levers(values, targets)
    (args.out / "levers.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = card + [
        "## 你的摄入对照", "",
        "参考点来自GBD 2017对195个国家25岁及以上成人的人群估计：按各疾病全球死亡占比加权的最低风险摄入水平，没有在个人层面验证。", "",
        "各项为习惯性每日平均记录；尿钠为完整24小时收集结果。比例是记录值除以论文参考点，不是营养达标率。", "",
        "相对参考点不足或超量不等于需要补足或减到该值；尤其红肉、加工肉、含糖饮料、反式脂肪和钠的低值不构成增加摄入的理由。", "",
        "| 项目 | 你的记录 | 论文参考点（范围） | 相对参考点差值 | 占参考点比例 | 相对参考范围 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for key, factor in FACTORS.items():
        prefix = factor["output"]
        delta = outputs[prefix + "_delta"]
        lower, upper = factor["reference_range"]
        delta_unit = "个百分点" if factor["unit"] == "%" else "g/d"
        difference = (f"不足 {abs(delta):.4g}" if delta < 0 else f"超量 {delta:.4g}" if delta > 0 else "差值为 0")
        lines.append(f"| {factor['label_zh']} | {values[key]:.4g} {factor['unit']} | "
                     f"{factor['reference']:g}（{lower:g}–{upper:g}）{factor['unit']} | "
                     f"{difference} {delta_unit} | {outputs[prefix + '_ratio_pct']:.2f}% | "
                     f"{POSITION[outputs[prefix + '_range_position']]} |")
    lines += ["", "钠的参考范围较宽，反映原研究的证据不确定性；不能据此判定个人安全摄入量。", "",
              "## 输入口径", ""]
    for factor in FACTORS.values():
        lines.append(f"- {factor['label_zh']}：{factor['definition_zh']}")
    if targets:
        lines += ["", "## 你提供的目标情景", "", scenario["note_zh"], ""]
        for item in scenario["levers"]:
            prefix = FACTORS[item["key"]]["output"]
            lines.append(f"- {item['label_zh']}：{item['from']:.4g} → {item['to']:.4g} {item['unit']}；"
                         f"占参考点比例变为 {item['outputs'][prefix + '_ratio_pct']:.2f}%。")
    lines += ["", f"边界: {BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
