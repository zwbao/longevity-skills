"""Exact, offline Table 2 lookup for current adult smokers."""
import argparse
import copy
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, TABLE, TITLE, lookup


def problem(key, message, kind="applicability"):
    return skillkit.Problem(key, key, kind, message)


def collect(path, manifest):
    try:
        return skillkit.collect_file(Path(path) if path else None, manifest)
    except (OSError, UnicodeError, ValueError) as exc:
        return skillkit.Collected(problems=[problem("measurements", f"无法读取输入表：{exc}", "file")])


def validate_exposure(row, values):
    key = row["input_key"]
    label = "累计包年（每天一包强度折算的年数）" if key == "equivalent_smoking_years" else "每日平均卷烟等效支数"
    if key not in values:
        return [problem(key, f"缺少{label}。请补充真实吸烟史，不要用另一种暴露量代替。", "missing")]
    if values[key] not in [float(p) for p in row["points"]]:
        points = "、".join(sorted(row["points"], key=float))
        return [problem(key, f"表2仅印出 {points} {row['paper_unit']}。当前值没有对应表值，无法计算；不要改动真实输入来凑表值。", "unsupported_point")]
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements")
    parser.add_argument("--outcome")
    parser.add_argument("--age")
    parser.add_argument("--sex")
    parser.add_argument("--targets")
    parser.add_argument("--out", default="out")
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json", "levers.json", "report.md"):
        (out / name).unlink(missing_ok=True)
    collected = collect(args.measurements, manifest)
    problems = list(collected.problems)
    if collected.unmatched:
        problems.append(problem("measurements", "无法识别的指标：" + "、".join(collected.unmatched), "unknown"))
    if collected.values.get("current_smoker") not in (None, 1):
        problems.append(problem("current_smoker", "本表仅适用于当前吸烟者（current_smoker=1）；不适用于既往吸烟、从不吸烟或二手烟。"))
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
        except ValueError:
            problems.append(problem("age", "年龄必须是有限数值。", "parse"))
    problems += skillkit.check_scalar(manifest, "age", age)
    sex = {"male": "male", "female": "female", "男": "male", "女": "female"}.get(args.sex)
    sex_zh = {"male": "男", "female": "女"}.get(sex)
    if sex is None:
        problems.append(problem("sex", "请提供论文适用性核对所需的性别组：male/female 或 男/女。", "missing"))
    row = TABLE.get(args.outcome)
    if row is None:
        problems.append(problem("outcome", "请选择 references/outcomes.md 中的一项结局；本技能不含骨折二分类结果。", "unknown"))
    else:
        problems += validate_exposure(row, collected.values)
        if row["sex"] and sex and sex != row["sex"]:
            required_sex = {"male": "男性", "female": "女性"}[row["sex"]]
            problems.append(problem("sex", f"论文的{row['label_zh']}结果仅适用于{required_sex}组。"))
        if row["reference_age"] and age is not None:
            low, high = row["reference_age"]
            if not low <= age < high + 1:
                problems.append(problem("age", f"表2的{row['label_zh']}仅适用于 {low}–{high} 岁参考组；未实现其他年龄的衰减系数。"))
    target_values = None
    if args.targets:
        target_manifest = copy.deepcopy(manifest)
        for spec in target_manifest["inputs"]:
            spec["required"] = False
        targets = collect(args.targets, target_manifest)
        problems += targets.problems
        if targets.unmatched:
            problems.append(problem("targets", "目标表含无法识别的指标：" + "、".join(targets.unmatched), "unknown"))
        if row:
            problems += validate_exposure(row, targets.values)
            if set(targets.values) - {row["input_key"]}:
                problems.append(problem("targets", "目标表只能包含所选结局的一个暴露指标；年龄、性别、吸烟状态均不能在本比较中改变。"))
            if not problems:
                target_values = targets.values
    card = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        report = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        body = report.read_text().split("\n", 1)[1]
        report.write_text("\n".join(card) + body)
        skillkit.write_result(out, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    key = row["input_key"]
    exposure = collected.values[key]
    values = lookup(args.outcome, exposure)
    skillkit.write_result(out, manifest, values)
    unit_zh = "包年（每天一包强度折算的累计年数）" if key == "equivalent_smoking_years" else "支/天（卷烟等效支数）"
    lines = card + ["## 你的查表结果", "", f"结局：{row['label_zh']}。当前吸烟；年龄 {age:g} 岁，性别组：{sex_zh}。", "", f"你提供的暴露为 {exposure:g} {unit_zh}，对应正文表2的精确暴露点。", "", f"该暴露点的人群平均相对风险 RR = **{values['mean_rr']:.2f}**，95%不确定区间 **{values['ui_lower']:.2f}–{values['ui_upper']:.2f}**（包含研究间异质性）。", "", f"该关联的证据星级：{row['star_rating']}/5。星级描述研究证据，不是你的风险等级。"]
    if row["reference_age"]:
        low, high = row["reference_age"]
        lines += ["", f"仅使用论文 {low}–{high} 岁参考年龄组的表值，没有执行年龄外推。"]
    if args.outcome == "parkinsons_disease":
        lines += ["", "帕金森病的反向关联属于观察性证据，不能据此认为吸烟可预防疾病或有总体健康收益。"]
    if values["ui_lower"] <= 1 <= values["ui_upper"]:
        lines += ["", "这个暴露点的不确定区间包含1，不能把点估计当作已确定的风险差异。"]
    if target_values is not None:
        target = target_values[key]
        scenario = lookup(args.outcome, target)
        delta = scenario["mean_rr"] - values["mean_rr"]
        note = "仅比较两个人群暴露点的关联，不是个人干预效果；不能预测减量或戒烟后的获益。累计包年是已经发生的历史暴露，不能倒退。"
        levers = {"schema": "longevity-levers/1", "skill": manifest["name"], "current": values, "targets": scenario, "sensitivity": [], "levers": [{"key": key, "from": exposure, "to": target, "mean_rr": scenario["mean_rr"], "mean_rr_delta": delta}], "note_zh": note}
        (out / "levers.json").write_text(json.dumps(levers, ensure_ascii=False, indent=2) + "\n")
        lines += ["", "## 你提供的假设暴露点", "", f"{target:g} {unit_zh}：表中 RR {scenario['mean_rr']:.2f}，95%不确定区间 {scenario['ui_lower']:.2f}–{scenario['ui_upper']:.2f}。两表值之差为 {delta:+.2f}（RR单位）。", "", note, "", "未计算差值的不确定区间：论文未给出这两个表值所需的联合抽样数据。"]
    lines += ["", f"边界：{BOUNDARY}", "", "本查表不估计绝对风险、患病时间、寿命变化或治疗效果。"]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
