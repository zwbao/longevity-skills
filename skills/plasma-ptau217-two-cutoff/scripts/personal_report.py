#!/usr/bin/env python3
"""One person's plasma pTau217 (Simoa ALZpath) against the printed cut-offs of
Martino-Adami et al., Nat Commun 2026 (doi:10.1038/s41467-026-76434-2).

Single cut-off: positive at or above it. Two cut-offs (Table 2 convention):
<= lower is negative, >= upper is positive, in between is indeterminate (grey zone).
Every constant is in presets.py with its locator; references/contract.md says how
each sentence of the report maps to the paper.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    ASHTON_SINGLE,
    ASHTON_TWO,
    ASSAY_ALIASES,
    BOUNDARY,
    COHORT_ZH,
    COHORTS,
    GMM,
    PRIMARY_COHORT,
    PRIMARY_PROBABILITY,
    PROBABILITIES,
    SINGLE_CUTOFF,
    TABLE2_PERFORMANCE_085,
    TWO_CUTOFFS,
)

TITLE = "血浆 pTau217 阳性 / 灰区 / 阴性分档"
CATEGORY_ZH = {"negative": "阴性", "indeterminate": "灰区（不确定）", "positive": "阳性"}
MARKER_ZH = {"ptau217": "pTau217", "ratio": "pTau217/Aβ42"}


def abnormal_probability(value: float, marker: str, cohort: str) -> float:
    """Posterior probability of the higher (abnormal) mixture class for one value.

    Two-class equal-variance Gaussian mixture on ln(value), parameters from [P]
    Supplementary Tables 2 and 3. Single cut-off = where this is 0.5; two cut-offs =
    where it is 1-t and t (t = 0.80, 0.85, 0.90).
    """
    g = GMM[(marker, cohort)]
    (m_low, m_high), var, (p_low, p_high) = g["means"], g["variance"], g["proportions"]
    x = math.log(value)
    logit = math.log(p_high / p_low) + ((x - m_low) ** 2 - (x - m_high) ** 2) / (2 * var)
    return 1 / (1 + math.exp(-logit))


def cutoffs_from_gmm(marker: str, cohort: str, probability: float | None = None) -> tuple:
    """Values (pg/mL or ratio) where the posterior equals 0.5, or 1-t and t. Used to check [P]'s printed cut-offs."""
    g = GMM[(marker, cohort)]
    (m_low, m_high), var, (p_low, p_high) = g["means"], g["variance"], g["proportions"]

    def at(logit: float) -> float:
        return math.exp((logit - math.log(p_high / p_low)) * var / (m_high - m_low) + (m_low + m_high) / 2)

    if probability is None:
        return (at(0.0),)
    t = math.log(probability / (1 - probability))
    return at(-t), at(t)


def single_status(value: float, cutoff: float) -> str:
    """[P] Table 2: single GMM cut-off printed as '>=0.63' (pTau217) and '>=0.12' (ratio)."""
    return "positive" if value >= cutoff else "negative"


def two_cutoff_category(value: float, lower: float, upper: float) -> str:
    """[P] Table 2: lower cut-off '<=', upper cut-off '>='; values in between are indeterminate."""
    if value <= lower:
        return "negative"
    if value >= upper:
        return "positive"
    return "indeterminate"


def ashton_two_category(value: float) -> str:
    """Ashton et al. (2024) pair as printed in [P] Table 2: '<0.40' negative, '>0.63' positive."""
    lower, upper = ASHTON_TWO
    if value < lower:
        return "negative"
    if value > upper:
        return "positive"
    return "indeterminate"


def assess(ptau217: float, abeta42: float | None, cohort: str = PRIMARY_COHORT,
           probability: float = PRIMARY_PROBABILITY) -> dict:
    out = {"ptau217": ptau217, "cohort": cohort, "probability": probability}
    lower, upper = TWO_CUTOFFS[("ptau217", cohort, probability)]
    out["ptau217_cutoffs"] = (lower, upper)
    out["ptau217_two"] = two_cutoff_category(ptau217, lower, upper)
    out["ptau217_single"] = single_status(ptau217, SINGLE_CUTOFF["ptau217"])
    out["ptau217_probability"] = abnormal_probability(ptau217, "ptau217", cohort)
    out["ashton_single"] = "positive" if ptau217 > ASHTON_SINGLE else "negative"
    out["ashton_two"] = ashton_two_category(ptau217)
    out["ratio"] = None
    out["ratio_two"] = out["ratio_single"] = None
    out["ratio_cutoffs"] = None
    if abeta42 is not None:
        ratio = ptau217 / abeta42
        rl, ru = TWO_CUTOFFS[("ratio", cohort, probability)]
        out.update(ratio=ratio, ratio_cutoffs=(rl, ru),
                   ratio_two=two_cutoff_category(ratio, rl, ru),
                   ratio_single=single_status(ratio, SINGLE_CUTOFF["ratio"]))
    return out


