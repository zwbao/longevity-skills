#!/usr/bin/env python3
"""Two-year MCI-to-dementia conversion probability from six cognitive scores.

Model: the authors' published cognitive-scores XGBoost model (Simkhada et al.,
GeroScience 2026), exported to data/cog_model.json and evaluated with the
standard library in cog_model.py. The DEM-COG-MRI headline model is not
computed. Checkup labs and current medicines do not change the result.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import skillkit
from paper_card import lines as paper_card_lines

import cog_model
from presets import (
    ADAS13_MINUS_ADAS11_MAX,
    BOUNDARY,
    CDR_GLOBAL_VALUES,
    COG_ONLY_ABLATION_DROP_PCT,
    FEATURES,
    HEADLINE_TEST_BALANCED_ACCURACY_PCT,
    TABLE_S2_MEAN_SD,
    TITLE,
    WINDOW_MONTHS,
)

KEYS = [key for key, _col, _label, _unit in FEATURES]
LABELS = {key: label for key, _col, label, _unit in FEATURES}


def consistency_problems(values: Dict[str, float]) -> List[skillkit.Problem]:
    """Checks the scales themselves impose; each stops the computation."""
    problems: List[skillkit.Problem] = []
    cdr = values.get("cdr_global_score")
    if cdr is not None and not any(abs(cdr - allowed) < 1e-9 for allowed in CDR_GLOBAL_VALUES):
        problems.append(skillkit.Problem(
            "cdr_global_score", LABELS["cdr_global_score"], "value",
            f"CDR 全局分读成 {cdr:g}。它只能是 0、0.5、1、2 或 3；请核对是不是把 CDR-SB（各项之和）填到了这一行。",
        ))
    sb = values.get("cdr_sb_score")
    if sb is not None and abs(sb * 2 - round(sb * 2)) > 1e-9:
        problems.append(skillkit.Problem(
            "cdr_sb_score", LABELS["cdr_sb_score"], "value",
            f"CDR-SB 读成 {sb:g}。六个方框每项只能是 0、0.5、1、2、3，合计必须是 0.5 的倍数。",
        ))
    mmse = values.get("mmse_score")
    if mmse is not None and abs(mmse - round(mmse)) > 1e-9:
        problems.append(skillkit.Problem(
            "mmse_score", LABELS["mmse_score"], "value",
            f"MMSE 读成 {mmse:g}。MMSE 总分是 0–30 的整数。",
        ))
    faq = values.get("faq_score")
    if faq is not None and abs(faq - round(faq)) > 1e-9:
        problems.append(skillkit.Problem(
            "faq_score", LABELS["faq_score"], "value",
            f"FAQ 读成 {faq:g}。十个条目每项 0–3 分，合计是整数。",
        ))
    a11 = values.get("adas11_score")
    a13 = values.get("adas13_score")
    if a11 is not None and a13 is not None:
        gap = a13 - a11
        if gap < -1e-9 or gap > ADAS13_MINUS_ADAS11_MAX + 1e-9:
            problems.append(skillkit.Problem(
                "adas13_score", LABELS["adas13_score"], "value",
                f"ADAS-Cog 13（{a13:g}）减 ADAS-Cog 11（{a11:g}）是 {gap:g}。13 项版本比 11 项多延迟回忆（0–10）和数字划消（0–5），"
                f"差值应在 0 到 {ADAS13_MINUS_ADAS11_MAX:g} 之间；请核对两行是否填反或填成了别的版本。",
            ))
    return problems


def collect_inputs(scores: Optional[Path]) -> Tuple[Dict[str, float], List[skillkit.Problem], List[skillkit.Problem]]:
    """Returns values, stopping problems, and missing-item problems."""
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(scores, manifest)
    stopping = [p for p in collected.problems if p.kind != "missing"]
    missing = [p for p in collected.problems if p.kind == "missing"]
    stopping += consistency_problems(collected.values)
    return collected.values, stopping, missing


def unusual_lines(values: Dict[str, float]) -> List[str]:
    """Scores more than 2 SD from the paper's dynamic-dataset mean (Table S2)."""
    out = []
    for key in KEYS:
        mean, sd = TABLE_S2_MEAN_SD[key]
        value = values[key]
        if abs(value - mean) > 2 * sd:
            out.append(
                f"- {LABELS[key]} {value:g}：离论文训练人群的均值 {mean:g}（标准差 {sd:g}，补充表 S2）超过 2 个标准差。"
                "模型在这一带见过的人少，结果更不确定。"
            )
    return out


def read_list(path: Optional[Path]) -> List[str]:
    if path is None:
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]


def read_labs(path: Optional[Path]) -> List[Tuple[str, str, str]]:
    if path is None:
        return []
    text = path.read_text(encoding="utf-8-sig", errors="replace").strip()
    if not text:
        return []
    rows = list(csv.reader(text.splitlines()))
    head = [cell.strip().casefold() for cell in rows[0]]
    if head and head[0] in ("项目", "item", "name", "marker"):
        rows = rows[1:]
    out = []
    for row in rows:
        cells = [cell.strip() for cell in row] + ["", "", ""]
        if cells[0]:
            out.append((cells[0], cells[1], cells[2]))
    return out


