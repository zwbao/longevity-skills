"""Offline, sex-specific INTERHEART waist/hip tertiles and Table 3 lookup."""
import argparse
import csv
import io
import json
from decimal import Decimal
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (ASSOCIATIONS, BOUNDARY, BOUNDARY_NOTE, CUTPOINTS,
                     INPUT_UNITS, SCENARIO_NOTE, TITLE)


def lookup(tertile):
    if tertile == 1:
        return (1.0, None, None)  # Reference definition, not a fitted CI.
    return ASSOCIATIONS[tertile]


def compute(values, sex):
    waist, hip = (Decimal(str(values[k])) for k in INPUT_UNITS)
    low, high = CUTPOINTS[sex]
    ratio = waist / hip
    # Compare products, before decimal display rounding; do not invent <= rules.
    if waist == low * hip or waist == high * hip:
        tertile = None
        category = "切点边界：归属未说明"
        association = (None, None, None)
    else:
        tertile = 1 if waist < low * hip else (2 if waist < high * hip else 3)
        category = {1: "第1三分位组（参照）", 2: "第2三分位组", 3: "第3三分位组"}[tertile]
        association = lookup(tertile)
    return {"waist_hip_ratio": float(ratio), "tertile": tertile, "category": category,
            "category_or": association[0], "category_or_ci_low": association[1],
            "category_or_ci_high": association[2]}


def levers(values, targets, sex):
    current = compute(values, sex)
    payload = {"schema": "longevity-levers/1", "model": "interheart-waist-hip-tertiles",
               "model_zh": TITLE, "current": current, "sensitivity": [],
               "levers": [], "note_zh": SCENARIO_NOTE}
    for key in INPUT_UNITS:
        slope = (1 / values["hip_cm"] if key == "waist_cm"
                 else -values["waist_cm"] / values["hip_cm"] ** 2)
        payload["sensitivity"].append({"key": key, "unit": "cm", "value": values[key],
                                       "waist_hip_ratio_per_unit": slope,
                                       "note_zh": "局部算术导数，不表示疾病风险变化。"})
    for key, value in targets.items():
        result = compute({**values, key: value}, sex)
        payload["levers"].append({"key": key, "unit": "cm", "from": values[key],
                                  "to": value, **result,
                                  "waist_hip_ratio_delta": result["waist_hip_ratio"] - current["waist_hip_ratio"]})
    if targets:
        result = compute({**values, **targets}, sex)
        payload["targets"] = {"values": targets, **result,
                              "waist_hip_ratio_delta": result["waist_hip_ratio"] - current["waist_hip_ratio"]}
    return payload


def problem(key, message, kind="invalid"):
    return skillkit.Problem(key, key, kind, message)


def collect(path, manifest):
    try:
        if path is not None:
            text = path.read_text(encoding="utf-8-sig")
            delimiter = "\t" if text[:2048].count("\t") > text[:2048].count(",") else ","
            rows = csv.DictReader(io.StringIO(text), delimiter=delimiter)
            if any(None in row for row in rows):
                return {}, [problem("file", "存在比表头更多的单元格，请检查分隔符和未加引号的数值。")]
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError, csv.Error, AttributeError, TypeError) as exc:
        return {}, [problem("file", f"无法读取测量文件：{exc}")]
    issues = list(collected.problems)
    issues.extend(problem("file", f"未识别项目「{name}」，请检查项目名。")
                  for name in collected.unmatched)
    return collected.values, issues


def fail(out, manifest, issues):
    path = skillkit.write_problems(out, issues, TITLE, BOUNDARY)
    first, rest = path.read_text().split("\n", 1)
    path.write_text(first + "\n\n" + "\n".join(paper_card_lines()) + "\n" + rest)
    skillkit.write_result(out, manifest, {x["key"]: None for x in manifest["outputs"]})
    return skillkit.EXIT_INPUT_PROBLEM


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--sex", help="male/female/男/女，选择论文的性别分层")
    parser.add_argument("--age", help="可选年龄（岁），只作上下文，不改变分组")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "result.json", "levers.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    values, issues = collect(args.measurements, manifest)
    sex = {"male": "male", "female": "female", "男": "male", "女": "female"}.get(args.sex)
    if sex is None:
        issues.append(problem("sex", "请提供论文分层所需的性别：male/female/男/女；不能默认。",
                              "missing" if args.sex is None else "invalid"))
    age = None
    try:
        age = skillkit.parse_number(args.age) if args.age is not None else None
        issues.extend(skillkit.check_scalar(manifest, "age", age))
    except (ValueError, TypeError):
        issues.append(problem("age", "年龄须为有限数值，单位为岁。"))
    targets = {}
    if args.targets:
        target_manifest = {**manifest, "inputs": [{**x, "required": False} for x in manifest["inputs"]]}
        targets, target_issues = collect(args.targets, target_manifest)
        issues.extend(target_issues)
        if not targets and not target_issues:
            issues.append(problem("targets", "目标文件须至少包含一项腰围或臀围。", "missing"))
    if issues:
        return fail(args.out, manifest, issues)
    result = compute(values, sex)
    scenario = levers(values, targets, sex)
    skillkit.write_result(args.out, manifest, result)
    (args.out / "levers.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    low, high = CUTPOINTS[sex]
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的测量", "",
             f"腰围 {values['waist_cm']:g} cm；臀围 {values['hip_cm']:g} cm；论文性别分层：{'男' if sex == 'male' else '女'}。",
             f"腰臀比（腰围÷臀围）：{result['waist_hip_ratio']:.6g}；{result['category']}。",
             f"该性别切点：{low}、{high}；按未取显示舍入的测量计算。", BOUNDARY_NOTE,
             "这些三分位组来自研究对照人群，不是临床肥胖诊断界值，也不表示你在当前当地人群的百分位。"]
    if age is not None:
        lines.append(f"年龄上下文：{age:g} 岁；不用于校准个人风险。")
    if result["tertile"] is None:
        lines += ["", "本次只报告腰臀比；切点等号归属不明，因此不输出该档人群 OR。"]
    elif result["tertile"] == 1:
        lines += ["", "此组为表 3 的比较参照（OR 定义为 1），原表未提供参照组置信区间；不表示无心梗风险。"]
    else:
        lines += ["", "## 对应的人群关联", "",
                  f"表 3 该档人群 OR：{result['category_or']:.2f}；99% 置信区间：{result['category_or_ci_low']:.2f}–{result['category_or_ci_high']:.2f}。",
                  "参照为第1三分位组；使用男女合并、对全部所列风险因素及匹配因素调整后的关联。置信区间描述人群估计，不是个人风险区间。"]
    lines += ["", "研究为首次急性心梗病例对照设计，主要来自城市医院及其对照；不能从这张表得到未来某年限的绝对概率。",
              "测量应使用不易拉伸的软尺：腰围取肋缘与髂嵴之间最窄处的裸腹周长，臀围取臀部最宽处、薄衣外周长。两项来自同次测量。",
              "原研究排除妊娠及部分严重慢病；相关情境下只能把比值视为体形测量，不能据此推断疾病关联。"]
    if targets:
        target = scenario["targets"]
        lines += ["", "## 你指定的测量情景", "",
                  f"目标腰臀比：{target['waist_hip_ratio']:.6g}；{target['category']}。", SCENARIO_NOTE]
    lines += ["", f"边界: {BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
