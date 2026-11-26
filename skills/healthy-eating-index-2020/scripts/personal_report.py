"""Offline HEI-2020 scoring of already prepared dietary densities (age >=2)."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, COMPONENTS, TITLE


def component_score(key, value):
    row = COMPONENTS[key]
    fraction = (value - row["zero"]) / (row["full"] - row["zero"])
    return row["points"] * max(0.0, min(1.0, fraction))


def calculate(values):
    outputs = {row["output"] + "_score": component_score(key, values[key])
               for key, row in COMPONENTS.items()}
    outputs["hei_total_score"] = sum(outputs.values())
    return outputs


def slopes(key, value):
    """Exact one-sided slopes, including the kinks at the published cutoffs."""
    row = COMPONENTS[key]
    low, high = sorted((row["zero"], row["full"]))
    slope = row["points"] / (row["full"] - row["zero"])
    return (slope if low < value <= high else 0.0,
            slope if low <= value < high else 0.0)


def consistency_problems(values):
    problems = []
    for subset, total in (
        ("whole_fruits_density_ratio", "total_fruits_density_ratio"),
        ("greens_beans_density_ratio", "total_vegetables_density_ratio"),
        ("seafood_plant_density_ratio", "total_protein_density_ratio"),
    ):
        if subset in values and total in values and values[subset] > values[total] + 1e-9:
            problems.append(skillkit.Problem(subset, COMPONENTS[subset]["label_zh"], "inconsistent",
                f"{COMPONENTS[subset]['label_zh']}密度不能超过{COMPONENTS[total]['label_zh']}密度；请使用同一记录期和同一总能量分母。"))
    sf = values.get("saturated_fats_energy_pct")
    sugar = values.get("added_sugars_energy_pct")
    ratio = values.get("fatty_acids_ratio")
    if sf == 0:
        problems.append(skillkit.Problem("fatty_acids_ratio", "脂肪酸比值", "undefined",
            "饱和脂肪供能为零时，脂肪酸比值的分母为零。本工具只接收可定义的有限比值；请核对原始脂肪酸记录，不可填零代替缺失。"))
    # Same energy per gram for saturated/unsaturated fatty acids, as on NCI's
    # linked MCMC methods page. All three energy contributions must fit in 100%.
    if sf is not None and sugar is not None and ratio is not None:
        if sugar + sf * (1 + ratio) > 100 + 1e-9:
            problems.append(skillkit.Problem("fatty_acids_ratio", "供能比例", "inconsistent",
                "添加糖、饱和及不饱和脂肪酸推算的供能比例合计超过100%；请核对脂肪酸比值和百分比口径。"))
    return problems


def read_inputs(path, manifest, *, targets=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError, csv.Error) as exc:
        return {}, [skillkit.Problem("targets" if targets else "measurements", "饮食表", "file", f"无法读取饮食表：{exc}")]
    problems = [p for p in collected.problems if not (targets and p.kind == "missing")]
    for name in collected.unmatched:
        problems.append(skillkit.Problem(name, name, "unknown", f"无法识别项目「{name}」，请使用清单中的名称。"))
    if targets and not collected.values and not problems:
        problems.append(skillkit.Problem("targets", "目标表", "missing", "目标表至少需要一项可识别的输入。"))
    return collected.values, problems


def levers(values, targets):
    current = calculate(values)
    sensitivity, individual = [], []
    for key, row in COMPONENTS.items():
        left, right = slopes(key, values[key])
        sensitivity.append({
            "key": key, "label_zh": row["label_zh"], "unit": row["unit"],
            "value": values[key], "output": "hei_total_score",
            "left_score_per_unit": left, "right_score_per_unit": right,
            "note_zh": "其他评分输入固定的数学斜率；切点两侧分别列出，输入范围外不适用。",
        })
        if key in targets:
            moved = dict(values, **{key: targets[key]})
            errors = consistency_problems(moved)
            changed = calculate(moved) if not errors else None
            individual.append({
                "key": key, "label_zh": row["label_zh"], "unit": row["unit"],
                "from": values[key], "to": targets[key], "outputs": changed,
                "score_delta": changed["hei_total_score"] - current["hei_total_score"] if changed else None,
                "problems": [p.as_dict() for p in errors],
            })
    payload = {
        "schema": "longevity-levers/1", "model": "healthy-eating-index-2020",
        "model_zh": TITLE, "current": current, "sensitivity": sensitivity, "levers": individual,
        "note_zh": "仅为评分算术情景，不是推荐目标或健康获益；不模拟真实食物替代及总能量变化。单项情景若违反食物包含关系或供能约束则不计算。",
    }
    if targets:
        together = calculate(dict(values, **targets))
        payload["targets"] = {"values": targets, "outputs": together,
                              "score_delta": together["hei_total_score"] - current["hei_total_score"]}
    return payload


def with_card(text):
    first, _, rest = text.partition("\n")
    return "\n".join([first, "", *paper_card_lines(), "", rest.lstrip("\n")])


def render(values, outputs, scenarios):
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的记录", "",
             f"HEI-2020 总分：{outputs['hei_total_score']:.2f} / 100。分数越高，表示这份记录与该版指南的符合程度越高。",
             "这是输入记录覆盖期间的评分；没有据此判定能量摄入是否适量，也没有计算长期通常摄入。", "",
             "| 项目 | 输入值 | 输入口径 | 得分 / 满分 |", "|---|---:|---|---:|"]
    for key, row in COMPONENTS.items():
        basis = ("相对 " + row["reference"] + " 的密度比") if row["reference"] else (
            "总能量百分比" if row["unit"] == "%" else "(PUFA + MUFA) / SFA 质量比")
        lines.append(f"| {row['label_zh']} | {values[key]:g} | {basis} | {outputs[row['output'] + '_score']:.2f} / {row['points']} |")
    lines += ["", "食物当量不是杯子的容量或食物净重；豆类须按方法计入蔬菜和蛋白质食物相应分组。",
              "该方法依据美国指南制定，不能直接等同于中国居民膳食指南的符合程度。"]
    if "targets" in scenarios:
        target = scenarios["targets"]
        lines += ["", "## 你提供的目标情景", "",
                  f"所有目标同时代入：{target['outputs']['hei_total_score']:.2f} / 100；相对当前记录变化 {target['score_delta']:+.2f} 分。",
                  scenarios["note_zh"], ""]
        for lever in scenarios["levers"]:
            if lever["score_delta"] is None:
                lines.append(f"- 仅改变{lever['label_zh']}：与其他输入不一致，未计算单项情景。")
            else:
                lines.append(f"- 仅改变{lever['label_zh']}：{lever['from']:g} → {lever['to']:g}，总分变化 {lever['score_delta']:+.2f} 分。")
    lines += ["", f"边界: {BOUNDARY}", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="必填，周岁，至少2岁")
    parser.add_argument("--sex", help="可选上下文，不参与评分")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("report.md", "problems.json", "result.json", "levers.json"):
        (args.out / name).unlink(missing_ok=True)
    values, problems = read_inputs(args.measurements, manifest)
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, "age", age)
    except ValueError:
        problems.append(skillkit.Problem("age", "年龄", "parse", "年龄需要有限数值，单位为周岁。"))
    problems += consistency_problems(values)
    targets = {}
    if args.targets is not None:
        targets, target_problems = read_inputs(args.targets, manifest, targets=True)
        target_problems += consistency_problems(dict(values, **targets))
        for p in target_problems:
            p.message_zh = "目标表：" + p.message_zh
        problems += target_problems
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        path.write_text(with_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    outputs = calculate(values)
    scenarios = levers(values, targets)
    (args.out / "report.md").write_text(render(values, outputs, scenarios), encoding="utf-8")
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / "levers.json").write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
