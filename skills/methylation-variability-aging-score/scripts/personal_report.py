#!/usr/bin/env python3
"""Integrated DMP-DVP epigenetic score (Vishnyakova et al., J Gerontol A 2026).

For each model (EPIC model of Supplementary Table S15; 450K-restricted model of the
authors' repository) and as in eScores.R:

    M        = log2(beta) - log2(1 - beta)
    s_k      = intercept_k + sum(w_k,cpg * M_cpg)      for k in FI, CF, PF
    raw      = cox_FI * s_FI + cox_CF * s_CF + cox_PF * s_PF
    score    = (raw - mean_bio) / sd_bio * sd_age + mean_age

A model is computed only when every one of its CpGs is supplied; a missing CpG is
never filled with 0 (eScores.R does that; this skill does not). If neither model is
complete, or any value is unusable, the report lists why and the exit code is 3.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, HEALTH_SCORES, MODELS, load_model, model_cpgs

TITLE = "甲基化水平与变异性整合评分"
MISSING_SHOWN = 15


def m_value(beta: float) -> float:
    return math.log2(beta) - math.log2(1.0 - beta)


def score(model: dict, betas: dict[str, float]) -> float:
    m = {cpg: m_value(betas[cpg]) for cpg in model_cpgs(model)}
    raw = 0.0
    for key in HEALTH_SCORES:
        sub = model["intercept"][key] + sum(w * m[cpg] for cpg, w in model["weights"][key].items())
        raw += model["cox"][key] * sub
    t = model["transform"]
    return (raw - t["mean_bio"]) / t["sd_bio"] * t["sd_age"] + t["mean_age"]


def load_meds(path: Path | None) -> list[str]:
    if path is None:
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")]


def lab_lines(path: Path | None) -> list[str]:
    lines = ["## 体检", ""]
    rows: list[dict[str, str]] = []
    if path is not None and path.read_text(encoding="utf-8-sig").strip():
        rows = skillkit.read_rows(path)
    if not rows:
        lines.append("没有提供体检。体检不增删方法算出的结果。")
        return lines
    lines.append("下面照录体检数值。体检不增删方法算出的结果。")
    for row in rows:
        item = row.get("项目") or row.get("item") or row.get("name")
        value = row.get("结果") or row.get("value") or row.get("result")
        unit = row.get("单位") or row.get("unit") or ""
        if item and value:
            lines.append(f"- {item} {value}{' ' + unit if unit else ''}")
    return lines


def medication_lines(meds: list[str]) -> list[str]:
    lines = ["## 你正在使用的药", ""]
    if not meds:
        lines.append("没有提供现用药。")
        return lines
    for name in meds:
        lines.append(f"- {name}：这个方法不涉及任何药物，不能据此停，也不能据此开始。")
    return lines


def _paper_card_after_title(text: str) -> str:
    rows = text.splitlines()
    rest = rows[1:]
    while rest and rest[0] == "":
        rest = rest[1:]
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rest]) + "\n"


def _boundary_problems(collected: skillkit.Collected, manifest: dict) -> list[skillkit.Problem]:
    """Betas of exactly 0 or 1 pass the [0, 1] range but have no M-value."""
    problems = []
    for key, value in collected.values.items():
        if value <= 0.0 or value >= 1.0:
            spec = skillkit.spec_by_key(manifest, key)
            problems.append(skillkit.Problem(
                key, key, "range",
                f"{key} 的 β 值是 {value:g}。模型先把 β 值换成 M 值（log2(β/(1−β))），β 等于 0 或 1 时算不出来；"
                f"请核对芯片数据。{spec.get('note_zh', '')}",
            ))
    return problems


def _missing_text(name: str, missing: list[str], total: int) -> str:
    shown = "、".join(missing[:MISSING_SHOWN])
    more = f" 等 {len(missing)} 个" if len(missing) > MISSING_SHOWN else ""
    return f"{MODELS[name]['label']}需要 {total} 个位点，缺 {len(missing)} 个：{shown}{more}。"


def render(results: dict, missing: dict, totals: dict, age: float | None, unmatched: int,
           meds: list[str], labs: Path | None) -> str:
    lines = [f"# {TITLE}", "", "## 你的结果", ""]
    for name in ("epic", "450k"):
        label = MODELS[name]["label"]
        if results[name] is None:
            lines.append(f"- {label}：没有算。{_missing_text(name, missing[name], totals[name])}缺的位点不用 0 或别的数代替。")
        else:
            lines.append(f"- {label}：{results[name]:.1f}（用上全部 {totals[name]} 个位点）")
    if unmatched:
        lines.append(f"- 另有 {unmatched} 行不是这两个模型的位点，没有用到。")
    lines += [
        "",
        "## 怎么读这个数",
        "",
        "- 论文先用甲基化位点分别预测衰弱指数、认知功能和身体功能三项健康分（位点来自甲基化水平差异 DMP 和甲基化变异性差异 DVP），"
        "再按全因死亡的 Cox 模型权重合成一个分数，最后按加拿大老龄化纵向研究（CLSA）训练集的年龄均值和标准差换成“年”的刻度。",
        "- 所以这个数是你在 CLSA 训练人群里的相对位置，写成年龄的样子；它不是生物年龄，数越高表示甲基化特征越接近健康分更差的人。",
        "- 论文的最终指标是“表观年龄偏差”：把这个分数对实足年龄回归后的残差。回归的截距和斜率没有在正文、补充表或代码仓库里公布，"
        "所以报告不算偏差，也不说你比同龄人老还是年轻。",
    ]
    if age is not None:
        lines.append(f"- 你给的实足年龄是 {age:g} 岁，只作对照显示；分数和年龄直接相减不是论文的偏差。")
    lines += [
        "- 论文训练时用的是去除免疫细胞比例影响后的 M 值；作者公开的计算脚本直接把 β 值换成 M 值，这里照脚本做。"
        "不同实验室的芯片处理和标准化不同，分数会有偏移。",
        "- 两个模型的位点和权重不同，数值不能互相比较；EPIC 模型是论文主分析用的，450K 限定模型是论文在巴尔的摩老龄化纵向研究（BLSA）外部验证时用的。",
        "",
        *medication_lines(meds),
        "",
        *lab_lines(labs),
        "",
        f"边界: {BOUNDARY}",
    ]
    return "\n".join(lines) + "\n"


def report(out: Path, measurements: Path | None, age: float | None, meds: Path | None, labs: Path | None) -> int:
    out.mkdir(parents=True, exist_ok=True)
    for stale in ("problems.json", "report.md", "result.json"):
        if (out / stale).exists():
            (out / stale).unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems = [p for p in collected.problems if p.kind != "missing"]
    problems += [p for p in skillkit.check_scalar(manifest, "age", age) if p.kind != "missing"]
    problems += _boundary_problems(collected, manifest)
    empty = {spec["key"]: None for spec in manifest["outputs"]}
    if problems:
        path = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        path.write_text(_paper_card_after_title(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out, manifest, empty)
        return skillkit.EXIT_INPUT_PROBLEM

    results: dict[str, float | None] = {}
    missing: dict[str, list[str]] = {}
    totals: dict[str, int] = {}
    for name in MODELS:
        model = load_model(name)
        cpgs = model_cpgs(model)
        totals[name] = len(cpgs)
        missing[name] = [cpg for cpg in cpgs if cpg not in collected.values]
        results[name] = None if missing[name] else score(model, collected.values)

    if all(value is None for value in results.values()):
        closer = min(MODELS, key=lambda name: len(missing[name]))
        site_problems = [skillkit.Problem(cpg, cpg, "missing", f"缺少 {cpg} 的 β 值。") for cpg in missing[closer]]
        skillkit.write_problems(out, site_problems, TITLE, BOUNDARY)
        text = "\n".join([
            f"# {TITLE}", "", "## 输入没有通过检查", "",
            "这次没有计算。两个模型都要交齐全部位点：",
            *(f"- {_missing_text(name, missing[name], totals[name])}" for name in ("epic", "450k")),
            "",
            f"out/problems.json 逐个列出离交齐更近的那个模型（{MODELS[closer]['label']}）还缺的位点。缺的项不要用别的数代替。",
            "", f"边界: {BOUNDARY}",
        ])
        (out / "report.md").write_text(_paper_card_after_title(text), encoding="utf-8")
        skillkit.write_result(out, manifest, empty)
        return skillkit.EXIT_INPUT_PROBLEM

    text = render(results, missing, totals, age, len(collected.unmatched), load_meds(meds), labs)
    (out / "report.md").write_text(_paper_card_after_title(text), encoding="utf-8")
    skillkit.write_result(out, manifest, {MODELS[name]["output"]: results[name] for name in MODELS})
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit: one row per CpG, beta value")
    parser.add_argument("--age", type=float, help="chronological age in years; shown for context only")
    parser.add_argument("--medications", type=Path)
    parser.add_argument("--labs", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    code = report(args.out, args.measurements, args.age, args.medications, args.labs)
    print(args.out / "report.md")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
