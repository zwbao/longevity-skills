#!/usr/bin/env python3
"""Low absolute handgrip strength by the EWGSOP2 and FNIH cut-offs, with the hazard ratios of
all-cause mortality printed for those groups in the MHAS cohort (Pérez-Sousa et al.,
GeroScience 2026, Supplementary Table S3), plus allometric HGS (HGS / height^2).

Constants and sources are in presets.py; the contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, COHORT, CRITERION_ZH, CUTOFFS_KG, LABELS, PER_SD, S3, S3_SAMPLE

TITLE = "握力切点与全因死亡风险比（墨西哥 MHAS 队列）"
CRITERIA = ("ewgsop2", "fnih")


def is_low(grip_kg: float, sex: str, criterion: str) -> bool:
    """Methods: low absolute HGS is strictly below the cut-off; at or above is the reference."""
    return grip_kg < CUTOFFS_KG[criterion][sex]


def allometric(grip_kg: float, height_cm: float) -> float:
    """Methods: allometric HGS = HGS (kg) / height^2 (m^2)."""
    metres = height_cm / 100.0
    return grip_kg / (metres * metres)


def hazard_ratio(grip_kg: float, sex: str, criterion: str) -> tuple:
    """Supplementary Table S3, Model 2 (fully adjusted) HR for the person's group; 1.0 for the reference group."""
    if is_low(grip_kg, sex, criterion):
        return S3[(criterion, sex)]["model2"]
    return (1.0, None, None)


def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man"}:
        return "male"
    if text in {"female", "f", "女", "woman"}:
        return "female"
    return None


def _hr_text(row: tuple) -> str:
    est, low, high = row
    if low is None:
        return "1（参照组）"
    return f"{est:.3f}（95% 置信区间 {low:.3f}–{high:.3f}）"


def assess(values: dict, sex: str) -> dict:
    grip = values["grip_kg"]
    out = {"grip": grip, "criteria": {}}
    for crit in CRITERIA:
        out["criteria"][crit] = {"low": is_low(grip, sex, crit), "cut": CUTOFFS_KG[crit][sex],
                                 "hr": hazard_ratio(grip, sex, crit)}
    height = values.get("height_cm")
    out["allometric"] = allometric(grip, height) if height is not None else None
    return out


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def report_lines(result: dict, values: dict, sex: str, age: float | None) -> list:
    who = "男" if sex == "male" else "女"
    lines = [f"# {TITLE}", "", "## 输入", ""]
    lines.append(f"- {who}" + (f"，{age:g} 岁" if age is not None else ""))
    lines.append(f"- 握力 {result['grip']:.1f} kg" + (f"，身高 {values['height_cm']:.1f} cm" if values.get("height_cm") is not None else ""))
    lines += ["", "## 结果", ""]
    for crit in CRITERIA:
        c = result["criteria"][crit]
        label = LABELS[0] if c["low"] else LABELS[1]
        lines.append(f"- {CRITERION_ZH[crit]}：{who}性切点 {c['cut']:g} kg，你的握力{label}。")
        if c["low"]:
            row = S3[(crit, sex)]
            m1 = row["model1"]
            lines.append(f"  - 论文补充表 S3：握力低于这个切点的{who}性，与达到切点者相比，全因死亡风险比（完全调整的模型 2）"
                         f"{_hr_text(row['model2'])}，p {row['p2']}；只调整年龄的模型 1 为 {_hr_text(m1)}。")
        else:
            lines.append("  - 你在论文的参照组（达到或高于切点），风险比按定义为 1。")
    if sex == "female":
        lines.append("- 女性两个标准的切点都是 16 kg，论文里两者的估计完全相同。")
    if result["allometric"] is not None:
        lines.append(f"- 身高校正握力（握力 ÷ 身高²）：{result['allometric']:.2f} kg/m²。"
                     "论文按男女分别的四分位分组，但四分位界值印在正文表 2、表 3，这次没能打开，所以这里只报数，不分组。")
    else:
        lines.append("- 身高校正握力：没给身高，没有算。")
    lines += ["", "## 这意味着什么", ""]
    any_low = any(c["low"] for c in result["criteria"].values())
    if not any_low:
        lines.append("握力达到两个国际肌少症标准的切点，在论文里属于参照组，这是好的信号。以后用同样的握力计、同一只手再测，前后才能比较。")
    elif sex == "male":
        lines.append("在论文的墨西哥男性里，握力低于切点的人完全调整后的全因死亡风险约为达到切点者的 2 倍多。"
                     "这是人群关联，不是你个人的死亡概率。握力偏低常和肌肉减少、营养不足或慢病有关，可以请医生评估肌肉、营养和慢病情况。")
    else:
        lines.append("在论文的墨西哥女性里，握力低于 16 kg 的人只调整年龄时死亡风险更高，但完全调整后置信区间跨过 1、没有统计学差异；"
                     "论文认为女性的结论不确定。握力偏低仍值得请医生评估肌肉、营养和慢病情况。")
    lines += ["", "## 说明", "",
              f"- 论文人群：墨西哥健康与老龄研究（MHAS）{COHORT['baseline_year']} 年第 3 轮做了握力测试的 {COHORT['n']} 名 {COHORT['min_age']} 岁及以上成人，"
              f"随访到 {COHORT['end_year']} 年，中位 {COHORT['followup_median_months']} 个月，死亡 {COHORT['deaths']} 人。"
              f"补充表 S3 的完整资料样本是男性 {S3_SAMPLE['male'][0]} 人（死亡 {S3_SAMPLE['male'][1]}）、女性 {S3_SAMPLE['female'][0]} 人（死亡 {S3_SAMPLE['female'][1]}）。",
              "- 测量方法：电子握力计，每只手测两次，取优势手的最大值（kg）。用别的握力计或别的手，读数可能不同。",
              "- 这些切点是肌少症共识里“肌力低”的定义，不是论文在这个队列里推导出的死亡阈值；论文也说没有评估它们作为筛查工具的准确性。",
              f"- 论文另报了按性别标准化后每增加 1 个标准差的风险比（男性绝对握力 {PER_SD[('absolute', 'male')][0]:.2f}，"
              f"男性身高校正握力 {PER_SD[('allometric', 'male')][0]:.2f}，女性身高校正握力 {PER_SD[('allometric', 'female')][0]:.2f}）；"
              "标准差印在表 1，这次没能打开，所以不换算你的标准化分数。"]
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
    if person_sex is None:
        problems.append(skillkit.Problem("sex", "性别", "missing" if not sex else "unit",
                                         "需要性别（男或女）：两个标准的握力切点男女不同。"))
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    values = dict(collected.values)
    result = assess(values, person_sex)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(result, values, person_sex, age)) + "\n"), encoding="utf-8")
    ew, fn = result["criteria"]["ewgsop2"], result["criteria"]["fnih"]
    skillkit.write_result(out_dir, manifest, {
        "ewgsop2_category": LABELS[0] if ew["low"] else LABELS[1],
        "ewgsop2_mortality_hr": ew["hr"][0],
        "fnih_category": LABELS[0] if fn["low"] else LABELS[1],
        "fnih_mortality_hr": fn["hr"][0],
        "allometric_hgs_kg_m2": round(result["allometric"], 3) if result["allometric"] is not None else None,
    })
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit: 握力（必填，kg）, 身高（可选，cm）")
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age, args.sex)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
