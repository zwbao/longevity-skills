#!/usr/bin/env python3
"""Read the printed dose-response table; never fit, interpolate or extrapolate."""

import argparse
import bisect
import csv
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, MEASURES, PROTOCOL, TITLE


def load_table():
    tables = {key: [] for key in MEASURES}
    path = Path(__file__).resolve().parents[1] / "data/dose_response.csv"
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            tables[row["metric"]].append({
                "dose": float(row["dose"]), "hr": float(row["hr"]),
                "ci_low": float(row["ci_low"]) if row["ci_low"] else None,
                "ci_high": float(row["ci_high"]) if row["ci_high"] else None,
                "reference": row["reference"] == "true",
            })
    return tables


TABLE = load_table()


def lookup(key, value):
    rows = TABLE[key]
    if not math.isfinite(value) or not rows[0]["dose"] <= value <= rows[-1]["dose"]:
        raise ValueError("超出补充表 5 印出的范围，不外推。")
    doses = [r["dose"] for r in rows]
    index = bisect.bisect_left(doses, value)
    exact = doses[index] == value
    lower = rows[index] if exact else rows[index - 1]
    upper = rows[index]
    return {
        "metric": key, "value": value, "mode": "exact" if exact else "bracket",
        "hr": lower["hr"] if exact else None,
        "ci_low": lower["ci_low"] if exact else None,
        "ci_high": lower["ci_high"] if exact else None,
        "reference_dose": next(r["dose"] for r in rows if r["reference"]),
        "lower": lower, "upper": upper,
    }


def problem(key, message, kind="input"):
    return skillkit.Problem(key, MEASURES.get(key, {}).get("label", key), kind, message)


def collect(path, manifest):
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, csv.Error) as exc:
        return {}, [problem("measurements", f"无法读取测量表：{exc}。请提供 marker,value,unit 格式的 CSV。")]
    issues = list(result.problems)
    if result.unmatched:
        issues.append(problem("measurements", "未识别项目：" + "、".join(result.unmatched) + "。请使用支持的活动名称。"))
    if len(result.values) != 1:
        issues.append(problem("measurements", "每次需要且只接受一种活动或久坐测量；多种指标须分别运行，不能合并风险。", "missing" if not result.values else "input"))
    return result.values, issues


def levers(current, target=None):
    key = current["metric"]
    # A derivative of the unpublished spline cannot be obtained from this table.
    # Display neighbouring *printed* points as the available sensitivity evidence.
    rows = TABLE[key]
    if current["mode"] == "exact":
        index = next(i for i, r in enumerate(rows) if r["dose"] == current["value"])
        neighbours = rows[max(0, index - 1):min(len(rows), index + 2)]
    else:
        neighbours = [current["lower"], current["upper"]]
    result = {
        "schema": "longevity-levers/1", "model": "accelerometry_mortality_table5",
        "model_zh": "加速度计活动及久坐的队列关联查表", "current": current,
        "sensitivity": [{"key": key, "unit": MEASURES[key]["unit"],
                         "value": current["value"], "hr_per_unit": None,
                         "adjacent_printed_rows": neighbours,
                         "note_zh": "未公布样条系数，局部导数不可计算；这里只列相邻印出值，不能用于误差传播。"}],
        "levers": [], "note_zh": BOUNDARY + "单一暴露逐项比较，不合成多种活动的总风险。",
    }
    if target is not None:
        delta = target["hr"] - current["hr"] if current["hr"] is not None and target["hr"] is not None else None
        result["targets"] = target
        result["levers"] = [{"key": key, "unit": MEASURES[key]["unit"],
                             "from": current["value"], "to": target["value"],
                             "hr_delta": delta, "target": target,
                             "note_zh": "同一参照下两行 HR 的算术差；不是个人干预效果。非表格点不计算差值。"}]
    return result


def result_values(current):
    values = {"metric": current["metric"], "exposure": current["value"],
              "exposure_unit": MEASURES[current["metric"]]["display_unit"],
              "lookup_mode": current["mode"], "hazard_ratio": current["hr"],
              "ci_low": current["ci_low"], "ci_high": current["ci_high"],
              "reference_dose": current["reference_dose"]}
    for side in ("lower", "upper"):
        for name in ("dose", "hr", "ci_low", "ci_high"):
            values[f"{side}_{name}"] = current[side][name]
    return values