def parse_assay(raw: str | None) -> bool:
    return (raw or "").strip().lower() in ASSAY_ALIASES


def _fmt(x: float) -> str:
    """At least two decimals, as the paper prints cut-offs (0.50, 0.097)."""
    text = f"{x:.3f}".rstrip("0")
    return text if len(text.split(".")[1]) >= 2 else f"{x:.2f}"


def meaning(result: dict) -> list:
    cat = result["ptau217_two"]
    if cat == "negative":
        text = ("这次 pTau217 落在论文的阴性区（不高于下切点）。在论文巴西队列里，这一区的人大多数脑脊液淀粉样蛋白也是阴性，"
                "这是好消息；但它不排除以后变化，也不排除其他原因的认知问题。")
    elif cat == "positive":
        text = ("这次 pTau217 落在论文的阳性区（不低于上切点）。论文里这一区的人大多数脑脊液淀粉样蛋白异常。"
                "这不是诊断：请带着这份结果到神经内科或记忆门诊，由医生结合认知评估决定下一步。")
    else:
        text = ("这次 pTau217 落在两个切点之间的灰区。论文和血液标志物工作组的做法是：灰区的人不下阳性或阴性结论，"
                "由医生决定是否做脑脊液或 PET 等确认检查，或过一段时间复查。")
    lines = [text]
    lo, up = result["ptau217_cutoffs"]
    near = [c for c in (lo, up, SINGLE_CUTOFF["ptau217"]) if abs(result["ptau217"] - c) <= 0.02]
    if near:
        lines.append(f"你的数离切点 {', '.join(_fmt(c) for c in near)} pg/mL 不到 0.02。论文切点只印到两位小数，"
                     "化验本身也有约 6% 的批内变异（论文方法部分），这样的数在复查时可能落到另一侧。")
    return lines


