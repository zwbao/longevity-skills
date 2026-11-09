#!/usr/bin/env python3
"""Personal modifiable risk factor score (Chen et al., J Gerontol A 2026;81(10):glag196).

Counts the 11 binary risk factors of Method S1 (0-11), the three cluster scores,
and looks up the per-point hazard ratio of the person's age group in
Supplementary Table S11. The paper prints no per-person example; the hazard
relative to zero factors is the per-point HR raised to the score (a model
extrapolation, labelled as such).
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
    AGE_GROUPS,
    BMI_HIGH,
    BMI_LOW,
    BOUNDARY,
    CLUSTERS_ZH,
    DBP_MMHG,
    DIET_ITEMS_ZH,
    DIET_SCORE_RISK_MAX,
    FACTORS,
    FASTING_GLUCOSE_MMOL,
    GDS15_DEPRESSION_MIN,
    HDL_MMOL,
    LDL_MMOL,
    PA_MET_H_WEEK_MIN,
    RANDOM_GLUCOSE_MMOL,
    SBP_MMHG,
    SLEEP_HIGH_H,
    SLEEP_LOW_H,
    TABLE_S11,
    TC_MMOL,
    TG_MMOL,
)

TITLE = "可改变危险因素得分与全因死亡风险比"
FLAGS = (
    "education_junior_middle", "depressive_symptoms", "ever_smoked", "ever_drank",
    "diabetes_diagnosed", "glucose_lowering_medication", "hypertension_diagnosed",
    "antihypertensive_medication", "hyperlipidemia_diagnosed", "lipid_lowering_medication",
)
YES = {"1", "yes", "y", "true", "是", "有"}
NO = {"0", "no", "n", "false", "否", "无", "没有"}
PA_UNITS = {"met-h/week", "met-h/wk", "met-hr/week", "met·h/week", "met-h/周", "met小时/周", "met-hours/week", "met h/week", "mets-h/week"}
LIPIDS = ("tc_mmol_l", "ldl_c_mmol_l", "hdl_c_mmol_l", "tg_mmol_l")
# Inputs a target file may move. Diagnoses and medicines are not levers.
TARGETABLE = ("pa_met_h_week", "diet_score", "sleep_hours", "bmi_kg_m2", "weight_kg", "sbp_mmhg", "dbp_mmhg",
              "fasting_glucose_mmol_l", "random_glucose_mmol_l", *LIPIDS, "gds15_score")


def age_group(age: float) -> tuple[str, str]:
    key, label = AGE_GROUPS[0][1], AGE_GROUPS[0][2]
    for low, group_key, group_label in AGE_GROUPS:
        if age >= low:
            key, label = group_key, group_label
    return key, label


def bmi_of(values: dict) -> float | None:
    if "bmi_kg_m2" in values:
        return values["bmi_kg_m2"]
    if "weight_kg" in values and "height_cm" in values:
        return values["weight_kg"] / (values["height_cm"] / 100) ** 2
    return None


def _any_or_unknown(hits: list[bool | None]) -> bool | None:
    """True if any criterion is met; False only if every criterion is known and unmet."""
    if any(hit is True for hit in hits):
        return True
    if all(hit is False for hit in hits):
        return False
    return None


def _cmp(value: float | None, test) -> bool | None:
    return None if value is None else bool(test(value))


def classify(values: dict, flags: dict) -> dict:
    """Each of the 11 factors as 1, 0 or None (cannot be decided), by Method S1."""
    edu = flags.get("education_junior_middle")
    gds = values.get("gds15_score")
    cidi = flags.get("depressive_symptoms")
    dep_hits = [hit for hit in (_cmp(gds, lambda v: v >= GDS15_DEPRESSION_MIN), cidi) if hit is not None]
    depression = True if any(dep_hits) else (False if dep_hits else None)
    glucose = [_cmp(values.get("fasting_glucose_mmol_l"), lambda v: v >= FASTING_GLUCOSE_MMOL),
               _cmp(values.get("random_glucose_mmol_l"), lambda v: v >= RANDOM_GLUCOSE_MMOL)]
    glucose_known = [hit for hit in glucose if hit is not None]
    glucose_hit = True if any(glucose_known) else (False if glucose_known else None)
    bp = _any_or_unknown([_cmp(values.get("sbp_mmhg"), lambda v: v >= SBP_MMHG),
                          _cmp(values.get("dbp_mmhg"), lambda v: v >= DBP_MMHG)])
    lipids = _any_or_unknown([_cmp(values.get("ldl_c_mmol_l"), lambda v: v >= LDL_MMOL),
                              _cmp(values.get("hdl_c_mmol_l"), lambda v: v < HDL_MMOL),
                              _cmp(values.get("tg_mmol_l"), lambda v: v >= TG_MMOL),
                              _cmp(values.get("tc_mmol_l"), lambda v: v >= TC_MMOL)])
    bmi = bmi_of(values)
    state = {
        "low_education": None if edu is None else (not edu),
        "depression": depression,
        "smoking": flags.get("ever_smoked"),
        "alcohol": flags.get("ever_drank"),
        "physical_inactivity": _cmp(values.get("pa_met_h_week"), lambda v: v < PA_MET_H_WEEK_MIN),
        "unhealthy_diet": _cmp(values.get("diet_score"), lambda v: v <= DIET_SCORE_RISK_MAX),
        "abnormal_sleep": _cmp(values.get("sleep_hours"), lambda v: v < SLEEP_LOW_H or v > SLEEP_HIGH_H),
        "abnormal_bmi": _cmp(bmi, lambda v: v < BMI_LOW or v > BMI_HIGH),
        "diabetes": _any_or_unknown([flags.get("diabetes_diagnosed"), flags.get("glucose_lowering_medication"), glucose_hit]),
        "hypertension": _any_or_unknown([flags.get("hypertension_diagnosed"), flags.get("antihypertensive_medication"), bp]),
        "dyslipidemia": _any_or_unknown([flags.get("hyperlipidemia_diagnosed"), flags.get("lipid_lowering_medication"), lipids]),
    }
    return {key: (None if value is None else int(bool(value))) for key, value in state.items()}


MISSING_ZH = {
    "low_education": "是否读完初中（--education-junior-middle yes 或 no）",
    "depression": "GDS-15 得分，或过去一年是否有两周以上的抑郁症状（--depressive-symptoms yes 或 no）",
    "smoking": "是否曾经吸烟（--ever-smoked yes 或 no）",
    "alcohol": "是否饮酒（--ever-drank yes 或 no）",
    "physical_inactivity": "每周体力活动量（MET-小时/周）",
    "unhealthy_diet": "10 项健康饮食得分（0–10）",
    "abnormal_sleep": "每晚平均睡眠时长（小时）",
    "abnormal_bmi": "体质指数，或体重和身高",
    "diabetes": "是否诊断过糖尿病、是否在用降糖药（yes 或 no），以及空腹血糖或随机血糖",
    "hypertension": "是否诊断过高血压、是否在用降压药（yes 或 no），以及收缩压和舒张压",
    "dyslipidemia": "是否诊断过高血脂、是否在用降脂药（yes 或 no），以及总胆固醇、低密度和高密度脂蛋白胆固醇、甘油三酯四项",
}


def scores(state: dict) -> dict:
    total = sum(state.values())
    by_cluster = {cluster: 0 for cluster in CLUSTERS_ZH}
    for key, _label, cluster in FACTORS:
        by_cluster[cluster] += state[key]
    return {"modifiable": total, **by_cluster}


def compute(values: dict, flags: dict, age: float) -> dict:
    state = classify(values, flags)
    if any(value is None for value in state.values()):
        raise ValueError("undetermined factors")
    group, label = age_group(age)
    hr = TABLE_S11[group]["modifiable"][0]
    s = scores(state)
    return {"state": state, "scores": s, "age_group": group, "age_group_zh": label, "hr_per_point": hr,
            "relative_hazard_vs_zero": hr ** s["modifiable"]}


def parse_flag(name: str, raw: str | None) -> tuple[bool | None, str | None]:
    if raw is None:
        return None, None
    text = str(raw).strip().lower()
    if text in YES:
        return True, None
    if text in NO:
        return False, None
    return None, f"--{name.replace('_', '-')} 只接受 yes 或 no（是/否），收到「{raw}」。"


def collect(path: Path | None, manifest: dict) -> skillkit.Collected:
    """skillkit.collect_measurements, with MET-h/week written for the activity row read as its score unit."""
    rows = skillkit.read_rows(path) if path is not None else []
    if rows:
        fields = list(rows[0].keys())
        unit_col = skillkit._column(fields, skillkit.UNIT_COLUMNS)
        name_col = skillkit._column(fields, skillkit.NAME_COLUMNS)
        if unit_col and name_col:
            index = skillkit.alias_index(skillkit.input_specs(manifest))
            for row in rows:
                hit = next((index[v] for v in skillkit.name_variants(row.get(name_col, "")) if v in index), None)
                unit = row.get(unit_col, "").strip().lower().replace(" ", "")
                if hit and hit[0]["key"] == "pa_met_h_week" and unit.replace("mets", "met") in {u.replace(" ", "") for u in PA_UNITS}:
                    row[unit_col] = "score"
    return skillkit.collect_measurements(rows, manifest)


FIXED_ZH = {
    "low_education": "受教育程度是过去的事，成年后通常改不了；论文把它列为社会层面可改变的因素。",
    "smoking": "论文把已戒烟也算作“有”，所以按这个定义戒烟后这一项仍是 1；这不是说戒烟没有用。",
    "alcohol": "论文把已戒酒也算作“有”，所以按这个定义戒酒后这一项仍是 1。",
}


def levers(values: dict, flags: dict, age: float, targets: dict) -> dict:
    """Score and model hazard now, per factor present, and with each target alone and together."""
    manifest = skillkit.load_manifest(__file__)
    now = compute(values, flags, age)
    hr = now["hr_per_point"]
    labels = {key: label for key, label, _ in FACTORS}
    sensitivity = [
        {"key": key, "label_zh": labels[key], "present": bool(now["state"][key]),
         "relative_hazard_factor_if_removed": (1 / hr) if now["state"][key] else 1.0,
         **({"not_a_target": True, "reason_zh": FIXED_ZH[key]} if key in FIXED_ZH and now["state"][key] else {})}
        for key, _label, _cluster in FACTORS
    ]
    out = {
        "schema": "longevity-levers/1",
        "model": "modifiable-risk-factor-score",
        "model_zh": "可改变危险因素计数（Chen 等 2026，三个中国队列）",
        "current": {"modifiable_risk_score": now["scores"]["modifiable"], "age_group": now["age_group"],
                    "hr_per_point": hr, "relative_hazard_vs_zero": now["relative_hazard_vs_zero"]},
        "sensitivity": sensitivity,
        "levers": [],
        "note_zh": ("每项是 0 或 1，等权相加。按论文定义，诊断过或正在用药本身就算这一项存在，所以血压、血糖、血脂达标"
                    "不会让这一项变成 0；这不是停药的理由。少一项对应的相对风险变化是按每分风险比推算的模型数。"),
    }
    usable = {key: value for key, value in targets.items() if key in TARGETABLE}
    if "weight_kg" in usable and "height_cm" not in values:
        usable.pop("weight_kg")
        out["skipped_zh"] = "体重目标没有用上：测量表里没有身高，算不出目标体质指数。"

    def moved_values(change: dict) -> dict:
        moved = dict(values, **change)
        if "weight_kg" in change and "bmi_kg_m2" not in change:
            moved.pop("bmi_kg_m2", None)  # a weight target replaces a directly given BMI
        return moved

    if usable:
        for key, target in usable.items():
            moved = compute(moved_values({key: target}), flags, age)
            delta = moved["scores"]["modifiable"] - now["scores"]["modifiable"]
            spec = skillkit.spec_by_key(manifest, key)
            out["levers"].append({"key": key, "label_zh": spec.get("label_zh", key), "unit": spec.get("unit", ""),
                                  "from": values.get(key), "to": target, "score_delta": delta,
                                  "relative_hazard_factor": hr ** delta})
        together = compute(moved_values(usable), flags, age)
        delta = together["scores"]["modifiable"] - now["scores"]["modifiable"]
        out["targets"] = {"values": usable, "modifiable_risk_score": together["scores"]["modifiable"],
                          "score_delta": delta, "relative_hazard_factor": hr ** delta,
                          "relative_hazard_vs_zero": together["relative_hazard_vs_zero"]}
        out["levers"].sort(key=lambda item: item["score_delta"])
    return out


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def _fmt_ci(triple: tuple) -> str:
    return f"{triple[0]:.3f}（{triple[1]:.3f}–{triple[2]:.3f}）"


def write_report(out_dir: Path, measurements: Path | None, age: float | None, flag_values: dict,
                 targets: Path | None = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "levers.json"):
        if (out_dir / name).exists():
            (out_dir / name).unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = collect(measurements, manifest)
    problems = [p for p in collected.problems if p.kind != "missing"]
    problems += skillkit.check_scalar(manifest, "age", age)
    flags: dict = {}
    for name in FLAGS:
        value, message = parse_flag(name, flag_values.get(name))
        if message:
            problems.append(skillkit.Problem(name, name, "parse", message))
        flags[name] = value
    values = dict(collected.values)
    if not problems:
        state = classify(values, flags)
        labels = {key: label for key, label, _ in FACTORS}
        for key, value in state.items():
            if value is None:
                problems.append(skillkit.Problem(key, labels[key], "missing", f"{labels[key]}这一项定不下来：需要{MISSING_ZH[key]}。"))
    empty = {"modifiable_risk_score": None, "sep_risk_score": None, "behavior_risk_score": None, "metabolic_risk_score": None,
             "age_group": None, "hr_per_point": None, "relative_hazard_vs_zero": None}
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, empty)
        return path

    result = compute(values, flags, age)
    s = result["scores"]
    row = TABLE_S11[result["age_group"]]
    lines = [f"# {TITLE}", "", "## 结果", ""]
    lines.append(f"- 可改变危险因素：{s['modifiable']} 项（满分 11）。社会经济与心理 {s['sep']}/2，行为 {s['behavior']}/5，代谢 {s['metabolic']}/4。")
    lines.append(f"- 年龄 {age:g} 岁，属于论文的{result['age_group_zh']}。")
    lines.append(f"- 这个年龄段每多一项，全因死亡风险比 {_fmt_ci(row['modifiable'])}（补充表 S11，三个队列汇总，按年龄、性别、队列调整）。")
    lines.append(f"- 与没有任何一项的同龄人相比，模型推算的相对风险约 {result['relative_hazard_vs_zero']:.2f} 倍"
                 "（每分风险比的得分次方；论文没有印出这个数，置信区间没有算）。")
    if collected.unmatched:
        lines.append(f"- 测量表里这几行没有认出，没有用上：{'、'.join(collected.unmatched)}。")
    lines += ["", "## 逐项", "", "| 因素 | 组别 | 判定 |", "| --- | --- | --- |"]
    for key, label, cluster in FACTORS:
        lines.append(f"| {label} | {CLUSTERS_ZH[cluster]} | {'有' if result['state'][key] else '无'} |")
    bmi = bmi_of(values)
    lines += ["", "## 这个年龄段的分组风险比（补充表 S11，每多一分）", "",
              f"- 社会经济与心理 {_fmt_ci(row['sep'])}；行为 {_fmt_ci(row['behavior'])}；代谢 {_fmt_ci(row['metabolic'])}。",
              "- 这三个数来自同时放进三个分组得分的模型，不能相乘成一个总数。", "", "## 说明", "",
              "- 11 项等权相加，每项只看有或没有，不看程度；切点照补充方法 S1。",
              "- 诊断过或正在用降压、降糖、降脂药，按论文定义这一项就算“有”，即使现在测得的数值正常。这是论文的定义，不是让你停药或换药的理由。"]
    if bmi is not None and math.isclose(bmi, BMI_HIGH, abs_tol=0.05):
        lines.append("- 你的体质指数正好在 28：补充方法 S1 的表把 >28 算作风险，正文的统一说明写的是 ≥28，两处不一致；这里按表算“无”。")
    lines += [
        "- 健康饮食得分按 10 条行为各 1 分：" + "；".join(DIET_ITEMS_ZH) + "。",
        "- 队列都在中国南方（海南、广州），百岁组样本只有 989 人；只在基线测了一次，随访中的变化没有算进去。",
        "- 风险比是人群里的关联，不是这个人的死亡概率；论文没有给出可以换算成个人概率的基线生存率。",
        "", f"边界: {BOUNDARY}",
    ]
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(lines) + "\n"), encoding="utf-8")
    skillkit.write_result(out_dir, manifest, {
        "modifiable_risk_score": s["modifiable"], "sep_risk_score": s["sep"], "behavior_risk_score": s["behavior"],
        "metabolic_risk_score": s["metabolic"], "age_group": result["age_group"], "hr_per_point": result["hr_per_point"],
        "relative_hazard_vs_zero": result["relative_hazard_vs_zero"]})
    wanted = dict(collect(targets, manifest).values) if targets is not None else {}
    (out_dir / "levers.json").write_text(json.dumps(levers(values, flags, age, wanted), ensure_ascii=False, indent=1) + "\n",
                                         encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path, help="CSV item,value,unit")
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex", help="accepted; not part of the score")
    for name in FLAGS:
        parser.add_argument(f"--{name.replace('_', '-')}", dest=name)
    parser.add_argument("--targets", type=Path, help="CSV of target values for out/levers.json")
    parser.add_argument("--medications", type=Path, help="accepted and ignored: medicine use is given by the yes/no flags")
    parser.add_argument("--labs", type=Path, help="accepted and ignored")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age, {name: getattr(args, name) for name in FLAGS}, args.targets)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