def context_lines(medications: Sequence[str], labs: Sequence[Tuple[str, str, str]]) -> List[str]:
    lines = ["## 你正在使用的药", ""]
    if not medications:
        lines.append("没有提供现用药。")
    for name in medications:
        lines.append(f"- {name}：药物不是这个模型的输入，不改变上面的概率。不能据此开始或停止。")
    lines += ["", "## 体检", ""]
    if not labs:
        lines.append("没有提供体检。体检不增删方法算出的结果。")
    else:
        lines.append("下面照录体检数值。体检不是这个模型的输入，不增删方法算出的结果。")
        for item, value, unit in labs:
            lines.append(f"- {item} {value}{(' ' + unit) if unit else ''}".rstrip())
    return lines


def render_report(
    values: Dict[str, float],
    missing: Sequence[skillkit.Problem],
    medications: Sequence[str],
    labs: Sequence[Tuple[str, str, str]],
) -> Tuple[str, Dict[str, object]]:
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 输入", ""]
    for key in KEYS:
        shown = f"{values[key]:g}" if key in values else "没有提供"
        lines.append(f"- {LABELS[key]}：{shown}")
    outputs: Dict[str, object] = {
        "conversion_probability_pct": None,
        "model_group": None,
        "model_threshold_pct": None,
    }
    lines += ["", "## 结果", ""]
    if missing:
        names = "、".join(p.label for p in missing)
        lines.append(
            f"六项量表没有齐（缺：{names}），所以没有转化概率。模型要求六项同一次就诊测得；缺的项不要用别的数代替。"
        )
    else:
        ordered = [values[key] for key in KEYS]
        folds = cog_model.fold_probabilities(ordered)
        prob = sum(folds) / len(folds)
        cut = cog_model.threshold()
        above = prob >= cut
        group = "高于模型切点（模型归入两年内转化组）" if above else "低于模型切点（模型归入两年内稳定组）"
        outputs.update({
            "conversion_probability_pct": 100 * prob,
            "model_group": "above_threshold" if above else "below_threshold",
            "model_threshold_pct": 100 * cut,
        })
        lines.append(
            f"按论文作者公开的六项认知量表模型，{WINDOW_MONTHS} 个月内由轻度认知障碍转为痴呆的校准概率是 {100 * prob:.1f}%。"
        )
        lines.append(
            f"这个模型自己的判别切点是 {100 * cut:.1f}%，你的概率{group}。"
        )
        lines.append(
            f"模型由五个校准折平均得到，五折各自给出 {100 * min(folds):.1f}%–{100 * max(folds):.1f}%。"
        )
        lines.append(
            "这个概率只适用于已经由医生诊断为轻度认知障碍的人；认知正常或已经诊断痴呆的人，模型没有定义。"
        )
        unusual = unusual_lines(values)
        if unusual:
            lines += ["", "训练人群里少见的数：", *unusual]
    lines += [
        "",
        "## 队列里的表现（不是你的结果）",
        "",
        f"论文的独立测试集（ADNI）上，包含磁共振的完整多模态模型平衡准确率 {HEADLINE_TEST_BALANCED_ACCURACY_PCT:g}%；"
        f"只用这六项量表时，平衡准确率低 {COG_ONLY_ABLATION_DROP_PCT:g} 个百分点。这些是人群上的分类表现，不是这个人的准确率。",
        "",
        "## 没有计算的",
        "",
        "- 论文的主模型（人口学与 APOE ε4、六项量表、323 项 FreeSurfer 结构磁共振指标）没有计算：它要 ADNI 同一流程测出的脑区体积、皮层厚度和面积，个人报告无法提供。",
        "- SHAP 和置换重要性是队列层面的特征排名，不对个人计算。",
        "",
        *context_lines(medications, labs),
        "",
        f"边界: {BOUNDARY}",
    ]
    return "\n".join(lines) + "\n", outputs


def write_report(
    out_dir: Path,
    scores: Optional[Path],
    medications: Optional[Path] = None,
    labs: Optional[Path] = None,
) -> Tuple[int, Path]:
    out_dir = Path(out_dir)
    manifest = skillkit.load_manifest(__file__)
    values, stopping, missing = collect_inputs(scores)
    if stopping:
        report = skillkit.write_problems(out_dir, stopping, TITLE, BOUNDARY)
        skillkit.write_result(out_dir, manifest, {
            "conversion_probability_pct": None, "model_group": None, "model_threshold_pct": None,
        })
        return skillkit.EXIT_INPUT_PROBLEM, report
    text, outputs = render_report(values, missing, read_list(medications), read_labs(labs))
    out_dir.mkdir(parents=True, exist_ok=True)
    report = out_dir / "report.md"
    report.write_text(text, encoding="utf-8")
    skillkit.write_result(out_dir, manifest, outputs)
    if missing:
        skillkit.write_problems(out_dir, missing, TITLE, BOUNDARY)
        report.write_text(text, encoding="utf-8")
        return skillkit.EXIT_INPUT_PROBLEM, report
    return 0, report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--scores", type=Path, help="CSV: marker,value,unit — six cognitive and functional scores")
    parser.add_argument("--medications", type=Path, help="one medicine per line (context only)")
    parser.add_argument("--labs", type=Path, help="checkup CSV 项目,结果,单位 (context only)")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    code, report = write_report(args.out, args.scores, args.medications, args.labs)
    print(report)
    return code


if __name__ == "__main__":
    sys.exit(main())
