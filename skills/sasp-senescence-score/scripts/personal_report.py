#!/usr/bin/env python3
"""Personal SASP Score from 38 Olink NPX values (Zhao et al., Aging Cell 2026).

The score is the authors' pre-trained GAET model (shangshuzhao/sasp, commit
34d5f1b) run on one person's UKB-PPP-scale NPX values. It is not fine-tuned and
does not take age. Other platforms (Olink Target, Luminex, pg/mL) need the
cohort-level re-scaling or fine-tuning the paper describes, which one person's
sample cannot supply, so the script stops on them.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import skillkit
from paper_card import lines as paper_card_lines

import gaet
from presets import (
    BOUNDARY,
    CUTOFF,
    FLAG_ABS_Z,
    KEYS,
    PAPER,
    PROTEINS,
    SCALE_MEDIAN_ABS_Z,
    TITLE,
    UKB_MEAN_SD,
    UNITS_NPX,
)

KEY_TO_PROTEIN = {key: name for name, key in KEYS.items()}


def _is_npx(unit_text: str) -> bool:
    return skillkit.normalize_unit(unit_text).replace(" ", "") in UNITS_NPX


def prepare_rows(rows: Sequence[Dict[str, str]], manifest: dict) -> Tuple[List[Dict[str, str]], List[skillkit.Problem]]:
    """Check the unit column for the protein rows.

    Rows named by a protein must say NPX in the unit column (a row named by its
    key, gdf15_npx, already says it). An NPX row is renamed to its key with the
    unit cleared, so skillkit reads it in the key's own scale; any other unit is
    a problem, because a concentration cannot be converted to NPX.
    """
    if not rows:
        return [], []
    specs = skillkit.input_specs(manifest, "measurements")
    index = skillkit.alias_index(specs)
    fields = list(rows[0].keys())
    name_col = skillkit._column(fields, skillkit.NAME_COLUMNS)
    unit_col = skillkit._column(fields, skillkit.UNIT_COLUMNS)
    if name_col is None:
        return list(rows), []
    out: List[Dict[str, str]] = []
    problems: List[skillkit.Problem] = []
    for row in rows:
        raw_name = row.get(name_col, "")
        hit = None
        for variant in skillkit.name_variants(raw_name):
            if variant in index:
                hit = index[variant]
                break
        if hit is None:
            out.append(row)
            continue
        spec, by_key = hit
        unit_text = row.get(unit_col, "") if unit_col else ""
        label = spec.get("label_zh", spec["key"])
        if _is_npx(unit_text) or (by_key and not skillkit.normalize_unit(unit_text)):
            fixed = dict(row)
            fixed[name_col] = spec["key"]
            if unit_col:
                fixed[unit_col] = ""
            out.append(fixed)
        elif not skillkit.normalize_unit(unit_text):
            problems.append(skillkit.Problem(
                spec["key"], label, "unit_missing",
                f"{raw_name} 没有写单位。这个模型只读 Olink NPX（log2 标度），请在单位列写 NPX；"
                "化验单上的 pg/mL、ng/mL 浓度不能换成 NPX。",
            ))
        else:
            problems.append(skillkit.Problem(
                spec["key"], label, "unit",
                f"{raw_name} 的单位是 {unit_text}。这个模型只读 Olink Explore 的 NPX 值（log2 标度），"
                "浓度单位不能换算成 NPX，所以不能计算。",
            ))
    return out, problems


def z_scores(values: Dict[str, float]) -> Dict[str, float]:
    out = {}
    for name in PROTEINS:
        mean, sd = UKB_MEAN_SD[name]
        out[name] = (values[KEYS[name]] - mean) / sd
    return out


def scale_problem(z: Dict[str, float]) -> Optional[skillkit.Problem]:
    median_abs = statistics.median(abs(v) for v in z.values())
    if median_abs > SCALE_MEDIAN_ABS_Z:
        return skillkit.Problem(
            "", "NPX 标度", "scale",
            f"38 个蛋白离 UK Biobank（UKB-PPP）平均值的中位距离是 {median_abs:.1f} 个标准差，"
            f"超过 {SCALE_MEDIAN_ABS_Z:g}。数据看起来不在 UKB-PPP 的 NPX 标度上（例如 Olink Target 96、"
            "未经同样标准化的 NPX、线性 NPX 或浓度）。论文对别的平台要先在整组人里重新标定或微调模型，"
            "一个人的样本做不到，所以这次不计算。",
        )
    return None


def group_text(score: float) -> str:
    return f"高于 {CUTOFF:g}" if score > CUTOFF else f"不高于 {CUTOFF:g}"


def render(score: float, z: Dict[str, float]) -> str:
    high = score > CUTOFF
    lines = [f"# {TITLE}", "", *paper_card_lines(), ""]
    lines += [
        "## 你的结果",
        "",
        f"- SASP 评分：**{score:.1f}**",
        f"- 论文分组：**{group_text(score)}**（论文把 > {CUTOFF:g} 作为高分组）",
        "",
        "这个分数由论文作者公开的预训练模型，直接用你的 38 个蛋白 NPX 值算出。模型训练时用实足年龄做引导，"
        "所以分数的数值和年龄在同一个量级，但它不是年龄，也没有用到你的年龄。",
        "",
    ]
    if high:
        lines += [
            f"论文里，{CUTOFF:g} 是训练样本中基线没有主要慢病（癌症、糖尿病、心衰、心梗、卒中、慢阻肺、痴呆）的人的第 90 百分位。"
            "你的分数在这个切点之上。在 UK Biobank 测试样本里，高分组随访期间的死亡和多种慢病发生率较高；"
            "这是人群比较，不是对你个人的预测。",
        ]
    else:
        lines += [
            f"论文里，{CUTOFF:g} 是训练样本中基线没有主要慢病的人的第 90 百分位。你的分数没有超过这个切点。"
            "这不表示没有风险，只说明不在论文定义的高分组里。",
        ]
    lines += ["", "## 离 UK Biobank 平均水平较远的蛋白", ""]
    far = sorted(((name, value) for name, value in z.items() if abs(value) >= FLAG_ABS_Z), key=lambda item: -abs(item[1]))
    if far:
        lines.append(f"下面这些蛋白离 UKB-PPP 人群平均值至少 {FLAG_ABS_Z:g} 个标准差。这是描述，不是模型对分数的贡献：")
        lines.append("")
        for name, value in far:
            lines.append(f"- {name}：{'高于' if value > 0 else '低于'}平均 {abs(value):.1f} 个标准差")
    else:
        lines.append(f"38 个蛋白都在 UKB-PPP 人群平均值 {FLAG_ABS_Z:g} 个标准差以内。")
    lines += [
        "",
        "## 论文里的人群数字（不是你的结果）",
        "",
        f"- UK Biobank 测试样本 {PAPER['n_test']} 人：SASP 评分与实足年龄的相关 rho = {PAPER['rho_age_test']:.2f}；"
        f"调整年龄、性别等因素后，每高 1 个标准差，死亡风险比 {PAPER['hr_mortality_per_sd']:.2f}"
        f"（95% CI {PAPER['hr_mortality_ci'][0]:.2f}–{PAPER['hr_mortality_ci'][1]:.2f}），平均随访 {PAPER['mean_follow_up_years']} 年。",
        f"- MEDEX 试验 {PAPER['n_medex']} 名 65–84 岁老人：用 Luminex 平台、并在该队列微调后计算；不运动组 18 个月里评分上升，运动组没有显著上升，"
        "但运动与否和时间的交互作用不显著。",
        "",
        "## 这个分数算不了什么",
        "",
        "- 不是年龄，不算“衰老加速”；论文没有定义分数减年龄的差值。",
        "- 不按蛋白给出贡献（论文的 SHAP 排名是人群平均，需要训练数据，这里没有）。",
        "- 只适用于 UKB-PPP 标度的 Olink Explore NPX；其他平台论文要整组微调，一个人做不到。",
        "",
        f"边界: {BOUNDARY}",
    ]
    return "\n".join(lines) + "\n"


def write_report(out_dir: Path, measurements: Optional[Path]) -> Path:
    manifest = skillkit.load_manifest(__file__)
    rows = skillkit.read_rows(measurements) if measurements is not None else []
    rows, problems = prepare_rows(rows, manifest)
    collected = skillkit.collect_measurements(rows, manifest)
    flagged = {p.key for p in problems}
    problems += [p for p in collected.problems if p.key not in flagged]
    if problems:
        skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        raise SystemExit(skillkit.EXIT_INPUT_PROBLEM)
    z = z_scores(collected.values)
    problem = scale_problem(z)
    if problem:
        skillkit.write_problems(out_dir, [problem], TITLE, BOUNDARY)
        raise SystemExit(skillkit.EXIT_INPUT_PROBLEM)
    score = gaet.sasp_score([collected.values[KEYS[name]] for name in PROTEINS])
    out_dir.mkdir(parents=True, exist_ok=True)
    report = out_dir / "report.md"
    report.write_text(render(score, z), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {
        "sasp_score": score,
        "sasp_group": "high" if score > CUTOFF else "low",
        "proteins_far_from_ukb": float(sum(1 for value in z.values() if abs(value) >= FLAG_ABS_Z)),
    })
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="SASP Score (GAET) from 38 Olink Explore NPX values")
    parser.add_argument("--proteins", type=Path, help="CSV: marker,value,unit (unit NPX)")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        path = write_report(args.out, args.proteins)
    except SystemExit as exc:
        if exc.code == skillkit.EXIT_INPUT_PROBLEM:
            sys.stdout.write(str(args.out / "report.md") + "\n")
        raise
    sys.stdout.write(str(path) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
