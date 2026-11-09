#!/usr/bin/env python3
"""SARA total and item scores of one person with SCA27B, placed against the printed
results of Traschütz et al. (eBioMedicine 2026; 219 patients, 390 healthy controls).

- SARA total = sum of the eight items (Methods).
- Age-decade comparison with the printed SCA27B medians and healthy-control 90th percentiles.
- Cohort progression (overall 0.54, ambulatory 0.40 SARA points/year).
- Short-allele GAA repeats: Table S4 per-repeat contrast against a patient with the cohort
  median of 16 repeats, Table S5 item contrasts, and the printed >180 / >=250 group contrasts.

Constants and sources are in presets.py; the contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    AMBULATORY_GAIT_MAX,
    AUC_BY_DECADE,
    BOUNDARY,
    COHORT,
    CONTROL_MEDIAN,
    CONTROL_P90,
    PATHOGENIC_THRESHOLD,
    PROGRESSION_AMBULATORY,
    PROGRESSION_OVERALL,
    S4_TIME_X_SHORT,
    S5_ITEMS,
    SARA_ITEMS,
    SARA_MAX,
    SCA27B_DECADE_MEDIAN,
    SHORT_ALLELE_GE250,
    SHORT_ALLELE_GT180,
    SHORT_ALLELE_MEDIAN,
    SHORT_THRESHOLD_LOW,
)

TITLE = "SCA27B 共济失调评分（SARA）与队列进展对照"
ITEM_LABEL = {key: label for key, label, _ in SARA_ITEMS}


def sara_total(values: dict) -> float:
    """Methods: SARA total (0-40) is the sum of the eight item scores."""
    return sum(values[key] for key, _, _ in SARA_ITEMS)


def gait_stance_share_pct() -> float:
    """Discussion: share of the SARA total range made up by gait and stance."""
    maxima = {key: top for key, _, top in SARA_ITEMS}
    return (maxima["sara_gait_score"] + maxima["sara_stance_score"]) / SARA_MAX * 100


def decade(age: float | None) -> int | None:
    if age is None:
        return None
    return int(age // 10) * 10


def short_allele_contrast(short_repeats: float) -> tuple:
    """Table S4: difference in SARA points/year versus an otherwise identical patient
    with the cohort-median short allele (16 repeats). Returns (estimate, low, high)."""
    delta = short_repeats - SHORT_ALLELE_MEDIAN
    est, low, high = (coef * delta for coef in S4_TIME_X_SHORT)
    return (est, min(low, high), max(low, high))


def item_short_contrast(item: str, short_repeats: float) -> tuple:
    """Table S5: item-level difference in points/year versus 16 short-allele repeats."""
    delta = (short_repeats - SHORT_ALLELE_MEDIAN) / 100
    est, low, high = (coef * delta for coef in S5_ITEMS[item]["short_per100"])
    return (est, min(low, high), max(low, high))


def item_relative_acceleration_pct(item: str) -> float:
    """Results: item progression acceleration per 100 short-allele repeats, relative to
    that item's overall progression (Table S5 ratio)."""
    row = S5_ITEMS[item]
    return row["short_per100"][0] / row["overall"] * 100


def short_allele_group(short_repeats: float) -> str:
    if short_repeats >= PATHOGENIC_THRESHOLD:
        return "ge250"
    if short_repeats > SHORT_THRESHOLD_LOW:
        return "gt180"
    return "le180"


GROUP_ZH = {
    "le180": "180 个重复及以下",
    "gt180": "超过 180、不到 250 个重复（中间范围）",
    "ge250": "250 个重复及以上（双等位致病扩增）",
}


def assess(values: dict, age: float | None) -> dict:
    total = sara_total(values)
    ambulatory = values["sara_gait_score"] <= AMBULATORY_GAIT_MAX
    dec = decade(age)
    p90 = CONTROL_P90.get(dec) if dec is not None else None
    result = {
        "total": total,
        "ambulatory": ambulatory,
        "progression": PROGRESSION_AMBULATORY if ambulatory else PROGRESSION_OVERALL,
        "decade": dec,
        "control_p90": p90,
        "above_p90": None if p90 is None else total > p90,
        "margin_p90": None if p90 is None else total - p90,
        "cohort_median": SCA27B_DECADE_MEDIAN.get(dec) if dec is not None else None,
        "short": values.get("gaa_short_allele_repeats"),
        "long": values.get("gaa_long_allele_repeats"),
    }
    if result["short"] is not None:
        result["short_group"] = short_allele_group(result["short"])
        result["short_contrast"] = short_allele_contrast(result["short"])
    return result