def report_lines(result: dict, abeta42: float | None) -> list:
    cohort, prob = result["cohort"], result["probability"]
    lo, up = result["ptau217_cutoffs"]
    lines = [f"# {TITLE}", "", "## 输入", "",
             f"- 血浆 pTau217：{_fmt(result['ptau217'])} pg/mL（Simoa ALZpath）"]
    if abeta42 is not None:
        lines.append(f"- 血浆 Aβ42：{abeta42:g} pg/mL（Simoa Neurology 4-plex E）")
    lines += ["", "## 结果", "",
              f"切点组：{COHORT_ZH[cohort]}，后验概率阈值 ≥{prob:.2f}"
              + ("（论文推荐的主读法）" if (cohort, prob) == (PRIMARY_COHORT, PRIMARY_PROBABILITY) else "") + "。", "",
              f"- **pTau217 两切点分档：{CATEGORY_ZH[result['ptau217_two']]}**"
              f"（≤{_fmt(lo)} 阴性，≥{_fmt(up)} 阳性，之间为灰区）",
              f"- 按论文混合模型，这个数属于「异常分布」那一组的后验概率：{result['ptau217_probability']:.2f}"
              f"（两切点就是这个概率等于 {1 - prob:.2f} 和 {prob:.2f} 的位置；它不是患阿尔茨海默病的概率）",
              f"- pTau217 单切点：{CATEGORY_ZH[result['ptau217_single']]}（≥{SINGLE_CUTOFF['ptau217']} pg/mL 为阳性）"]
    if result["ratio"] is not None:
        rl, ru = result["ratio_cutoffs"]
        lines += [f"- pTau217/Aβ42 比值：{result['ratio']:.3f}",
                  f"- 比值两切点分档：{CATEGORY_ZH[result['ratio_two']]}（≤{_fmt(rl)} 阴性，≥{_fmt(ru)} 阳性）",
                  f"- 比值单切点：{CATEGORY_ZH[result['ratio_single']]}（≥{SINGLE_CUTOFF['ratio']} 为阳性）"]
    else:
        lines.append("- pTau217/Aβ42 比值：没有交 Aβ42，没有算。")
    lines.append(f"- 对照：论文表 2 引用的 Ashton 等（2024）北美和欧洲切点——单切点（>{ASHTON_SINGLE}）"
                 f"{CATEGORY_ZH[result['ashton_single']]}；两切点（<{_fmt(ASHTON_TWO[0])} 阴性，>{_fmt(ASHTON_TWO[1])} 阳性）"
                 f"{CATEGORY_ZH[result['ashton_two']]}。")
    lines += ["", "## 这意味着什么", ""] + meaning(result)
    if result["ratio"] is not None and result["ratio_two"] != result["ptau217_two"]:
        lines.append(f"pTau217 和比值的分档不一致。论文在巴西队列里比值的阴性预测值较低（表 2：≥0.85 时 "
                     f"{TABLE2_PERFORMANCE_085['ratio']['npv']}，pTau217 为 {TABLE2_PERFORMANCE_085['ptau217']['npv']}），"
                     "排除病理时更依赖 pTau217 本身；不一致时请交给医生判断。")
    perf = TABLE2_PERFORMANCE_085["ptau217"]
    lines += ["", "## 说明", "",
              f"- 论文队列里的表现（不是你的结果）：巴西队列 45 名同时有脑脊液的人中，pTau217 在 ≥0.85 两切点下"
              f"阳性预测值 {perf['ppv']}、阴性预测值 {perf['npv']}，{perf['indeterminate_pct']}% 落在灰区（表 2）。",
              "- 切点只适用于 Simoa 平台 ALZpath pTau217 试剂。Lumipulse、Elecsys、质谱等其他方法的 pTau217 数值尺度不同，不能套用。",
              "- 论文发现携带 APOE-ε4、体重指数偏低、肾功能（eGFR）偏低的人 pTau217 偏高；肾功能差时读数要更谨慎。",
              "- 研究对象是巴西和阿根廷 60 岁及以上的记忆门诊和社区人群，不是中国人群；切点在别的人群可能不同。",
              "- 本技能只按切点分档，不算患病概率，不看趋势。",
              "", f"边界: {BOUNDARY}"]
    return lines


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def write_report(out_dir: Path, measurements: Path | None, assay: str | None,
                 cohort: str = PRIMARY_COHORT, probability: float = PRIMARY_PROBABILITY) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = out_dir / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems = list(collected.problems)
    if not parse_assay(assay):
        problems.append(skillkit.Problem(
            "assay", "pTau217 检测方法", "missing" if not assay else "range",
            "需要确认 pTau217 是用 Simoa（Quanterix）平台 ALZpath 试剂测的（--assay simoa-alzpath）。"
            "论文切点只适用于这种方法；化验单上看不到方法时，请问检测机构。"
            + (f"收到的是「{assay}」，其他方法的数值尺度不同，不能套用这些切点。" if assay else "")))
    if cohort not in COHORTS:
        problems.append(skillkit.Problem("cohort", "切点队列", "range", f"--cohort 只能是 {' 或 '.join(COHORTS)}。"))
    if probability not in PROBABILITIES:
        problems.append(skillkit.Problem("probability", "后验概率阈值", "range",
                                         "--probability 只能是论文印出的 0.80、0.85 或 0.90。"))
    empty = {spec["key"]: None for spec in manifest["outputs"]}
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, empty)
        return path
    values = collected.values
    abeta42 = values.get("abeta42_pg_ml")
    result = assess(values["ptau217_pg_ml"], abeta42, cohort, probability)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(result, abeta42)) + "\n"), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {
        "ptau217_two_cutoff_category": result["ptau217_two"],
        "ptau217_single_cutoff_status": result["ptau217_single"],
        "ptau217_abnormal_class_probability": result["ptau217_probability"],
        "ptau217_abeta42_ratio": result["ratio"],
        "ratio_two_cutoff_category": result["ratio_two"],
        "ratio_single_cutoff_status": result["ratio_single"],
        "ashton_two_cutoff_category": result["ashton_two"],
        "cutoff_set": f"{cohort}_{probability:.2f}",
    })
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit: 血浆pTau217，可选血浆Aβ42")
    parser.add_argument("--assay", help="pTau217 检测方法，必须是 simoa-alzpath")
    parser.add_argument("--cohort", default=PRIMARY_COHORT, help="brazil（默认，有脑脊液验证）或 argentina")
    parser.add_argument("--probability", type=float, default=PRIMARY_PROBABILITY, help="0.80、0.85（默认）或 0.90")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.assay, args.cohort, args.probability)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
