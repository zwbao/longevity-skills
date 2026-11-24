"""Conditional NREM power contrast, using published unstandardized slopes."""
import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import AGE_GROUPS, BOUNDARY, COEFFICIENTS, RATIO_KEYS, TITLE


def calculate(values):
    eeg_db, bold_db = (10 * math.log10(values[k]) for k in RATIO_KEYS)
    eeg_term = COEFFICIENTS[RATIO_KEYS[0]] * eeg_db
    bold_term = COEFFICIENTS[RATIO_KEYS[1]] * bold_db
    return {"eeg_power_difference_db": eeg_db, "bold_power_difference_db": bold_db,
            "eeg_conditional_term_db": eeg_term, "bold_conditional_term_db": bold_term,
            "csf_power_difference_db": eeg_term + bold_term}


def levers(values, targets, manifest):
    current = calculate(values)["csf_power_difference_db"]
    specs = {s["key"]: s for s in skillkit.input_specs(manifest)}
    payload = {"schema": "longevity-levers/1", "model": manifest["name"],
               "model_zh": TITLE, "current": {"csf_power_difference_db": current},
               "sensitivity": [], "levers": [], "note_zh": BOUNDARY}
    for key, coefficient in COEFFICIENTS.items():
        payload["sensitivity"].append({
            "key": key, "label_zh": specs[key]["label_zh"], "unit": "1",
            "value": values[key], "db_per_unit": 10 * coefficient / (math.log(10) * values[key]),
            "db_per_db": coefficient})
        if key in targets:
            moved = calculate(dict(values, **{key: targets[key]}))["csf_power_difference_db"]
            payload["levers"].append({
                "key": key, "label_zh": specs[key]["label_zh"], "unit": "1",
                "from": values[key], "to": targets[key], "csf_power_difference_db": moved,
                "csf_power_difference_delta_db": moved - current})
    if targets:
        together = calculate(dict(values, **targets))["csf_power_difference_db"]
        payload["targets"] = {"values": targets, "csf_power_difference_db": together,
                              "csf_power_difference_delta_db": together - current}
    return payload


def collect(path, manifest, partial=False):
    try:
        data = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError) as error:
        return {}, [skillkit.Problem("measurements", "输入文件", "file", f"无法读取测量表：{error}")]
    problems = [p for p in data.problems if not (partial and p.kind == "missing")]
    for name in data.unmatched:
        problems.append(skillkit.Problem(name, name, "unknown", f"无法识别指标「{name}」；请提供 NREM 线性功率比，而非绝对功率或 dB 数。"))
    if partial and not data.values and not problems:
        problems.append(skillkit.Problem("targets", "目标文件", "missing", "目标文件没有可用的功率比。"))
    return data.values, problems


def age_value(raw, key, manifest):
    try:
        value = skillkit.parse_number(raw) if raw is not None else None
    except (ValueError, TypeError):
        return None, [skillkit.Problem(key, "记录时年龄", "parse", "记录时年龄必须是有限数值（岁）。")]
    problems = skillkit.check_scalar(manifest, key, value)
    if not problems and not any(low <= value <= high for low, high in AGE_GROUPS):
        problems.append(skillkit.Problem(key, "记录时年龄", "population", "研究夜间样本为 18–39 岁或 60–83 岁，不外推到中年或其他年龄。"))
    return value, problems


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age")
    parser.add_argument("--reference-age")
    parser.add_argument("--sex", help="仅作背景，不参与本模型")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args()
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "levers.json", "problems.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    age, issues = age_value(args.age, "age", manifest)
    problems.extend(issues)
    reference_age, issues = age_value(args.reference_age, "reference_age", manifest)
    problems.extend(issues)
    if age is not None and reference_age is not None and not problems:
        if not any(low <= age <= high and low <= reference_age <= high for low, high in AGE_GROUPS):
            problems.append(skillkit.Problem("reference_age", "参照记录年龄", "population", "两份记录必须来自同一年龄组；跨年龄组时年龄项不能抵消。"))
    targets = {}
    if args.targets is not None:
        targets, issues = collect(args.targets, manifest, partial=True)
        problems.extend(issues)
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 1)[1]
        path.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", body]), encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    result = calculate(values)
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的模型对比", "",
             f"比较记录年龄：{age:g} 岁；参照记录年龄：{reference_age:g} 岁。",
             "差值方向固定为比较记录减参照记录；两份记录都必须是同流程采集和处理的 NREM 睡眠。",
             "", "| 项目 | 数值（dB） |", "|---|---:|"]
    for spec in manifest["outputs"]:
        lines.append(f"| {spec['label_zh']} | {result[spec['key']]:+.3f} |")
    lines += ["", "正值表示比较记录的模型功率更高，负值表示更低；没有正常/异常切点。",
              "EEG 与 BOLD 项是相互调整后的模型项，不代表独立的因果机制或对你的病因诊断。",
              "未计算绝对 CSF 功率、真实流速或个人预测区间。研究未验证这套关系能预测同一个人的长期变化。",
              "本方法需要研究级同步 EEG/fMRI 功率；手环睡眠时长、睡眠分期比例和常规 MRI 报告不能替代。"]
    if targets:
        target_value = calculate(dict(values, **targets))["csf_power_difference_db"]
        lines += ["", f"目标情景下的模型差为 {target_value:+.3f} dB。目标是相对同一参照记录的功率比，仅作数学情景对比，不是睡眠或血管干预的疗效预测。"]
    lines += ["", f"边界：{BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    (args.out / "levers.json").write_text(json.dumps(levers(values, targets, manifest), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
