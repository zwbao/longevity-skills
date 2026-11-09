#!/usr/bin/env python3
"""Cumulative BMI and waist-circumference exposure (cBMI, cWC) over three measurement
waves, computed with the cut points of Yu et al. (GeroScience 2026; Rugao Longitudinal
Ageing Study), with the baseline BMI group and the printed cohort context.

Constants and sources are in presets.py; the contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BMI_LABELS,
    BMI_OBESITY_FROM,
    BMI_REF,
    BMI_UNDERWEIGHT_BELOW,
    BOUNDARY,
    COHORT,
    PAPER_WAVES,
    TABLE_S2,
    TABLE_S4_BMI_KDM,
    WC_REF_CM,
    WC_REF_FEMALE_CHINESE_CM,
)

TITLE = "累积 BMI 与腰围暴露（如皋老年队列方法）"
BMI_KEYS = ("bmi_wave1_kg_m2", "bmi_wave2_kg_m2", "bmi_wave3_kg_m2")
WC_KEYS = ("waist_wave1_cm", "waist_wave2_cm", "waist_wave3_cm")
INTERVAL_KEYS = ("interval_1_2_years", "interval_2_3_years")


def excess(value: float, reference: float) -> float:
    """Methods: exposure above the reference; set to zero below it."""
    return max(0.0, value - reference)


def cumulative_exposure(values, reference: float, intervals) -> float:
    """Area under the per-wave excess between consecutive waves (trapezoid), in unit x years.

    The paper prints "excessive exposure ... multiplied by their durations (in years)"
    across three waves; the combination rule is documented in references/contract.md.
    """
    ex = [excess(v, reference) for v in values]
    return sum((ex[i] + ex[i + 1]) / 2.0 * intervals[i] for i in range(len(intervals)))


def bmi_group(bmi: float) -> int:
    """Methods: baseline BMI groups <18.5, 18.5 to <24, 24 to <28, >=28 kg/m2."""
    if bmi < BMI_UNDERWEIGHT_BELOW:
        return 0
    if bmi < BMI_REF:
        return 1
    if bmi < BMI_OBESITY_FROM:
        return 2
    return 3


def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man"}:
        return "male"
    if text in {"female", "f", "女", "woman"}:
        return "female"
    return None


def _missing(manifest: dict, keys, values: dict, reason: str) -> list:
    out = []
    for key in keys:
        if key not in values:
            spec = skillkit.spec_by_key(manifest, key)
            out.append(skillkit.Problem(key, spec["label_zh"], "missing", f"缺少{spec['label_zh']}。{reason}"))
    return out


def series_problems(manifest: dict, values: dict, sex: str | None, sex_raw: str | None, bad_keys: set) -> list:
    problems = []
    have_bmi = [k for k in BMI_KEYS if k in values or k in bad_keys]
    have_wc = [k for k in WC_KEYS if k in values or k in bad_keys]
    if not have_bmi and not have_wc:
        problems += _missing(manifest, BMI_KEYS + WC_KEYS, values,
                             "论文用三轮测量算累积暴露，BMI 三次或腰围三次至少要齐一组。")
        return problems
    if have_bmi and len(have_bmi) < 3:
        problems += [p for p in _missing(manifest, BMI_KEYS, values, "BMI 要三次都有才算累积 BMI。") if p.key not in bad_keys]
    if have_wc and len(have_wc) < 3:
        problems += [p for p in _missing(manifest, WC_KEYS, values, "腰围要三次都有才算累积腰围。") if p.key not in bad_keys]
    if have_wc and sex is None and not sex_raw:
        problems.append(skillkit.Problem("sex", "性别", "missing",
                                         "缺少性别。腰围切点男女不同（男 90 cm、女 80 cm），请用 --sex 写男或女。"))
    return problems


def assess(values: dict, sex: str | None) -> dict:
    intervals = [values[k] for k in INTERVAL_KEYS]
    result: dict = {"intervals": intervals}
    if all(k in values for k in BMI_KEYS):
        bmis = [values[k] for k in BMI_KEYS]
        result["cbmi"] = cumulative_exposure(bmis, BMI_REF, intervals)
        result["bmi_group"] = bmi_group(bmis[-1])
        result["bmi_excess"] = [excess(v, BMI_REF) for v in bmis]
    if sex and all(k in values for k in WC_KEYS):
        wcs = [values[k] for k in WC_KEYS]
        ref = WC_REF_CM[sex]
        result["cwc"] = cumulative_exposure(wcs, ref, intervals)
        result["wc_ref"] = ref
        result["wc_excess"] = [excess(v, ref) for v in wcs]
        result["wc_baseline_over"] = wcs[-1] >= ref
        if sex == "female":
            result["cwc_f85"] = cumulative_exposure(wcs, WC_REF_FEMALE_CHINESE_CM, intervals)
    return result


def _cohort_position(value: float, median: float, iqr: tuple) -> str:
    if value <= 0:
        return "为 0，属于论文里的“无累积暴露”参照组"
    if value > iqr[1]:
        return f"高于论文队列的上四分位数 {iqr[1]:g}"
    if value > median:
        return f"高于论文队列中位数 {median:g}，不超过上四分位数 {iqr[1]:g}"
    return f"大于 0，但不超过论文队列中位数 {median:g}"


def _beta(row: tuple, unit: str, digits: int = 2) -> str:
    est, low, high = row
    unit_text = f" {unit}" if unit else ""
    return f"{est:+.{digits}f}{unit_text}（95% 置信区间 {low:.{digits}f} 到 {high:.{digits}f}）"


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def report_lines(result: dict, values: dict, sex: str | None, age: float | None) -> list:
    d1, d2 = result["intervals"]
    lines = [f"# {TITLE}", "", "## 输入", ""]
    who = []
    if sex:
        who.append("男" if sex == "male" else "女")
    if age is not None:
        who.append(f"{age:g} 岁")
    if who:
        lines.append("- " + "，".join(who))
    lines.append(f"- 三次测量的间隔：第 1→2 次 {d1:g} 年，第 2→3 次 {d2:g} 年（论文是 {PAPER_WAVES[0]}→{PAPER_WAVES[1]}→{PAPER_WAVES[2]}，即 3 年和 2 年）")
    if "cbmi" in result:
        lines.append("- BMI：" + " → ".join(f"{values[k]:.1f}" for k in BMI_KEYS) + " kg/m²")
    if all(k in values for k in WC_KEYS):
        lines.append("- 腰围：" + " → ".join(f"{values[k]:.1f}" for k in WC_KEYS) + " cm")
    lines += ["", "## 结果", ""]
    if "cbmi" in result:
        ex = "、".join(f"{v:.1f}" for v in result["bmi_excess"])
        lines.append(f"- 累积 BMI 暴露（cBMI）：**{result['cbmi']:.1f} kg/m²×年**。三次超出 24 kg/m² 的量依次为 {ex}（低于 24 记 0）。"
                     f"{_cohort_position(result['cbmi'], COHORT['cbmi_median'], COHORT['cbmi_iqr'])}。")
        g = result["bmi_group"]
        lines.append(f"- 最近一次（相当于论文基线）BMI 分组：{BMI_LABELS[g]}。")
    else:
        lines.append("- 没有三次 BMI，所以没有累积 BMI 暴露。")
    if "cwc" in result:
        ex = "、".join(f"{v:.1f}" for v in result["wc_excess"])
        lines.append(f"- 累积腰围暴露（cWC）：**{result['cwc']:.1f} cm×年**。三次超出 {result['wc_ref']:g} cm 的量依次为 {ex}（低于切点记 0）。"
                     f"{_cohort_position(result['cwc'], COHORT['cwc_median'], COHORT['cwc_iqr'])}。")
        if "cwc_f85" in result:
            lines.append(f"- 女性按中国腰围标准 85 cm 再算一次（论文补充表 12 的敏感性分析）：{result['cwc_f85']:.1f} cm×年。")
    else:
        lines.append("- 没有三次腰围（或没有性别），所以没有累积腰围暴露。")
    lines += ["", "## 论文里这一类人的情况", "",
              "论文把累积暴露为 0 的人当参照组，其余的人按三分位分成 T1–T3；三分位的界值论文没有印出，所以这里不给你分到 T1、T2 还是 T3。",
              "补充表 2（模型 1，687 人）里，和累积暴露为 0 的人相比："]
    s2 = TABLE_S2
    lines.append(f"- cBMI 最高三分位（T3）的人，KDM-BA 生物年龄平均高 {_beta(s2['cbmi']['kdm_ba']['T3'], '岁')}，PD {_beta(s2['cbmi']['pd']['T3'], '')}。")
    lines.append(f"- cWC 最高三分位（T3）的人，KDM-BA 平均高 {_beta(s2['cwc']['kdm_ba']['T3'], '岁')}，PD {_beta(s2['cwc']['pd']['T3'], '')}。")
    lines.append(f"- 连续变量：cBMI 每多 1 kg/m²×年，KDM-BA {_beta(s2['cbmi']['kdm_ba']['per_unit'], '岁', 3)}；cWC 每多 1 cm×年，KDM-BA {_beta(s2['cwc']['kdm_ba']['per_unit'], '岁', 3)}。")
    if "cbmi" in result and result["bmi_group"] != 1:
        row = TABLE_S4_BMI_KDM[result["bmi_group"]]
        lines.append(f"- 补充表 4：基线{BMI_LABELS[result['bmi_group']]}的人，KDM-BA 比正常体重的人 {_beta(row, '岁')}。")
    lines += ["", "这些是论文人群的平均差别，不是你的生物年龄，也不能用你的累积暴露乘以每单位的数去推算你老了几岁。",
              "", "## 这意味着什么", ""]
    any_exposure = result.get("cbmi", 0) > 0 or result.get("cwc", 0) > 0
    if not any_exposure:
        lines.append("这几年 BMI 和腰围都没有超过论文的切点，在论文里属于“无累积暴露”的参照组。")
    else:
        lines.append("累积暴露同时反映超出切点多少和持续多久。论文发现，即使在 70 多岁以后，累积暴露越高的人，血液指标算出的生物年龄（KDM-BA）平均越高；"
                     "单看某一次的体重或腰围，只和 KDM-BA 有关联，和 PD 没有。作者据此认为长期的体重和腰围管理可能有意义。"
                     "怎样管理、要不要减重，请和医生一起根据你的整体健康情况决定；高龄时非故意的体重下降也需要请医生看。")
    lines += ["", "## 说明", "",
              f"- 论文人群：江苏如皋老年队列（RLAS）{COHORT['n']} 名老人，平均 {COHORT['mean_age']} 岁（标准差 {COHORT['sd_age']}），女性 {COHORT['female_n']} 人（{COHORT['female_pct']}%）。",
              "- 论文没有写清每一轮的超出量怎样和间隔年数相乘；这里用相邻两轮超出量的平均乘以间隔年数再相加（梯形面积），见技能的 references/contract.md。",
              "- 论文的长寿多基因评分（11 个位点）只用来分高低两组，分组用的中位数没有印出，所以这里不算这一项。",
              "- 论文用的是三次测量（间隔 3 年和 2 年）；你的间隔差得多或测量方法不同，数值不能直接和论文队列比。"]
    if age is not None and age < 70:
        lines.append(f"- 你的年龄 {age:g} 岁，论文队列入组时都在 70 岁以上，结果不一定适用。")
    lines += ["", f"边界: {BOUNDARY}"]
    return lines


def write_report(out_dir: Path, measurements: Path | None, age: float | None, sex_raw: str | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = out_dir / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems = list(collected.problems)
    bad_keys = {p.key for p in problems}
    if age is not None:
        problems += skillkit.check_scalar(manifest, "age", age)
    sex = parse_sex(sex_raw)
    if sex_raw and sex is None:
        problems.append(skillkit.Problem("sex", "性别", "unit", f"性别写的是“{sex_raw}”，请写男或女。"))
    values = dict(collected.values)
    problems += series_problems(manifest, values, sex, sex_raw, bad_keys)
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    result = assess(values, sex)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(result, values, sex, age)) + "\n"), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {
        "cbmi_kg_m2_years": round(result["cbmi"], 3) if "cbmi" in result else None,
        "cwc_cm_years": round(result["cwc"], 3) if "cwc" in result else None,
        "cwc_cm_years_female_85cm": round(result["cwc_f85"], 3) if "cwc_f85" in result else None,
        "baseline_bmi_group": BMI_LABELS[result["bmi_group"]] if "bmi_group" in result else None,
    })
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path,
                        help="CSV item,value,unit: 三次 BMI 和/或三次腰围，两段间隔年数")
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age, args.sex)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
