"""Original CAIDE Model 1 and Model 2, standard library only."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (TITLE, BOUNDARY, TARGET_NOTE, MODIFIABLE, CUTS, POINTS,
                     OUTPUT_KEYS, CATEGORY_LABELS, RISK_TABLE, LOGISTIC, CUTOFF)


def category_indices(values, age, sex, model):
    age_low, age_high = CUTS["age"]
    edu_low, edu_high = CUTS["education_years"]
    indices = {"age": 0 if age < age_low else 1 if age <= age_high else 2,
               "education_years": 0 if values["education_years"] <= edu_low else
               1 if values["education_years"] <= edu_high else 2,
               "sex": int(sex == "male"),
               **{k: int(values[k] > CUTS[k]) for k in
                  ("sbp_mmhg", "bmi_kg_m2", "total_cholesterol_mmol_l")},
               "active": int(values["active"])}
    if model == 2:
        indices["apoe_e4"] = int(values["apoe_e4"])
    return indices


def lookup(total, model):
    for low, high, risk, ci_low, ci_high in RISK_TABLE[model]:
        if low <= total <= high:
            return {"category": f"{low}–{high}", "risk_pct": risk,
                    "ci_low_pct": ci_low, "ci_high_pct": ci_high}
    raise ValueError("score outside the printed table")


def cutoff(total, model):
    return "at_or_above_cutoff" if total >= CUTOFF[model] else "below_cutoff"


def score(values, age, sex, model=1):
    categories = category_indices(values, age, sex, model)
    outputs = {OUTPUT_KEYS[k]: POINTS[model][k][i] for k, i in categories.items()}
    total = sum(outputs.values())
    group = lookup(total, model)
    b0, b1, b2 = LOGISTIC[model]
    outputs.update({"model": model, "total_score": total, "score_category": group["category"],
                    "group_risk_20y_pct": group["risk_pct"],
                    "group_ci_low_pct": group["ci_low_pct"], "group_ci_high_pct": group["ci_high_pct"],
                    "model_risk_20y_pct": 100 / (1 + math.exp(-(b0 + b1 + b2 * total))),
                    "cutoff_category": cutoff(total, model)})
    return outputs


def deltas(current, moved):
    return {"score_delta": moved["total_score"] - current["total_score"],
            "model_risk_delta_pp": moved["model_risk_20y_pct"] - current["model_risk_20y_pct"],
            "group_risk_delta_pp": moved["group_risk_20y_pct"] - current["group_risk_20y_pct"]}


def levers(values, age, sex, model, targets, manifest):
    """Exact category contrasts, because derivatives obscure threshold jumps."""
    current = score(values, age, sex, model)
    indices = category_indices(values, age, sex, model)
    sensitivity = []
    for spec in manifest["inputs"]:
        key = spec["key"]
        item = {"key": key, "label_zh": spec["label_zh"], "unit": spec.get("unit", ""),
                "value": age if key == "age" else sex if key == "sex" else values.get(key),
                "modifiable": key in MODIFIABLE}
        if key in indices:
            points = POINTS[model][key]
            index = indices[key]
            item.update({"method": "exact_category_contrast", "current_score": points[index],
                         "current_category": CATEGORY_LABELS[key][index], "categories": []})
            for label, contribution in zip(CATEGORY_LABELS[key], points):
                total = current["total_score"] + contribution - points[index]
                b0, b1, b2 = LOGISTIC[model]
                moved = {"total_score": total, "model_risk_20y_pct": 100 / (1 + math.exp(-(b0 + b1 + b2 * total))),
                         "group_risk_20y_pct": lookup(total, model)["risk_pct"]}
                item["categories"].append({"category": label, "score": contribution, **deltas(current, moved)})
        else:
            item.update({"method": "not_in_model", "note_zh": "模型1不使用APOE状态；未知不等于非携带者。"})
        sensitivity.append(item)
    output = {"schema": "longevity-levers/1", "model": f"caide-model-{model}", "model_zh": TITLE,
              "current": current, "sensitivity": sensitivity, "levers": [],
              "note_zh": TARGET_NOTE + BOUNDARY}
    for key, target in targets.items():
        moved = score(dict(values, **{key: target}), age, sex, model)
        spec = skillkit.spec_by_key(manifest, key)
        output["levers"].append({"key": key, "label_zh": spec["label_zh"], "unit": spec["unit"],
                                 "from": values[key], "to": target, "outputs": moved, **deltas(current, moved)})
    if targets:
        moved = score(dict(values, **targets), age, sex, model)
        output["targets"] = {"values": targets, "outputs": moved, **deltas(current, moved)}
    return output


def problem(key, kind, message, manifest):
    spec = next((s for s in manifest["inputs"] if s["key"] == key), {})
    return skillkit.Problem(key, spec.get("label_zh", key), kind, message)


def collect(path, manifest, partial=False):
    try:
        data = skillkit.collect_file(path, manifest) if path else skillkit.collect_measurements([], manifest)
    except (OSError, ValueError) as exc:
        return {}, [problem("measurements", "file", f"无法读取输入表：{exc}", manifest)]
    problems = [p for p in data.problems if not (partial and p.kind == "missing")]
    for key in ("active", "apoe_e4"):
        if key in data.values and data.values[key] not in (0, 1):
            problems.append(problem(key, "category", "仅接受0或1；不知道时请留空，不要估计。", manifest))
    if "education_years" in data.values and not data.values["education_years"].is_integer():
        problems.append(problem("education_years", "category", "填写完成的整年教育年限，不对非整数分类。", manifest))
    for key in data.unmatched:
        problems.append(problem(key, "unknown", f"无法识别项目：{key}。", manifest))
    if partial:
        for key in data.values:
            if key not in MODIFIABLE:
                problems.append(problem(key, "target", "这项不是本模型允许修改的目标。", manifest))
        if not data.values and not problems:
            problems.append(problem("targets", "missing", "目标表至少填写一项血压、BMI、总胆固醇或活动状态。", manifest))
    return data.values, problems


def write_failure(out, problems):
    skillkit.write_problems(out, problems, TITLE, BOUNDARY)
    path = out / "report.md"
    heading, body = path.read_text(encoding="utf-8").split("\n", 1)
    path.write_text(heading + "\n\n" + "\n".join(paper_card_lines()) + "\n" + body, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="测量时的周岁，39–64岁")
    parser.add_argument("--sex", help="male/男或female/女")
    parser.add_argument("--model", default="1", help="1=常规七项；2=含APOE的八项")
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
        problems.append(problem("age", "parse", "年龄需要有限数值。", manifest))
    problems.extend(skillkit.check_scalar(manifest, "age", age))
    if age is not None and age != int(age):
        problems.append(problem("age", "category", "请填写已满周岁整数。", manifest))
    sex = {"男": "male", "女": "female"}.get(args.sex, (args.sex or "").lower())
    if sex not in ("male", "female"):
        problems.append(problem("sex", "category", "请提供male（男）或female（女）。", manifest))
    model = int(args.model) if args.model in ("1", "2") else None
    if model is None:
        problems.append(problem("model", "category", "模型只能选1或2。", manifest))
    if model == 2 and "apoe_e4" not in values:
        problems.append(problem("apoe_e4", "missing", "模型2需要已知APOE ε4携带状态；没有结果可选模型1，不要填0替代未知。", manifest))
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, partial=True)
        problems.extend(target_problems)
    if problems:
        write_failure(args.out, problems)
        return skillkit.EXIT_INPUT_PROBLEM
    outputs = score(values, age, sex, model)
    scenarios = levers(values, age, sex, model, targets, manifest)
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的结果", "",
             f"采用模型{model}，总分：**{outputs['total_score']}分**；分组：{outputs['score_category']}分。",
             f"相同分组在原队列的约20年痴呆发生比例：**{outputs['group_risk_20y_pct']:.1f}%**"
             f"（组比例的95%置信区间：{outputs['group_ci_low_pct']:.1f}%至{outputs['group_ci_high_pct']:.1f}%）。",
             f"把总分代入论文连续风险公式得到：**{outputs['model_risk_20y_pct']:.2f}%**。",
             "分组发生比例与连续公式估计来自不同计算，不能混用；置信区间属于原研究分组，不是你的个人预测区间。",
             "上述结果未针对当代中国人群校准，也不表示已患痴呆。",
             f"{'达到' if outputs['cutoff_category'] == 'at_or_above_cutoff' else '未达到'}"
             f"论文模型{model}的≥{CUTOFF[model]}分筛查切点；切点不是诊断标准。", "",
             "| 项目 | 你的类别 | 得分 |", "|---|---|---:|"]
    for key, index in category_indices(values, age, sex, model).items():
        label = skillkit.spec_by_key(manifest, key)["label_zh"]
        lines.append(f"| {label} | {CATEGORY_LABELS[key][index]} | {outputs[OUTPUT_KEYS[key]]} |")
    lines += ["", "活动定义：闲暇体力活动每周至少两次、每次至少20–30分钟，且达到出汗和气喘的程度；不直接用步数代替。",
              "这些输入应来自同一中年评估时点，不能把老年血压与中年年龄拼在一起。"]
    if model == 1:
        lines.append("本次模型1不使用APOE；即使提供该项，也不会按模型2加分。")
    if outputs["group_ci_low_pct"] < 0:
        lines.append("本组置信区间下限为原表印出的负值，反映区间近似方法，并非负的患病概率。")
    if targets:
        target = scenarios["targets"]
        lines += ["", "## 你提供的目标情景", "", TARGET_NOTE,
                  f"所有目标同时代入：{target['outputs']['total_score']}分，"
                  f"连续公式估计{target['outputs']['model_risk_20y_pct']:.2f}%，"
                  f"相对当前变化{target['model_risk_delta_pp']:+.2f}个百分点。",
                  "变化是模型内比较，不是已证实的个人获益；分组比例可能随跨组发生不规则变化。", "",
                  "| 单独代入项目 | 当前值 | 目标值 | 单位 | 总分变化 |", "|---|---:|---:|---|---:|"]
        for item in scenarios["levers"]:
            lines.append(f"| {item['label_zh']} | {item['from']:g} | {item['to']:g} | {item['unit']} | {item['score_delta']:+g} |")
    lines += ["", f"边界：{BOUNDARY}"]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / "levers.json").write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
