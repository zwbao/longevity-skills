"""Clinical Phenotypic Age using the published 2019 correction; standard library."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    AGE_LOG_FACTOR, AGE_OFFSET, AGE_SCALE, BOUNDARY, COEFFICIENTS,
    INTERCEPT, RISK_DENOMINATOR, RISK_NUMERATOR, TARGET_NOTE, TITLE,
)


def phenotypic_age(values):
    xb = INTERCEPT + math.fsum(
        weight * (math.log(values[key]) if key == "crp_mg_dl" else values[key])
        for key, weight in COEFFICIENTS.items()
    )
    # Substitute -ln(1-M) = 1.51714*exp(xb)/0.0076927 before evaluating.
    # This is algebraically identical and avoids M rounding to 0 or 1.
    return AGE_OFFSET + (math.log(AGE_LOG_FACTOR) + math.log(RISK_NUMERATOR)
                         - math.log(RISK_DENOMINATOR) + xb) / AGE_SCALE


def levers(values, targets, manifest):
    specs = {x["key"]: x for x in manifest["inputs"]}
    current = phenotypic_age(values)
    sensitivity = []
    for key, weight in COEFFICIENTS.items():
        spec = specs[key]
        slope = weight / AGE_SCALE
        if key == "crp_mg_dl":
            slope /= values[key]
        sensitivity.append({"key": key, "label_zh": spec["label_zh"],
                            "unit": spec["unit"], "value": values[key],
                            "years_per_unit": slope, "modifiable": key != "age"})
    data = {"schema": "longevity-levers/1", "model": "phenotypic-age",
            "model_zh": "表型年龄（Liu 2018，2019 更正公式）",
            "current": {"phenoage": current, "age": values["age"]},
            "sensitivity": sensitivity, "levers": [], "note_zh": TARGET_NOTE}
    for key, target in targets.items():
        changed = phenotypic_age({**values, key: target})
        data["levers"].append({"key": key, "label_zh": specs[key]["label_zh"],
                               "unit": specs[key]["unit"], "from": values[key],
                               "to": target, "phenoage": changed,
                               "phenoage_delta": changed - current})
    if targets:
        changed = phenotypic_age({**values, **targets})
        data["targets"] = {"values": targets, "phenoage": changed,
                           "phenoage_delta": changed - current}
    return data


def collect(path, manifest, targets=False):
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        return {}, [skillkit.Problem("targets" if targets else "measurements", "输入文件", "file",
                                    f"无法读取输入表格：{exc}")]
    problems = [x for x in result.problems if not targets or x.kind != "missing"]
    if targets:
        problems += [skillkit.Problem(name, name, "unknown_target",
                                     f"目标项目「{name}」不属于九项血检；年龄不能作为改善目标。")
                     for name in result.unmatched]
        if not result.values and not problems:
            problems.append(skillkit.Problem("targets", "目标表", "empty", "目标表没有可计算的血检目标。"))
    return result.values, problems


def write_report(out, measurements, age, targets_path=None):
    manifest = skillkit.load_manifest(__file__)
    out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "levers.json", "problems.json", "report.md"):
        (out / name).unlink(missing_ok=True)
    values, problems = collect(measurements, manifest)
    age_value = None
    if age is not None:
        try:
            age_value = skillkit.parse_number(str(age))
        except ValueError:
            problems.append(skillkit.Problem("age", "实足年龄", "parse", "年龄必须是有限的数值，单位为岁。"))
    if age is None or age_value is not None:
        problems += skillkit.check_scalar(manifest, "age", age_value)
    targets = {}
    if targets_path is not None:
        targets, target_problems = collect(targets_path, manifest, targets=True)
        problems += target_problems
    start = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        report = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        body = report.read_text(encoding="utf-8").split("\n", 2)[2]
        report.write_text("\n".join(start) + "\n" + body, encoding="utf-8")
        skillkit.write_result(out, manifest, {x["key"]: None for x in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    values["age"] = age_value
    score = phenotypic_age(values)
    delta = score - age_value
    scenarios = levers(values, targets, manifest)
    result = {"phenoage": score, "phenoage_difference": delta}
    lines = start + ["## 你的结果", "", "仍在验证：未找到论文印出的完整个人输入及对应表型年龄示例，读出为暂定。", "",
                     f"表型年龄：**{score:.2f} 岁**。实足年龄：{age_value:g} 岁。",
                     f"表型年龄减实足年龄：**{delta:+.2f} 岁**。", "",
                     "表型年龄表示在原始参考人群中具有相近模型死亡风险的年龄。它不是身体每个器官的真实年龄。",
                     "这里的简单年龄差不是论文的 PhenoAgeAccel（年龄回归残差），不能用来判断衰老速度或所属风险五分位。", "",
                     "## 本次输入", "", "| 项目 | 数值 | 单位 |", "|---|---:|---|"]
    for spec in manifest["inputs"]:
        key = spec["key"]
        if key in values:
            lines.append(f"| {spec['label_zh']} | {values[key]:g} | {spec['unit']} |")
    lines += ["", "应使用同一次、空腹至少 8 小时采血的九项结果；原研究排除了空腹不足的样本。",
              "本报告限 20–84 岁。85 岁以上在研究中被统一编码为 85 岁，不能据此建立精确年龄的个人读出。",
              "研究缺少重复表型年龄测量及疾病新发资料；短期分数变化不能证明衰老被逆转。"]
    if targets:
        lines += ["", "## 你提供的目标情景", "", TARGET_NOTE, "",
                  f"全部目标同时达到时：{scenarios['targets']['phenoage']:.2f} 岁，模型变化 {scenarios['targets']['phenoage_delta']:+.2f} 岁。", "",
                  "| 单独改变的项目 | 目标值 | 单位 | 模型年龄变化（岁） |", "|---|---:|---|---:|"]
        for item in scenarios["levers"]:
            lines.append(f"| {item['label_zh']} | {item['to']:g} | {item['unit']} | {item['phenoage_delta']:+.2f} |")
    lines += ["", f"边界: {BOUNDARY}", ""]
    (out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    skillkit.write_result(out, manifest, result)
    (out / "levers.json").write_text(json.dumps(scenarios, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="实足年龄（岁）；支持 20–84 岁")
    parser.add_argument("--sex", help="可选上下文；不进入公式，也不改变结果")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    return write_report(args.out, args.measurements, args.age, args.targets)


if __name__ == "__main__":
    raise SystemExit(main())
