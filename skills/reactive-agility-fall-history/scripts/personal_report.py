#!/usr/bin/env python3
"""SKILLCOURT Random Star Run and stepping reaction times compared with the exploratory
cutoffs of Giesche et al. (GeroScience 2026) for older adults with vs without a
history of falls.

Constants and sources are in presets.py; the contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import ADJUSTED, BOUNDARY, COHORT, CUTOFFS, SIDE_ABOVE, SIDE_BELOW, TUG_ADJUSTED_AUC

TITLE = "SKILLCOURT 反应敏捷成绩与跌倒史切点对照"
_EPS = 1e-9


def at_or_above(value_s: float, cutoff_s: float) -> bool:
    """Longer times lie on the fall-history side; a value equal to the cutoff counts as at/above."""
    return value_s >= cutoff_s - _EPS


def assess(values: dict) -> dict:
    rows = {}
    for key, spec in CUTOFFS.items():
        if key in values:
            rows[key] = at_or_above(values[key], spec["cutoff_s"])
    return rows


def _fmt_s(value: float) -> str:
    return f"{value:.2f}" if value < 10 else f"{value:.1f}"


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def report_lines(result: dict, values: dict, age: float | None) -> list:
    lines = [f"# {TITLE}", "", "## 输入", ""]
    if age is not None:
        lines.append(f"- 年龄 {age:g} 岁")
    for key, spec in CUTOFFS.items():
        if key in values:
            lines.append(f"- {spec['label_zh']}：{_fmt_s(values[key])} 秒")
    lines += ["", "## 结果", ""]
    for key, spec in CUTOFFS.items():
        if key not in result:
            lines.append(f"- {spec['label_zh']}：没有提供，不对照。")
            continue
        side = SIDE_ABOVE if result[key] else SIDE_BELOW
        detail = f"未调整 ROC 的 AUC {spec['unadjusted_auc']:.2f}"
        if spec["sensitivity_pct"] is not None:
            detail += f"，灵敏度 {spec['sensitivity_pct']}%，特异度 {spec['specificity_pct']}%"
        lines.append(f"- {spec['label_zh']} {_fmt_s(values[key])} 秒，论文切点 {spec['cutoff_s']:g} 秒：{side}。（该切点在论文人群里：{detail}）")
    n_above = sum(1 for v in result.values() if v)
    lines += ["", "## 这意味着什么", ""]
    if n_above == 0:
        lines.append("你提供的成绩都低于论文切点，也就是更像论文里没有跌倒史的那一组。这不保证不会跌倒：切点在论文人群里也会漏掉不少有跌倒史的人。")
    else:
        lines.append(f"你有 {n_above} 项成绩达到或超过论文切点，也就是在论文人群里，有跌倒史的人更常落在这一侧。"
                     "这不说明你一定跌倒过或将来会跌倒：同一切点下，没有跌倒史的人也有相当一部分落在这一侧。")
        lines.append("如果近期跌过倒、走路不稳或担心跌倒，可以请医生或康复治疗师做一次正式的跌倒风险评估（平衡、肌力、视力、用药等）。")
    rsr = ADJUSTED["random_star_run_s"]
    lines += ["", "## 说明", "",
              f"- 论文人群：德国和卢森堡两个中心 {COHORT['n']} 名 {COHORT['min_age']} 岁及以上社区老人（{COHORT['fallers']} 人过去 12 个月有跌倒史，{COHORT['non_fallers']} 人没有），平均 {COHORT['mean_age']} 岁；"
              f"随机星形跑分析样本 {COHORT['rsr_n']} 人。跌倒史是回顾性自报。",
              "- 三个切点都来自不含年龄、中心等协变量的 ROC 分析，论文称为探索性切点，没有在另一批人里验证过。",
              f"- 调整年龄和中心后，随机星形跑每慢 1 个标准差，有跌倒史的比值比 {rsr['or_per_sd']}，模型 AUC {rsr['auc']}，高于起立行走测试（TUG）的 {TUG_ADJUSTED_AUC}；"
              "这些模型用预测概率，本技能没有读到模型的截距和系数（表 5–7），所以这里不算个人概率。",
              "- 只适用于在 SKILLCOURT 上按论文流程测的成绩：随机星形跑做 3 次取最快一次；踏步反应取 30 次平均。其他敏捷测试、坐着按键的电脑反应时不能套用这些切点。",
              "- 论文的两个中心场地设置略有不同；作者之一为 SKILLCOURT 公司提供咨询（论文已声明）。"]
    if age is not None and age < COHORT["min_age"]:
        lines.append(f"- 你的年龄 {age:g} 岁，不在论文人群（{COHORT['min_age']} 岁及以上）内，切点不一定适用。")
    lines += ["", f"边界: {BOUNDARY}"]
    return lines


def write_report(out_dir: Path, measurements: Path | None, age: float | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = out_dir / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems = list(collected.problems)
    if age is not None:
        problems += skillkit.check_scalar(manifest, "age", age)
    if not problems and not any(key in collected.values for key in CUTOFFS):
        problems.append(skillkit.Problem(
            "random_star_run_s", "随机星形跑完成时间（SKILLCOURT）", "missing",
            "没有读到任何一项 SKILLCOURT 成绩。请至少提供随机星形跑完成时间、简单踏步反应时间或选择踏步反应时间中的一项（秒）。"))
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    values = dict(collected.values)
    result = assess(values)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(result, values, age)) + "\n"), encoding="utf-8")
    outputs = {spec["output"]: None for spec in CUTOFFS.values()}
    for key, above in result.items():
        outputs[CUTOFFS[key]["output"]] = SIDE_ABOVE if above else SIDE_BELOW
    outputs["tests_at_or_above_cutoff"] = sum(1 for v in result.values() if v)
    skillkit.write_result(out_dir, manifest, outputs)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path,
                        help="CSV item,value,unit: 随机星形跑、简单踏步反应、选择踏步反应（秒，至少一项）")
    parser.add_argument("--age", type=float)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
