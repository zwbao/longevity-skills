#!/usr/bin/env python3
"""Calf circumference change between two measurements, grouped with the cut points of
Zhang et al. (JAMA Netw Open 2026; CLHLS 2018-2021), with the printed odds ratios of
incident falls for that group versus no decrease (Tables 2-4).

Constants and sources are in presets.py; the contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    ABS_CUTS_CM,
    ABS_LABELS,
    BOUNDARY,
    COHORT,
    PER_10PCT,
    PER_1CM,
    REL_CUTS_PCT,
    REL_LABELS,
    STRATUM_ZH,
    TABLE2_MODEL4,
    TABLE3_MODEL4,
    TABLE4_ABS,
    TABLE4_REL,
)

TITLE = "小腿围变化分档与跌倒比值比（CLHLS 队列）"
_EPS = 1e-9


def absolute_change(baseline_cm: float, followup_cm: float) -> float:
    """Methods: absolute CC change = CC2021 - CC2018 (cm)."""
    return followup_cm - baseline_cm


def relative_change(baseline_cm: float, followup_cm: float) -> float:
    """Methods: relative CC change = (CC2021 - CC2018) / CC2018 x 100 (%)."""
    return (followup_cm - baseline_cm) / baseline_cm * 100


def _group(decrease: float, cuts: tuple) -> int:
    """0 = no decrease (stable or increased); then < cuts[0], cuts[0] to < cuts[1], >= cuts[1]."""
    if decrease <= _EPS:
        return 0
    if decrease < cuts[0] - _EPS:
        return 1
    if decrease < cuts[1] - _EPS:
        return 2
    return 3


def absolute_group(change_cm: float) -> int:
    return _group(-change_cm, ABS_CUTS_CM)


def relative_group(change_pct: float) -> int:
    return _group(-change_pct, REL_CUTS_PCT)


def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man"}:
        return "male"
    if text in {"female", "f", "女", "woman"}:
        return "female"
    return None


def strata(sex: str | None, age: float | None) -> list:
    keys = []
    if sex:
        keys.append(sex)
    if age is not None:
        keys.append("under80" if age < 80 else "80plus")
    return keys


def assess(values: dict) -> dict:
    base, follow = values["calf_baseline_cm"], values["calf_followup_cm"]
    change_cm = absolute_change(base, follow)
    change_pct = relative_change(base, follow)
    a, r = absolute_group(change_cm), relative_group(change_pct)
    return {
        "change_cm": change_cm,
        "change_pct": change_pct,
        "abs_group": a,
        "rel_group": r,
        "abs_or": TABLE2_MODEL4[a],
        "rel_or": TABLE3_MODEL4[r],
    }


def _or_text(row: tuple) -> str:
    est, low, high = row
    if low is None:
        return "1（参照组）"
    return f"{est:.2f}（95% 置信区间 {low:.2f}–{high:.2f}）"


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def report_lines(result: dict, values: dict, sex: str | None, age: float | None) -> list:
    lines = [f"# {TITLE}", "", "## 输入", ""]
    who = []
    if sex:
        who.append("男" if sex == "male" else "女")
    if age is not None:
        who.append(f"{age:g} 岁")
    if who:
        lines.append("- " + "，".join(who))
    lines.append(f"- 第一次小腿围 {values['calf_baseline_cm']:.1f} cm，第二次 {values['calf_followup_cm']:.1f} cm")
    a, r = result["abs_group"], result["rel_group"]
    lines += ["", "## 结果", "",
              f"- 绝对变化：{result['change_cm']:+.1f} cm，分档：{ABS_LABELS[a]}。",
              f"- 相对变化：{result['change_pct']:+.1f}%，分档：{REL_LABELS[r]}。",
              f"- 论文表 2（模型 4）里，绝对分档“{ABS_LABELS[a]}”的跌倒比值比：{_or_text(result['abs_or'])}。",
              f"- 论文表 3（模型 4）里，相对分档“{REL_LABELS[r]}”的跌倒比值比：{_or_text(result['rel_or'])}。"]
    for key in strata(sex, age):
        lines.append(f"- 表 4 {STRATUM_ZH[key]}：绝对分档比值比 {_or_text(TABLE4_ABS[key][a])}；相对分档比值比 {_or_text(TABLE4_REL[key][r])}。")
    lines += ["", "## 这意味着什么", ""]
    if a == 0 and r == 0:
        lines.append("两次之间小腿围没有减少，在论文里属于参照组，这是好的信号。以后按同样姿势、同一条腿再量，前后才能比较。")
    else:
        lines.append("比值比大于 1 表示在论文人群里，这一档的人比小腿围没减少的人更常报告跌倒；置信区间跨过 1 的那一档，论文里没有统计学差异。"
                     "这是人群关联，不是你个人的跌倒概率。")
        lines.append("小腿围变细可能来自肌肉减少，也可能来自脂肪或水肿变化。如果三年左右明显变细、或近期跌过倒，可以请医生评估肌肉力量、平衡和用药。")
    lines += ["", "## 说明", "",
              f"- 论文人群：CLHLS 2018 和 2021 两轮，{COHORT['n']} 名 {COHORT['min_age']} 岁及以上社区老人，平均 {COHORT['mean_age']} 岁，"
              f"中位随访 {COHORT['followup_median_years']} 年，{COHORT['falls']} 人（{COHORT['falls_pct']}%）报告新发跌倒。",
              f"- 论文另报了连续变量：每减少 1 cm 比值比 {PER_1CM[0]:.2f}（{PER_1CM[1]:.2f}–{PER_1CM[2]:.2f}），每减少 10% 比值比 {PER_10PCT[0]:.2f}（{PER_10PCT[1]:.2f}–{PER_10PCT[2]:.2f}）；这里只按分档查表，不外推连续值。",
              "- 测量方法：坐位、双脚平放、膝约 90°，量右小腿，精确到 0.1 cm；两次要同一条腿、同样姿势。",
              "- 论文两次测量间隔约 3 年；你的两次间隔差得多时，这些比值比不一定适用。"]
    if age is not None and age < COHORT["min_age"]:
        lines.append(f"- 你的年龄 {age:g} 岁，不在论文人群（{COHORT['min_age']} 岁及以上）内。")
    lines += ["", f"边界: {BOUNDARY}"]
    return lines


def write_report(out_dir: Path, measurements: Path | None, age: float | None, sex: str | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = out_dir / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems = list(collected.problems)
    if age is not None:
        problems += skillkit.check_scalar(manifest, "age", age)
    person_sex = parse_sex(sex)
    if sex and person_sex is None:
        problems.append(skillkit.Problem("sex", "性别", "unit", f"性别写的是“{sex}”，请写男或女，或者不填。"))
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    values = dict(collected.values)
    result = assess(values)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(result, values, person_sex, age)) + "\n"), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {
        "calf_change_cm": round(result["change_cm"], 2),
        "calf_change_pct": round(result["change_pct"], 2),
        "absolute_category": ABS_LABELS[result["abs_group"]],
        "absolute_or": result["abs_or"][0],
        "relative_category": REL_LABELS[result["rel_group"]],
        "relative_or": result["rel_or"][0],
    })
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit: 基线小腿围, 随访小腿围（都必填，cm）")
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age, args.sex)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
