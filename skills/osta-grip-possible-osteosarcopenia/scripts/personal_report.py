#!/usr/bin/env python3
"""Possible osteosarcopenia (OSTA index plus AWGS 2019 handgrip) as defined by
Koh et al. (J Gerontol A 2026; TARGET cohort, Singapore).

Constants and sources are in presets.py; the contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BOUNDARY,
    COGNITION_OR,
    COGNITIVE_LOSS_PCT,
    COHORT,
    GRIP_CUT_KG,
    IC_BETA,
    MINIMOCA_INTERACTION,
    MINIMOCA_JOINT,
    OSTA_FACTOR,
    OSTA_HIGH_BELOW,
    OSTA_LABELS,
    OSTA_POSSIBLE_OSTEOPOROSIS_MAX,
    SCREENING,
    TABLE_S12,
)

TITLE = "可能骨肌减少症筛查（OSTA 加握力，新加坡 TARGET 队列）"
_EPS = 1e-9


def osta_index(weight_kg: float, age_years: float) -> float:
    """Methods: OSTA = 0.2 x [body weight (kg) - age (years)], not truncated."""
    return OSTA_FACTOR * (weight_kg - age_years)


def osta_risk(index: float) -> str:
    """high < -4; moderate -4 to -1 (inclusive); low > -1."""
    if index < OSTA_HIGH_BELOW - _EPS:
        return "high"
    if index <= OSTA_POSSIBLE_OSTEOPOROSIS_MAX + _EPS:
        return "moderate"
    return "low"


def possible_osteoporosis(index: float) -> bool:
    return osta_risk(index) in ("high", "moderate")


def possible_sarcopenia(grip_kg: float, sex: str) -> bool:
    """AWGS 2019: handgrip < 18 kg (women) or < 28 kg (men)."""
    return grip_kg < GRIP_CUT_KG[sex] - _EPS


def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man", "男性"}:
        return "male"
    if text in {"female", "f", "女", "woman", "女性"}:
        return "female"
    return None


def assess(weight_kg: float, grip_kg: float, age: float, sex: str) -> dict:
    index = osta_index(weight_kg, age)
    osteo = possible_osteoporosis(index)
    sarco = possible_sarcopenia(grip_kg, sex)
    return {
        "osta_index": index,
        "osta_risk": osta_risk(index),
        "possible_osteoporosis": osteo,
        "possible_sarcopenia": sarco,
        "possible_osteosarcopenia": osteo and sarco,
    }


def _yes(flag: bool) -> str:
    return "是" if flag else "否"


def _ci(row: tuple) -> str:
    return f"{row[0]:.2f}（95% 置信区间 {row[1]:.2f} 到 {row[2]:.2f}）"


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def report_lines(result: dict, weight_kg: float, grip_kg: float, age: float, sex: str) -> list:
    cut = GRIP_CUT_KG[sex]
    sex_zh = "男" if sex == "male" else "女"
    lines = [f"# {TITLE}", "", "## 输入", "",
             f"- {sex_zh}，{age:g} 岁，体重 {weight_kg:g} kg，优势手握力 {grip_kg:g} kg", "",
             "## 结果", "",
             f"- OSTA 指数 = 0.2 ×（{weight_kg:g} − {age:g}）= {result['osta_index']:.2f}，{OSTA_LABELS[result['osta_risk']]}。",
             f"- 可能骨质疏松（OSTA ≤ −1）：{_yes(result['possible_osteoporosis'])}。",
             f"- 可能肌少症（握力低于{sex_zh}性切点 {cut:g} kg）：{_yes(result['possible_sarcopenia'])}。",
             f"- 可能骨肌减少症（两项都是）：{_yes(result['possible_osteosarcopenia'])}。",
             "", "## 这意味着什么", ""]
    if result["possible_osteosarcopenia"]:
        lines.append("你同时符合论文的“可能骨质疏松”和“可能肌少症”两条，属于论文里的“可能骨肌减少症”组。"
                     "这是筛查阳性，不是诊断：论文在做过 DXA 的人里核对，筛查阳性的人约一半被 DXA 确认。"
                     "可以请医生评估骨密度（DXA）和肌肉量、肌力，并留意平衡和跌倒。")
    elif result["possible_osteoporosis"] or result["possible_sarcopenia"]:
        which = "可能骨质疏松" if result["possible_osteoporosis"] else "可能肌少症"
        lines.append(f"你只符合“{which}”一条，不属于论文的“可能骨肌减少症”组。"
                     "论文写明单独的骨质疏松或肌少症与内在能力、6 个月认知都没有显著关联，所以下面的认知关联不适用于你；"
                     "但单项筛查阳性本身仍值得和医生讨论（骨密度或肌力评估）。")
    else:
        lines.append("两条都不符合，按论文的定义不属于“可能骨肌减少症”。筛查阴性的人在论文里 DXA 确认没有骨肌减少症的比例很高，"
                     "但这仍不是骨密度检查的替代。")
    lines += ["", "## 论文人群里的关联（不是你的个人结果）", "",
              f"- 论文人群：新加坡 TARGET 队列 {COHORT['n']} 名 {COHORT['min_age']} 岁及以上社区老人，平均 {COHORT['mean_age']} 岁；"
              f"{COHORT['prevalence_pct']}% 符合可能骨肌减少症。",
              f"- 调整协变量后，可能骨肌减少症与内在能力总分（0–5）较低相关：β = {_ci(IC_BETA)}（表 3）。",
              f"- 基线认知能力完好的比值比 {_ci(COGNITION_OR)}（补充表 11）；"
              f"可能骨肌减少症组 {COGNITIVE_LOSS_PCT['possible']}% 有认知能力下降，另一组 {COGNITIVE_LOSS_PCT['no']}%（表 2）。",
              f"- 6 个月时简版 MoCA（0–15 分）：在基线认知已下降的人里，可能骨肌减少症多降 {abs(MINIMOCA_INTERACTION[0]):.2f} 分"
              f"（95% 置信区间 {MINIMOCA_INTERACTION[1]:.2f} 到 {MINIMOCA_INTERACTION[2]:.2f}）；"
              f"与两者都没有的人相比合计低 {abs(MINIMOCA_JOINT):.2f} 分（表 4）。基线认知完好的人里没有显著差别。",
              f"- 补充表 12 预测均值：认知下降组 {TABLE_S12[('loss', 'no')][0]:.2f} 对 {TABLE_S12[('loss', 'possible')][0]:.2f} 分；"
              f"认知完好组 {TABLE_S12[('intact', 'no')][0]:.2f} 对 {TABLE_S12[('intact', 'possible')][0]:.2f} 分。",
              "", "## 说明", "",
              f"- 筛查表现（补充表 3，{SCREENING['n']} 名做过 DXA 和握力的人，对照 DXA 骨密度、肌肉量和握力定义）："
              f"灵敏度 {SCREENING['sensitivity']}%，特异度 {SCREENING['specificity']}%，阳性预测值 {SCREENING['ppv']}%，"
              f"阴性预测值 {SCREENING['npv']}%，ROC 曲线下面积 {SCREENING['roc']}。",
              "- 握力：论文用弹簧式握力计，每只手量两次，取优势手两次的平均，精确到 0.5 kg；没有做 5 次起坐试验。",
              "- OSTA 原本为亚洲绝经后女性设计，论文对男女都用同一公式和切点；论文没有对指数取整。"]
    if age < COHORT["min_age"]:
        lines.append(f"- 你的年龄 {age:g} 岁，不在论文人群（{COHORT['min_age']} 岁及以上）内，分类不一定适用。")
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
    problems += skillkit.check_scalar(manifest, "age", age)
    person_sex = parse_sex(sex)
    if not sex:
        problems.append(skillkit.Problem("sex", "性别", "missing", "缺少性别。握力切点男女不同（男 28 kg、女 18 kg），请写男或女。"))
    elif person_sex is None:
        problems.append(skillkit.Problem("sex", "性别", "unit", f"性别写的是“{sex}”，请写男或女。"))
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    weight, grip = collected.values["weight_kg"], collected.values["grip_strength_kg"]
    result = assess(weight, grip, float(age), person_sex)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(result, weight, grip, float(age), person_sex)) + "\n"),
                    encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {
        "osta_index": round(result["osta_index"], 2),
        "osta_risk_category": OSTA_LABELS[result["osta_risk"]],
        "possible_osteoporosis": _yes(result["possible_osteoporosis"]),
        "possible_sarcopenia": _yes(result["possible_sarcopenia"]),
        "possible_osteosarcopenia": _yes(result["possible_osteosarcopenia"]),
    })
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit: 体重 (kg), 握力 (kg, 优势手两次平均)")
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age, args.sex)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