def _ci(row: tuple, digits: int = 2) -> str:
    est, low, high = row
    return f"{est:+.{digits}f}（95% 置信区间 {low:+.{digits}f} 到 {high:+.{digits}f}）"


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def report_lines(result: dict, values: dict, age: float | None) -> list:
    lines = [f"# {TITLE}", "", "## 输入", ""]
    if age is not None:
        lines.append(f"- 评分时年龄 {age:g} 岁")
    lines.append("- SARA 各项：" + "，".join(
        f"{label} {values[key]:g}/{top}" for key, label, top in SARA_ITEMS))
    if result["long"] is not None:
        lines.append(f"- FGF14 GAA 重复数：较长等位 {result['long']:g}")
    if result["short"] is not None:
        lines.append(f"- FGF14 GAA 重复数：较短等位 {result['short']:g}")

    total = result["total"]
    lines += ["", "## 结果", "", f"- SARA 总分：{total:g} / {SARA_MAX}（八项相加）。"]
    floor_items = [ITEM_LABEL[key] for key, _, _ in SARA_ITEMS[2:] if values[key] <= 1]
    lines.append(f"- 步态 {values['sara_gait_score']:g}、站姿 {values['sara_stance_score']:g}；"
                 f"其余六项中 {len(floor_items)} 项 ≤1 分。论文里 SCA27B 的分数主要来自步态、站姿和跟膝胫，"
                 f"其余各项 79–94% 的患者 ≤1 分。")
    if result["ambulatory"]:
        lines.append(f"- 步态项 ≤{AMBULATORY_GAIT_MAX}，属于论文的“仍能独立行走”亚组；该亚组的队列平均进展是每年 "
                     f"{PROGRESSION_AMBULATORY[0]:.2f} 分（95% 置信区间 {PROGRESSION_AMBULATORY[1]:.2f}–{PROGRESSION_AMBULATORY[2]:.2f}）。")
    else:
        lines.append(f"- 步态项 >{AMBULATORY_GAIT_MAX}（需要间断扶持或助行），不属于“独立行走”亚组；全队列平均进展是每年 "
                     f"{PROGRESSION_OVERALL[0]:.2f} 分（95% 置信区间 {PROGRESSION_OVERALL[1]:.2f}–{PROGRESSION_OVERALL[2]:.2f}）。")
    lines.append(f"- 按全队列平均速度，5 年约增加 {PROGRESSION_OVERALL[0] * 5:.1f} 分；这是队列平均，不是你个人的预测。")

    lines += ["", "## 和同龄人对照", ""]
    dec = result["decade"]
    if dec is None:
        lines.append("- 没有给年龄，不做同龄对照。")
    else:
        span = f"{dec}–{dec + 10}岁"
        med = result["cohort_median"]
        if med is not None:
            lines.append(f"- 论文 SCA27B 患者 {span} 的 SARA 中位数 {med[0]:g}（四分位 {med[1]:g}–{med[2]:g}）。")
        if dec in CONTROL_MEDIAN:
            lines.append(f"- 同一年龄段健康对照的中位数 {CONTROL_MEDIAN[dec]:g}。")
        if result["control_p90"] is not None:
            relation = "高于" if result["above_p90"] else "不高于"
            lines.append(f"- 同年龄段健康对照的第 90 百分位是 {result['control_p90']:g} 分；你的总分{relation}它，"
                         f"差 {result['margin_p90']:+g} 分。论文把这个差看作对症治疗能让 SARA 改善的最大空间，"
                         f"年龄越大这个空间越小（区分患者和对照的曲线下面积 {AUC_BY_DECADE[dec]:.2f}）。")
        else:
            lines.append(f"- 论文只印出 50–80 岁三个年龄段的健康对照第 90 百分位，{span} 没有可对照的数。")

    lines += ["", "## 较短等位的 GAA 重复数", ""]
    if result["short"] is None:
        lines.append("- 没有给较短等位的重复数，不算这一部分。基因报告里通常写成两个数，例如 356/16，小的那个是较短等位。")
    else:
        short = result["short"]
        lines.append(f"- 分组：{GROUP_ZH[result['short_group']]}。")
        lines.append(f"- 补充表 S4 模型：和其他条件相同、较短等位为队列中位数 {SHORT_ALLELE_MEDIAN} 个重复的患者相比，"
                     f"每年 SARA 进展差 {_ci(result['short_contrast'])}分。")
        lines.append(f"- 论文另按切点分组（各自单独建模，不相加）：较短等位 >180 个重复的患者比 ≤180 的每年快 "
                     f"{SHORT_ALLELE_GT180[0]:.1f} 分（{SHORT_ALLELE_GT180[1]:.1f}–{SHORT_ALLELE_GT180[2]:.1f}）；"
                     f"≥250 的比 <250 的每年快 {SHORT_ALLELE_GE250[0]:.1f} 分（{SHORT_ALLELE_GE250[1]:.1f}–{SHORT_ALLELE_GE250[2]:.1f}）。"
                     "这两组在论文里分别只有 18 人和 6 人。")
        lines += ["", "| SARA 项目 | 队列平均每年进展 | 每 100 重复加快（相对队列平均） | 你相对 16 个重复的差（分/年） |", "| --- | --- | --- | --- |"]
        for key, label, _ in SARA_ITEMS:
            row = S5_ITEMS[key]
            est, low, high = item_short_contrast(key, short)
            lines.append(f"| {label} | {row['overall']:.3f} | {item_relative_acceleration_pct(key):.0f}% | "
                         f"{est:+.3f}（{low:+.3f} 到 {high:+.3f}） |")
        lines.append("")
        lines.append("- 这些是模型里的差值，不是你的绝对进展速度：补充表 S4 的协变量做过中心化，中心化用的数论文没有印出，所以本报告不把差值加到 0.54 上。")

    lines += ["", "## 说明", ""]
    if result["long"] is not None and result["long"] < PATHOGENIC_THRESHOLD:
        lines.append(f"- 较长等位 {result['long']:g} 个重复，低于论文入组标准（≥{PATHOGENIC_THRESHOLD}），论文人群不包括你这种情况，上面的对照只作参考。")
    if result["long"] is not None and result["short"] is not None and result["short"] > result["long"]:
        lines.append("- 较短等位的数比较长等位还大，可能两个数填反了；请对照基因报告再核对。")
    lines += [
        f"- 论文人群：{COHORT['centres']} 个欧洲和北美中心的 {COHORT['patients']} 名基因确诊 SCA27B 患者、{COHORT['assessments']} 次 SARA 评分，"
        f"其中 {COHORT['longitudinal']} 人有随访；健康对照 {COHORT['controls']} 人（{COHORT['controls_age'][0]}–{COHORT['controls_age'][1]} 岁）。",
        f"- 进展估计前排除了 {COHORT['excluded_comorbidity']} 名有其他疾病、多病共存或近期跌倒、手术干扰评分的患者；你如果有这类情况，分数可能高于病本身造成的程度。",
        "- 论文发现较长等位的重复数和起病年龄有关，但没有印出回归截距，所以本报告不估算起病年龄。",
        "- SARA 只能由医生按标准查体评分；自己估的分数不能用。",
        "",
        f"边界: {BOUNDARY}",
    ]
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
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    values = dict(collected.values)
    result = assess(values, age)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(result, values, age)) + "\n"), encoding="utf-8")
    contrast = result.get("short_contrast")
    skillkit.write_result(out_dir, manifest, {
        "sara_total_score": result["total"],
        "ambulatory_subgroup": "是" if result["ambulatory"] else "否",
        "cohort_progression_points_per_year": result["progression"][0],
        "control_p90_for_age_decade": result["control_p90"],
        "margin_over_control_p90": result["margin_p90"],
        "short_allele_group": GROUP_ZH[result["short_group"]] if result["short"] is not None else None,
        "short_allele_progression_difference": round(contrast[0], 3) if contrast else None,
    })
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit: 八项 SARA 分数（必填）, GAA 重复数（可选）")
    parser.add_argument("--age", type=float)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