def row_text(row, unit):
    ci = "参照行；论文没有给出置信区间" if row["reference"] else f"95% CI {row['ci_low']:.2f}–{row['ci_high']:.2f}"
    return f"{row['dose']:g} {unit}：HR = {row['hr']:.2f}（{ci}）"


def lookup_lines(current):
    unit = MEASURES[current["metric"]]["display_unit"]
    if current["mode"] == "exact":
        return [row_text(current["lower"], unit)]
    return ["输入位于两条印出剂量之间，只列两条原始结果；没有为输入值估算 HR，也不能把两行结果当作置信区间。",
            "- " + row_text(current["lower"], unit), "- " + row_text(current["upper"], unit)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age")
    parser.add_argument("--sex")
    parser.add_argument("--device")
    parser.add_argument("--protocol")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("result.json", "problems.json", "levers.json", "report.md"):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, issues = collect(args.measurements, manifest)
    try:
        age = float(args.age) if args.age is not None else None
        issues += skillkit.check_scalar(manifest, "age", age)
    except ValueError:
        issues.append(problem("age", "年龄需要填写年数。", "parse"))
    if args.sex is not None and args.sex not in ("male", "female", "男", "女"):
        issues.append(problem("sex", "性别如填写，请使用 male、female、男或女；性别不会改变查表结果。"))
    if args.device not in ("actigraph", "actical"):
        issues.append(problem("device", "需要确认设备为躯干部位佩戴的 actigraph 或 actical；手腕设备、自报时长、步数不能换算。", "missing" if args.device is None else "input"))
    if args.protocol != PROTOCOL:
        issues.append(problem("protocol", "需核实垂直轴 60 秒窗口、至少 4 个有效日且每天佩戴至少 10 小时、原文非佩戴识别及强度阈值；确认后才可填写 --protocol vertical-60s-harmonised。", "missing" if args.protocol is None else "input"))
    if args.device == "actical" and set(values) != {"mvpa_min_day"}:
        issues.append(problem("device", "补表剂量反应分析仅在 MVPA 纳入 Actical；其他指标只接受 Actigraph。"))
    wanted = {}
    if args.targets is not None:
        wanted, target_issues = collect(args.targets, manifest)
        issues += target_issues
        if set(wanted) != set(values):
            issues.append(problem("targets", "目标必须是本次同一种测量，使用同一设备定义和每日平均口径。"))
    if issues:
        path = skillkit.write_problems(args.out, issues, TITLE, BOUNDARY)
        text = path.read_text(encoding="utf-8")
        first, rest = text.split("\n", 1)
        path.write_text(first + "\n\n" + "\n".join(paper_card_lines()) + "\n" + rest, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM
    key, value = next(iter(values.items()))
    current = lookup(key, value)
    target = lookup(key, wanted[key]) if wanted else None
    spec = MEASURES[key]
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的查表结果", "",
             f"{spec['label']}：{value:g} {spec['display_unit']}。设备：{args.device}。年龄：{age:g} 岁。",
             "已声明符合论文处理协议；本程序读取处理后的每日平均值，不处理原始加速度信号。",
             f"本列的印出参照为 {current['reference_dose']:g} {spec['display_unit']}，参照 HR 为 1。",
             *lookup_lines(current), "",
             "HR 是研究人群相对参照的全因死亡瞬时危险比，置信区间反映关联估计的不确定性；这不是个人死亡概率的区间。",
             "研究来自美国和西欧的中老年人；对其他人群的适用性未验证。年龄只用于检查适用范围，性别不参与重新校准。"]
    if key == "mvpa_min_day":
        lines.append("使用补表 5 印出的 0 分钟参照；补表 3 的最低四分位中位数为 1.5 分钟，两者不混用。")
    if key == "sedentary_h_day":
        lines.append("久坐 12 小时行的置信上限按补表 5 的 3.82；正文该处写作 3.83。")
    if target is not None:
        lines += ["", "## 你提供的目标情景", "", *lookup_lines(target),
                  "这是目标值对应的队列关联，不代表达到目标就会获得相应风险变化。"]
    lines += ["", "边界: " + BOUNDARY]
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(args.out, manifest, result_values(current))
    (args.out / "levers.json").write_text(json.dumps(levers(current, target), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
