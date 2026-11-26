"""Compare alcohol exposure scenarios using published male stroke slopes."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (DAYS_PER_WEEK, GENETIC_CATEGORY_RANGE_G_WEEK, INTAKE_KEYS,
                     LABELS, REFERENCE_WEEKLY_DIFFERENCE_G, STROKE_RR)

TITLE = "饮酒量情景与卒中相对风险"
BOUNDARY = ("这是中国男性人群遗传研究的对数线性情景换算，不是个人发病概率、"
            "短期改变饮酒后的效果预测或安全饮酒阈值；不适用于女性或既往心脑血管病者，"
            "不用于诊断或用药决策，不能据此开始、停用或调整药物。")


def ratios_for_weekly_difference(delta_g_week):
    """Return (RR, lower, upper); a negative contrast reverses CI endpoints."""
    exponent = delta_g_week / REFERENCE_WEEKLY_DIFFERENCE_G
    results = {}
    for outcome, (rr, low, high) in STROKE_RR.items():
        bounds = sorted((low ** exponent, high ** exponent))
        results[outcome] = (rr ** exponent, *bounds)
    return results


def evaluate(values):
    delta = DAYS_PER_WEEK * (values[INTAKE_KEYS[0]] - values[INTAKE_KEYS[1]])
    low, high = GENETIC_CATEGORY_RANGE_G_WEEK
    within = all(low <= DAYS_PER_WEEK * values[key] <= high for key in INTAKE_KEYS)
    outputs = {"weekly_alcohol_difference_g": delta,
               "applicability": "within_category_means" if within else "extrapolation"}
    for outcome, triple in ratios_for_weekly_difference(delta).items():
        for suffix, value in zip(("rr", "rr_ci_low", "rr_ci_high"), triple):
            outputs[f"{outcome}_{suffix}"] = value
    return outputs


def scenario_note(outputs):
    if outputs["applicability"] == "extrapolation":
        return ("外推提示：至少一个摄入量情景超出附录男性遗传类别均值的 4–255 g/周范围"
                "（正文概述为 4–256）。以下仅是同一方程的外推；范围边缘不是安全阈值。")
    return ("两个情景在附录男性遗传类别均值的 4–255 g/周范围内；"
            "这不表示模型已经过个人预测验证。")


def make_levers(values, targets, manifest):
    current = evaluate(values)
    specs = {s["key"]: s for s in manifest["inputs"]}
    sensitivities = []
    for key, sign in zip(INTAKE_KEYS, (1, -1)):
        slopes = {name + "_rr": sign * current[name + "_rr"] * math.log(triple[0])
                  * DAYS_PER_WEEK / REFERENCE_WEEKLY_DIFFERENCE_G
                  for name, triple in STROKE_RR.items()}
        sensitivities.append({"key": key, "label_zh": specs[key]["label_zh"], "unit": "g/d",
                              "value": values[key], "rr_per_unit": slopes,
                              "modifiable": key == INTAKE_KEYS[0]})
    payload = {"schema": "longevity-levers/1", "model": "alcohol-stroke-loglinear-risk",
               "model_zh": TITLE, "current": current, "sensitivity": sensitivities,
               "levers": [], "note_zh": BOUNDARY}
    if targets:
        combined = dict(values, **targets)
        outputs = evaluate(combined)
        for key, target in targets.items():
            moved = evaluate(dict(values, **{key: target}))
            payload["levers"].append({"key": key, "label_zh": specs[key]["label_zh"],
                "unit": "g/d", "from": values[key], "to": target, "outputs": moved,
                "change": {o + "_rr": moved[o + "_rr"] - current[o + "_rr"] for o in STROKE_RR}})
        payload["targets"] = {"values": targets, "outputs": outputs,
                              "applicability": outputs["applicability"],
                              "note_zh": scenario_note(outputs)}
    return payload


def problem(key, kind, message):
    return skillkit.Problem(key, key, kind, message)


def collect(path, manifest, target=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError) as exc:
        return {}, [problem("targets" if target else "measurements", "file", f"无法读取输入表：{exc}")]
    problems = [p for p in collected.problems if not (target and p.kind == "missing")]
    if collected.unmatched:
        problems.append(problem("targets" if target else "measurements", "unknown",
                                "有未识别的项目：" + "、".join(collected.unmatched)))
    if target:
        if INTAKE_KEYS[1] in collected.values:
            problems.append(problem(INTAKE_KEYS[1], "target", "比较摄入量是固定参照，目标文件只接受当前纯酒精摄入量。"))
        if not collected.values and not problems:
            problems.append(problem("targets", "missing", "目标表没有可计算的目标，请填写当前纯酒精摄入量。"))
    return collected.values, problems


def parse_scalar(manifest, key, raw):
    if raw is None:
        return None, skillkit.check_scalar(manifest, key, None)
    try:
        value = skillkit.parse_number(raw)
    except ValueError:
        return None, [problem(key, "parse", f"{key} 需要有限数值。")]
    return value, skillkit.check_scalar(manifest, key, value)


def add_table(lines, outputs):
    lines += ["", "| 结局 | 模型相对风险 | 系数传播的 95% 区间 |", "| --- | ---: | ---: |"]
    for key, label in LABELS.items():
        lines.append(f"| {label} | {outputs[key + '_rr']:.3f} | "
                     f"{outputs[key + '_rr_ci_low']:.3f}–{outputs[key + '_rr_ci_high']:.3f} |")


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--age")
    parser.add_argument("--sex")
    parser.add_argument("--prior-cvd", help="0=无既往冠心病、卒中或短暂性脑缺血；1=有")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ("result.json", "levers.json", "problems.json", "report.md"):
        (args.out / filename).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    _, age_problems = parse_scalar(manifest, "age", args.age)
    problems += age_problems
    prior, prior_problems = parse_scalar(manifest, "prior_cvd", args.prior_cvd)
    problems += prior_problems
    if not prior_problems and prior != 0:
        problems.append(problem("prior_cvd", "population", "疾病分析排除了既往冠心病、卒中或短暂性脑缺血者，本次不计算。"))
    if args.sex is None:
        problems.append(problem("sex", "missing", "缺少性别；本模型仅支持男性。"))
    elif args.sex.strip().lower() not in {"male", "男"}:
        problems.append(problem("sex", "population", "仅接受 male 或男；论文女性结果不能用作女性饮酒风险系数。"))
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, target=True)
        problems += target_problems
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    outputs = evaluate(values)
    levers = make_levers(values, targets, manifest)
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 情景比较", "",
             f"当前情景：平均 {values[INTAKE_KEYS[0]]:.3f} g/日纯酒精"
             f"（一周总量 {values[INTAKE_KEYS[0]] * DAYS_PER_WEEK:.3f} g）。",
             f"比较情景：平均 {values[INTAKE_KEYS[1]]:.3f} g/日纯酒精"
             f"（一周总量 {values[INTAKE_KEYS[1]] * DAYS_PER_WEEK:.3f} g）。",
             f"当前减比较：一周纯酒精总量相差 {outputs['weekly_alcohol_difference_g']:.3f} g。", "",
             "下表分子是当前情景，分母是比较情景；1 表示模型中相同的风险水平。",
             scenario_note(outputs)]
    add_table(lines, outputs)
    lines += ["", "区间只传播论文斜率的不确定性，不包括摄入量误报、个体差异或模型外推误差。",
              "这里沿用长期暴露的对数线性假设；相同周总量不能反映集中大量饮酒与均匀饮酒的差异。",
              "研究主要涉及中国男性和烈酒；不能将结果当作女性、其他人群或特定酒种的已验证个体效应。",
              "未计算心肌梗死风险；该研究未检出明确净关联，不等于证明无风险或有保护作用。"]
    if targets:
        lines += ["", "## 目标情景", "",
                  f"你提供的目标：平均 {targets[INTAKE_KEYS[0]]:.3f} g/日纯酒精。比较情景保持固定。",
                  "这只是代入你给出的目标，不表示建议采用该目标。",
                  scenario_note(levers["targets"]["outputs"])]
        add_table(lines, levers["targets"]["outputs"])
    lines += ["", f"边界：{BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / "levers.json").write_text(json.dumps(levers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
