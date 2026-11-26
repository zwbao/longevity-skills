#!/usr/bin/env python3
"""Table 2 exposure-duration scenario; standard library only."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, INPUT_UNITS, LOG_RR_AT_FIVE_YEARS,
                     LOG_RR_PER_ADDITIONAL_YEAR, REFERENCE_YEARS)

TITLE = "LDL 降低与相对心血管风险：情景估计"


def log_rr_per_mmol(years):
    return LOG_RR_AT_FIVE_YEARS + (years - REFERENCE_YEARS) * LOG_RR_PER_ADDITIONAL_YEAR


def compute(values):
    log_rr = values["ldl_reduction_mmol_l"] * log_rr_per_mmol(values["duration_years"])
    return {"relative_risk_reduction_pct": -100 * math.expm1(log_rr),
            "relative_risk": math.exp(log_rr)}


def levers(values, targets):
    current = compute(values)
    rr = current["relative_risk"]
    slopes = {
        "ldl_reduction_mmol_l": -100 * rr * log_rr_per_mmol(values["duration_years"]),
        "duration_years": -100 * rr * values["ldl_reduction_mmol_l"] * LOG_RR_PER_ADDITIONAL_YEAR,
    }
    specs = {x["key"]: x for x in skillkit.load_manifest(__file__)["inputs"]}
    result = {
        "schema": "longevity-levers/1", "model": "ldl-exposure-risk-reduction",
        "model_zh": "LDL 降幅与暴露时间（Ference 等，2017，表2）",
        "current": {**current, "values": values},
        "sensitivity": [{"key": k, "label_zh": specs[k]["label_zh"], "unit": INPUT_UNITS[k],
                         "value": values[k], "rrr_percentage_points_per_unit": slopes[k]}
                        for k in INPUT_UNITS],
        "levers": [],
        "note_zh": "仅比较用户指定情景；持续时间不是可立即改变的生物指标。目标由用户提供，不据此推荐LDL目标或用药。",
    }
    for key, target in targets.items():
        moved = compute({**values, key: target})
        result["levers"].append({
            "key": key, "label_zh": specs[key]["label_zh"], "unit": INPUT_UNITS[key],
            "from": values[key], "to": target, **moved,
            "rrr_delta_percentage_points": moved["relative_risk_reduction_pct"] - current["relative_risk_reduction_pct"],
        })
    if targets:
        together = compute({**values, **targets})
        result["targets"] = {
            "values": targets, **together,
            "rrr_delta_percentage_points": together["relative_risk_reduction_pct"] - current["relative_risk_reduction_pct"],
        }
    return result


def collect(path, manifest, partial=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, UnicodeError, ValueError) as exc:
        return {}, [skillkit.Problem("file", "输入文件", "file", f"无法读取输入文件：{exc}")]
    problems = [p for p in collected.problems if not (partial and p.kind == "missing")]
    for name in collected.unmatched:
        problems.append(skillkit.Problem("unknown", name, "unknown", f"无法识别项目“{name}”。请提供LDL-C绝对下降量与持续年数；单次LDL-C浓度不能当作下降量。"))
    if partial and not collected.values and not problems:
        problems.append(skillkit.Problem("targets", "目标情景", "missing", "目标文件中没有可计算的项目。"))
    return collected.values, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    # A failed rerun must never expose a previous successful person's result.
    for filename in ("result.json", "levers.json", "problems.json"):
        (args.out / filename).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, partial=True)
        problems.extend(target_problems)
    if problems:
        report = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        content = report.read_text(encoding="utf-8").split("\n", 1)[1]
        report.write_text("\n".join([f"# {TITLE}", "", *paper_card_lines(), "", content]), encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM

    result = compute(values)
    scenarios = levers(values, targets)
    text = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的情景", "",
            f"LDL-C绝对下降量：{values['ldl_reduction_mmol_l']:g} mmol/L；持续：{values['duration_years']:g} 年。",
            f"相对于没有这一下降的情景，模型估计相对风险下降约 {result['relative_risk_reduction_pct']:.1f}%，相对风险为 {result['relative_risk']:.3f}。",
            "这是相对变化，不是你的发病概率，也不是绝对风险下降的百分点。", "",
            "持续时间超过5年的结果包含长期外推，依赖长期遗传证据与短期试验的整合；中间年数按论文脚注计算。",
            "输入应表示持续维持的下降量；两次化验的偶然波动不能证明已经维持多年。",
            "公式假设LDL-C与LDL颗粒数下降一致；糖尿病、代谢综合征或高甘油三酯时两者可能不一致。",
            "表2部分单元格以及表3、4与脚注有差异。本报告使用表2脚注公式，不输出绝对风险或NNT。"]
    if targets:
        text += ["", "## 你提供的目标情景", "",
                 f"同时代入所给目标后，相对风险下降约 {scenarios['targets']['relative_risk_reduction_pct']:.1f}%。",
                 f"相较当前情景，相对风险下降幅度变化 {scenarios['targets']['rrr_delta_percentage_points']:+.1f} 个百分点。",
                 "目标属于假设情景，不是本报告推荐的治疗目标；持续年数的增加不能立即实现。"]
    text += ["", f"边界：{BOUNDARY}", ""]
    (args.out / "report.md").write_text("\n".join(text), encoding="utf-8")
    skillkit.write_result(args.out, manifest, result)
    (args.out / "levers.json").write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
