#!/usr/bin/env python3
"""Phenotypic age and the CVD hazard ratios of Yu et al., GeroScience 2026.

The phenotypic-age formula is printed in the paper's Supplementary Methods
(Levine PhenoAge, computed by the authors with the BioAge R package). The
hazard ratios are printed in Results (path 2): per one-year increase in
PhenoAgeAccel, the cohort residual of phenotypic age on chronological age.

The residual's regression coefficients are not printed, so one person's
PhenoAgeAccel cannot be computed. A change of phenotypic age at the same
chronological age changes the residual by exactly the same amount, so the
hazard ratio of a target state against the current state is
exp(ln(HR) * delta_phenoage). That contrast is the only hazard ratio
reported, and only when --targets is given.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BOUNDARY,
    COHORT_AGE_MEAN,
    COHORT_PHENOAGE_MEAN,
    GAMMA,
    HR_CVD_DEATH,
    HR_INCIDENT_CVD,
    MORTALITY_NUMERATOR,
    PHENOAGE_BIOMARKERS,
    PHENOAGE_LOG_DENOMINATOR,
    PHENOAGE_LOG_NUMERATOR,
    PHENOAGE_OFFSET,
    PHENOTYPE_INTERCEPT,
    PHENOTYPE_WEIGHTS,
    TITLE,
)

OUTPUT_KEYS = ("phenoage", "phenoage_advance", "target_phenoage_delta", "target_hr_incident_cvd", "target_hr_cvd_death")


def linear_predictor(values: dict[str, float]) -> float:
    crp = values["crp_mg_dl"]
    if crp <= 0:
        raise ValueError("ln(CRP) needs a positive mg/dL value")
    paired = {key: values[key] for key in PHENOTYPE_WEIGHTS if key != "lncrp"}
    paired["lncrp"] = math.log(crp)
    return PHENOTYPE_INTERCEPT + sum(weight * paired[key] for key, weight in PHENOTYPE_WEIGHTS.items())


def phenotypic_age(values: dict[str, float]) -> float:
    """Supplementary Methods: PhenoAge = 141.50225 + ln(c * ln(1 - m)) / 0.090165."""
    mortality = 1.0 - math.exp(MORTALITY_NUMERATOR * math.exp(linear_predictor(values)) / GAMMA)
    if not 0.0 < mortality < 1.0:
        raise ValueError("mortality score is outside (0, 1); phenotypic age is undefined")
    return PHENOAGE_OFFSET + math.log(PHENOAGE_LOG_NUMERATOR * math.log(1.0 - mortality)) / PHENOAGE_LOG_DENOMINATOR


def hazard_ratio(delta_years: float, hr: tuple[float, float, float]) -> dict[str, float]:
    """Hazard ratio for a change of delta_years in PhenoAgeAccel, with the CI bounds carried through."""
    point, low, high = (math.exp(math.log(item) * delta_years) for item in hr)
    return {"hr": point, "low": min(low, high), "high": max(low, high)}


def _phenoage_or_none(values: dict[str, float]) -> float | None:
    try:
        return phenotypic_age(values)
    except (ValueError, OverflowError):
        return None


def levers(values: dict[str, float], targets: dict[str, float]) -> dict:
    """Sensitivity at the current values and the model contrast for each target.

    Sensitivities are central differences in years of phenotypic age per unit,
    with the log hazard ratio per unit for incident CVD and CVD death. Lever
    rows move one input alone; "targets" moves all of them together. Nothing
    here predicts what happens to this person.
    """
    manifest = skillkit.load_manifest(__file__)
    specs = {item["key"]: item for item in skillkit.input_specs(manifest)}
    current = phenotypic_age(values)
    sensitivity = []
    for key, label, unit in PHENOAGE_BIOMARKERS:
        x = values[key]
        step = 1e-4 * max(1.0, abs(x))
        low = dict(values, **{key: x - step}) if x - step > 0 else dict(values)
        high = dict(values, **{key: x + step})
        slope = (phenotypic_age(high) - phenotypic_age(low)) / (high[key] - low[key])
        sensitivity.append({
            "key": key,
            "label_zh": label,
            "unit": specs.get(key, {}).get("unit", unit),
            "value": x,
            "years_per_unit": slope,
            "log_hr_incident_cvd_per_unit": math.log(HR_INCIDENT_CVD[0]) * slope,
            "log_hr_cvd_death_per_unit": math.log(HR_CVD_DEATH[0]) * slope,
        })
    out = {
        "schema": "longevity-levers/1",
        "model": "phenoage_cvd_hazard",
        "model_zh": "表型年龄（Levine 公式）与英国生物银行表型年龄加速的心血管病风险比（Yu 2026）",
        "current": {"phenoage": current, "age": values["age"]},
        "sensitivity": sensitivity,
        "levers": [],
        "note_zh": (
            "风险比是同一实足年龄下目标状态对当前状态的模型换算：表型年龄每变 1 岁，"
            f"心血管病发病按 {HR_INCIDENT_CVD[0]:.3f}、死亡按 {HR_CVD_DEATH[0]:.3f} 的倍数变化。"
            "这是观察队列的关联，不是改变化验后的预测。年龄不是杠杆。"
        ),
    }
    usable = {key: value for key, value in targets.items() if key in values and key != "age"}
    for key, target in usable.items():
        moved = _phenoage_or_none(dict(values, **{key: target}))
        if moved is None:
            continue
        delta = moved - current
        out["levers"].append({
            "key": key,
            "label_zh": specs.get(key, {}).get("label_zh", key),
            "unit": specs.get(key, {}).get("unit", ""),
            "from": values[key],
            "to": target,
            "phenoage_delta": delta,
            "hr_incident_cvd": hazard_ratio(delta, HR_INCIDENT_CVD),
            "hr_cvd_death": hazard_ratio(delta, HR_CVD_DEATH),
        })
    out["levers"].sort(key=lambda item: item["phenoage_delta"])
    if usable:
        together = _phenoage_or_none(dict(values, **usable))
        if together is not None:
            delta = together - current
            out["targets"] = {
                "values": usable,
                "phenoage": together,
                "phenoage_delta": delta,
                "hr_incident_cvd": hazard_ratio(delta, HR_INCIDENT_CVD),
                "hr_cvd_death": hazard_ratio(delta, HR_CVD_DEATH),
            }
    return out


def _hr_text(item: dict[str, float]) -> str:
    return f"{item['hr']:.3f}（{item['low']:.3f}–{item['high']:.3f}）"


def render_report(values: dict[str, float] | None, missing_labels: list[str], lever_data: dict | None) -> str:
    lines = [f"# {TITLE}", "", *paper_card_lines(), "", "## 你的结果", ""]
    if values is None:
        lines.append("九项血液指标或实足年龄没有齐，所以没有表型年龄，也没有风险比换算。还缺：" + "、".join(missing_labels) + "。")
    else:
        age = values["age"]
        phenoage = phenotypic_age(values)
        lines.append(f"表型年龄 {phenoage:.2f} 岁，实足年龄 {age:g} 岁，表型年龄减实足年龄 {phenoage - age:.2f} 岁。")
        lines.append("")
        lines.append(
            "论文里的“表型年龄加速”是英国生物银行队列中表型年龄对实足年龄回归的残差，回归系数没有印出，"
            "所以这里给的差不是论文的加速值，也不换算成你自己的风险比。作为背景：论文队列的平均实足年龄 "
            f"{COHORT_AGE_MEAN} 岁、平均表型年龄 {COHORT_PHENOAGE_MEAN} 岁，表型年龄普遍低于实足年龄。"
        )
        lines.extend(["", "### 用到的九项", ""])
        for key, label, unit in PHENOAGE_BIOMARKERS:
            lines.append(f"- {label}（{unit}）：{values[key]:g}")
        lines.extend(["", "## 论文的风险比", ""])
        lines.append(
            f"在这个队列里，表型年龄加速每高 1 岁，心血管病发病风险比 {HR_INCIDENT_CVD[0]:.3f}（{HR_INCIDENT_CVD[1]:.3f}–{HR_INCIDENT_CVD[2]:.3f}），"
            f"心血管病死亡风险比 {HR_CVD_DEATH[0]:.3f}（{HR_CVD_DEATH[1]:.3f}–{HR_CVD_DEATH[2]:.3f}）。"
            "论文的样条分析显示这一关联并非完全线性，女性尤其明显；风险比按线性模型使用。"
        )
        targets = (lever_data or {}).get("targets")
        lines.extend(["", "## 如果达到目标值（模型换算）", ""])
        if not targets:
            lines.append("没有给目标值，所以没有换算。给 --targets 时，按同一实足年龄比较目标状态和当前状态。")
        else:
            lines.append(
                f"全部目标同时达到时，表型年龄 {targets['phenoage']:.2f} 岁，变化 {targets['phenoage_delta']:+.2f} 岁；"
                f"按论文风险比换算，心血管病发病风险比 {_hr_text(targets['hr_incident_cvd'])}，"
                f"死亡风险比 {_hr_text(targets['hr_cvd_death'])}（相对你现在的数值）。"
            )
            for item in lever_data["levers"]:
                lines.append(
                    f"- 只把{item['label_zh']}从 {item['from']:g} 改到 {item['to']:g} {item['unit']}：表型年龄 {item['phenoage_delta']:+.2f} 岁，"
                    f"发病风险比 {_hr_text(item['hr_incident_cvd'])}，死亡风险比 {_hr_text(item['hr_cvd_death'])}。"
                )
            lines.append("这些是观察队列关联的模型换算，不是改变化验后一定会发生的风险变化。")
    lines.extend(["", "## 没有计算的", ""])
    lines.append("- 你的绝对心血管风险：论文只报告风险比，没有基线风险。")
    lines.append("- KDM 生物年龄加速：需要论文没有印出的 NHANES 拟合参数。")
    lines.append("- 四个饮食质量评分：需要完整的 24 小时膳食记录和评分细则，不在本论文里。")
    lines.extend(["", f"边界: {BOUNDARY}"])
    return "\n".join(lines) + "\n"


def write_report(out_dir: Path, biomarkers: Path | None, age: float | None, targets: Path | None = None) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "levers.json"):
        stale = out_dir / name
        if stale.exists():
            stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    empty = {key: None for key in OUTPUT_KEYS}
    collected = skillkit.collect_file(biomarkers, manifest)
    # A missing marker or age also stops the run, so the caller can say what to measure.
    problems = list(collected.problems)
    problems += skillkit.check_scalar(manifest, "age", age)
    wanted: dict[str, float] = {}
    if targets is not None:
        target_collected = skillkit.collect_file(targets, manifest)
        problems += [item for item in target_collected.problems if item.kind != "missing"]
        wanted = dict(target_collected.values)
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        text = path.read_text(encoding="utf-8")
        rows = text.splitlines()
        if rows and rows[0].startswith("# "):
            text = "\n".join([rows[0], "", *paper_card_lines(), "", "输入没有通过检查，所以没有表型年龄，也没有风险比换算。", *rows[1:]]) + "\n"
        path.write_text(text, encoding="utf-8")
        skillkit.write_result(out_dir, manifest, empty)
        return skillkit.EXIT_INPUT_PROBLEM
    values = dict(collected.values)
    missing = [label for key, label, _unit in PHENOAGE_BIOMARKERS if key not in values]
    if age is None:
        missing.append("实足年龄")
    complete = None
    lever_data = None
    outputs = dict(empty)
    if not missing:
        values["age"] = age
        complete = values
        phenoage = phenotypic_age(complete)
        lever_data = levers(complete, wanted)
        outputs["phenoage"] = phenoage
        outputs["phenoage_advance"] = phenoage - age
        if "targets" in lever_data:
            outputs["target_phenoage_delta"] = lever_data["targets"]["phenoage_delta"]
            outputs["target_hr_incident_cvd"] = lever_data["targets"]["hr_incident_cvd"]["hr"]
            outputs["target_hr_cvd_death"] = lever_data["targets"]["hr_cvd_death"]["hr"]
        (out_dir / "levers.json").write_text(json.dumps(lever_data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (out_dir / "report.md").write_text(render_report(complete, missing, lever_data), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, outputs)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phenotypic age and CVD hazard ratios (Yu et al., GeroScience 2026)")
    parser.add_argument("--biomarkers", type=Path, help="CSV marker,value,unit with the nine PhenoAge biomarkers")
    parser.add_argument("--age", type=float, help="chronological age in years")
    parser.add_argument("--targets", type=Path, help="CSV of target values (marker,value,unit) for out/levers.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    code = write_report(args.out, args.biomarkers, args.age, args.targets)
    sys.stdout.write(str(args.out / "report.md") + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
