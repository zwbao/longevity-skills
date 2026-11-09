#!/usr/bin/env python3
"""Physical activity dose and frailty index after Ji, GeroScience 2026 (CHARLS, age >= 60).

Computes the paper's weighted total physical activity, its category and the 48-item
frailty index of Table 2, the two frailty phenotype items that need no cohort cut-off,
and looks up the printed betas (Tables 4-5, Figures 6-7) and Cox hazard ratios
(Supplementary Tables 1-2) for the person's category. Constants are in presets.py; the
contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (
    BMI_HIGH,
    BMI_LOW,
    BOUNDARY,
    COHORT,
    CREATININE_CUT_MG_DL,
    CRP_CUT_MG_L,
    FI_BMI_ITEM,
    FI_HEALTHY_MAX,
    FI_ITEMS_TOTAL,
    FI_PREFRAIL_MAX,
    FI_QUESTION_ITEMS,
    FIG6_FP_BETA,
    FIG7_FI_BETA,
    FP_HEALTHY_MAX,
    HB_NORMAL_G_DL,
    HBA1C_CUT_PCT,
    PA_CATEGORY_LABELS,
    PA_DOMAIN_ZH,
    PA_DOMAINS,
    PA_GUIDELINE_MIN,
    PA_WEIGHTS,
    SCORES,
    SUPP1_FP_HR_ALL,
    SUPP1_FP_HR_FRAIL,
    SUPP2_FI_HR_ALL,
    SUPP2_FI_HR_FRAIL,
    TABLE4_FP_GUIDELINE,
    TABLE5_FI_GUIDELINE,
)

TITLE = "体力活动剂量与衰弱指数（CHARLS 中国老人队列）"
_EPS = 1e-9
FI_CATEGORY_ZH = ("健康（≤0.10）", "衰弱前期（0.10–0.21）", "衰弱（>0.21）")


# ---------------------------------------------------------------- physical activity
def total_pa(hpa: float, mpa: float, lpa: float) -> float:
    """Methods: Total PA = (2 x HPA) + MPA + (0.5 x LPA), min/week."""
    return PA_WEIGHTS["hpa"] * hpa + PA_WEIGHTS["mpa"] * mpa + PA_WEIGHTS["lpa"] * lpa


def pa_category(minutes: float) -> int:
    """0 = 0 min/week, 1 = 1-149, 2 = 150-299, 3 = >= 300 (Methods)."""
    if minutes <= _EPS:
        return 0
    if minutes < PA_GUIDELINE_MIN - _EPS:
        return 1
    if minutes < 300 - _EPS:
        return 2
    return 3


# ---------------------------------------------------------------- frailty index
def bmi(weight_kg: float, height_cm: float) -> float:
    return weight_kg / (height_cm / 100.0) ** 2


def bmi_deficit(value: float) -> float:
    """Table 1 / Table 2 item 12: BMI < 18.5 or >= 25 = 1."""
    return 1.0 if (value < BMI_LOW or value >= BMI_HIGH) else 0.0


def fi_item_scores(values: dict, sex: str | None) -> dict:
    """Deficit score per answered item number (1-48), per Table 2. Missing items are absent."""
    scores = {}
    for num, key, _zh, _en, _code, kind in FI_QUESTION_ITEMS:
        if key in values:
            scores[num] = SCORES[kind][int(round(values[key]))]
    if "weight_kg" in values and "height_cm" in values:
        scores[FI_BMI_ITEM] = bmi_deficit(bmi(values["weight_kg"], values["height_cm"]))
    if "hba1c_pct" in values:
        scores[45] = 1.0 if values["hba1c_pct"] > HBA1C_CUT_PCT else 0.0
    if "hemoglobin_g_dl" in values and sex in HB_NORMAL_G_DL:
        low, high = HB_NORMAL_G_DL[sex]
        scores[46] = 0.0 if low <= values["hemoglobin_g_dl"] <= high else 1.0
    if "crp_mg_l" in values:
        scores[47] = 1.0 if values["crp_mg_l"] > CRP_CUT_MG_L else 0.0
    if "creatinine_mg_dl" in values:
        scores[48] = 1.0 if values["creatinine_mg_dl"] > CREATININE_CUT_MG_DL else 0.0
    return scores


def fi_category(fi: float) -> int:
    if fi <= FI_HEALTHY_MAX + _EPS:
        return 0
    if fi <= FI_PREFRAIL_MAX + _EPS:
        return 1
    return 2


def frailty_index(scores: dict) -> dict:
    """Sum of deficit scores / 48 (Table 2 footnote). With missing items only the bounds are given."""
    answered = len(scores)
    total = sum(scores.values())
    missing = FI_ITEMS_TOTAL - answered
    fi_min = total / FI_ITEMS_TOTAL
    fi_max = (total + missing) / FI_ITEMS_TOTAL
    out = {"answered": answered, "sum": total, "min": fi_min, "max": fi_max, "value": None, "category": None}
    if missing == 0:
        out["value"] = fi_min
        out["category"] = fi_category(fi_min)
    elif fi_category(fi_min) == fi_category(fi_max):
        out["category"] = fi_category(fi_min)
    return out


# ---------------------------------------------------------------- frailty phenotype (partial)
def fp_partial(values: dict) -> dict:
    """Table 1 items computable without cohort percentiles: endurance (db001) and BMI."""
    points, known = 0, []
    if "fi18_jog_1km" in values:
        known.append("endurance")
        points += 1 if int(round(values["fi18_jog_1km"])) >= 3 else 0   # need help and yes = 1
    if "weight_kg" in values and "height_cm" in values:
        known.append("bmi")
        points += int(bmi_deficit(bmi(values["weight_kg"], values["height_cm"])))
    if points > FP_HEALTHY_MAX:
        status = "已知两项得 2 分，衰弱表型分数至少 2，已达到论文的衰弱综合征（FP>1）"
    elif len(known) < 2:
        status = "能算的两项没有齐，无法判断"
    else:
        status = f"已知两项得 {points} 分；握力、步速、体力活动三项需要论文没印出的队列切点，无法判断是否 FP>1"
    return {"points": points if len(known) == 2 else None, "known": known, "status": status}


# ---------------------------------------------------------------- input checks
def parse_sex(raw: str | None) -> str | None:
    text = (raw or "").strip().lower()
    if text in {"male", "m", "男", "man"}:
        return "male"
    if text in {"female", "f", "女", "woman"}:
        return "female"
    return None


def code_problems(manifest: dict, values: dict) -> list:
    """Questionnaire answers must be whole answer codes."""
    problems = []
    for _num, key, _zh, _en, _code, kind in FI_QUESTION_ITEMS:
        if key in values and (abs(values[key] - round(values[key])) > _EPS or int(round(values[key])) not in SCORES[kind]):
            spec = skillkit.spec_by_key(manifest, key)
            problems.append(skillkit.Problem(key, spec["label_zh"], "range",
                                             f"{spec['label_zh']} 填的是 {values[key]:g}，不是一个答案代码。{spec.get('note_zh', '')}"))
    return problems


# ---------------------------------------------------------------- report
def _beta(row, digits: int) -> str:
    if row is None:
        return "参照组"
    est, low, high = row[:3]
    p = f"，p {row[3]}" if len(row) > 3 else ""
    return f"{est:.{digits}f}（95% 置信区间 {low:.{digits}f} 到 {high:.{digits}f}{p}）"


def _hr(row) -> str:
    if row is None:
        return "1（参照组）"
    est, low, high, p = row
    return f"{est:.3f}（95% 置信区间 {low:.3f}–{high:.3f}，p {p}）"


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def assess(values: dict, sex: str | None) -> dict:
    minutes = {d: values[f"{d}_min_per_week"] for d in ("hpa", "mpa", "lpa")}
    minutes["total"] = total_pa(minutes["hpa"], minutes["mpa"], minutes["lpa"])
    cats = {d: pa_category(minutes[d]) for d in PA_DOMAINS}
    scores = fi_item_scores(values, sex)
    fi = frailty_index(scores)
    fp = fp_partial(values)
    body = bmi(values["weight_kg"], values["height_cm"]) if ("weight_kg" in values and "height_cm" in values) else None
    return {"minutes": minutes, "cats": cats, "scores": scores, "fi": fi, "fp": fp, "bmi": body}


def report_lines(r: dict, sex: str | None, age: float | None) -> list:
    m, c, fi, fp = r["minutes"], r["cats"], r["fi"], r["fp"]
    lines = [f"# {TITLE}", "", "## 你的体力活动", ""]
    lines.append(f"- 每周高强度 {m['hpa']:g} 分钟、中等强度 {m['mpa']:g} 分钟、低强度 {m['lpa']:g} 分钟。")
    lines.append(f"- 论文的加权总活动量 = 2×{m['hpa']:g} + {m['mpa']:g} + 0.5×{m['lpa']:g} = **{m['total']:g} 分钟/周**，"
                 f"分档 {PA_CATEGORY_LABELS[c['total']]}；{'已' if m['total'] >= PA_GUIDELINE_MIN - _EPS else '没有'}达到每周 150 分钟。")
    lines.append("- 分强度：" + "；".join(f"{PA_DOMAIN_ZH[d]} {PA_CATEGORY_LABELS[c[d]]}" for d in ("hpa", "mpa", "lpa")) + "。")
    lines += ["", "### 论文人群里这些分档对应什么", "",
              "β 是该档相对每周 0 分钟的人，衰弱表型分数（0–5 分）或衰弱指数（0–1）平均低多少（负数表示更低），"
              "风险比是 10 年全因死亡风险相对每周 0 分钟的人。",
              "", "| 活动 | 你的分档 | 衰弱表型分数 β（图 6） | 衰弱指数 β（图 7） | 10 年死亡风险比（补充表 1，衰弱表型样本） | 10 年死亡风险比（补充表 2，衰弱指数样本） |",
              "| --- | --- | --- | --- | --- | --- |"]
    for d in PA_DOMAINS:
        k = c[d]
        lines.append(f"| {PA_DOMAIN_ZH[d]} | {PA_CATEGORY_LABELS[k]} | {_beta(FIG6_FP_BETA[d][k], 2)} | {_beta(FIG7_FI_BETA[d][k], 2)} | "
                     f"{_hr(SUPP1_FP_HR_ALL[d][k])} | {_hr(SUPP2_FI_HR_ALL[d][k])} |")
    met = [d for d in PA_DOMAINS if m[d] >= PA_GUIDELINE_MIN - _EPS]
    if met:
        lines += ["", "你达到每周 150 分钟的项目，论文表 4、表 5（模型 3）里达标者相对不达标者的差："]
        for d in met:
            lines.append(f"- {PA_DOMAIN_ZH[d]}：衰弱表型分数 β {_beta(TABLE4_FP_GUIDELINE[d], 3)}；衰弱指数 β {_beta(TABLE5_FI_GUIDELINE[d], 3)}。")

    lines += ["", "## 你的衰弱指数（48 项）", ""]
    lines.append(f"- 已答 {fi['answered']}/48 项，缺陷分合计 {fi['sum']:.2f}。")
    if fi["value"] is not None:
        lines.append(f"- 衰弱指数 = {fi['sum']:.2f} ÷ 48 = **{fi['value']:.3f}**，分档 {FI_CATEGORY_ZH[fi['category']]}。")
    else:
        lines.append(f"- 还缺 {FI_ITEMS_TOTAL - fi['answered']} 项，所以没有衰弱指数；缺项全按 0 时是 {fi['min']:.3f}，全按 1 时是 {fi['max']:.3f}。"
                     "缺的项不能用 0 代替，请补齐后再算。")
        if fi["category"] is not None:
            lines.append(f"- 不论缺项怎么答，分档都是 {FI_CATEGORY_ZH[fi['category']]}。")
        missing = missing_items(r)
        if missing:
            lines.append("- 缺的项：" + "、".join(missing) + "。")
    lines += ["", "## 衰弱表型（5 项里能算的 2 项）", ""]
    if r["bmi"] is not None:
        lines.append(f"- BMI {r['bmi']:.1f} kg/m²（<18.5 或 ≥25 计 1 分）。")
    lines.append(f"- {fp['status']}。")
    lines.append("- 握力、步速和体力活动三项，论文按 CHARLS 队列内（分性别）最低 20% 计分，没有印出切点，所以不算。")

    frail = (fi["category"] is not None and fi["category"] >= 1) or (fp["points"] is not None and fp["points"] >= 2)
    if frail:
        lines += ["", "## 论文里衰弱者的分组结果", "",
                  "论文另在衰弱者（图 8、图 9 的 F–I 组）里比较了各活动分档的 10 年死亡风险比：", ""]
        for d in PA_DOMAINS:
            k = c[d]
            lines.append(f"- {PA_DOMAIN_ZH[d]} {PA_CATEGORY_LABELS[k]}：补充表 1 {_hr(SUPP1_FP_HR_FRAIL[d][k])}；补充表 2 {_hr(SUPP2_FI_HR_FRAIL[d][k])}。")
        lines.append("- 注意：补充表 1 的 F 组与 B 组、补充表 2 的 G 组与 C 组数值完全相同，原文如此，这几行未必真是衰弱亚组的结果。")

    lines += ["", "## 这意味着什么", "",
              "- 置信区间跨过 0（β）或跨过 1（风险比）的那一档，论文里没有统计学差异。",
              "- 论文的衰弱分数比较是同一时间点的横断面比较，衰弱的人本来就可能活动更少（反向因果）；作者明确写这些结果不能证明增加活动能预防衰弱或降低死亡。",
              "- 衰弱指数是健康缺陷的累积比例，不是诊断。分数高或近期活动能力明显下降时，可以请医生做老年综合评估。",
              "", "## 说明", "",
              f"- 论文人群：CHARLS {COHORT['baseline_year']} 年基线、随访到 {COHORT['last_wave']} 年的 {COHORT['min_age']} 岁及以上老人；"
              f"衰弱表型样本 {COHORT['n_fp']} 人（{COHORT['fp_deaths']} 人死亡），衰弱指数样本 {COHORT['n_fi']} 人（{COHORT['fi_deaths']} 人死亡）。",
              "- 活动分钟数只算每次连续至少 10 分钟的活动。总活动量的加权是作者的近似，不是正式的 MET 分钟。",
              "- 抑郁情绪类各项的答案按“过去一周几天”换成论文的四级计分，换法见技能的 references/contract.md。"]
    if age is not None and age < COHORT["min_age"]:
        lines.append(f"- 你的年龄 {age:g} 岁，不在论文人群（{COHORT['min_age']} 岁及以上）内。")
    if sex is None:
        lines.append("- 没有给性别，血红蛋白一项（第 46 项）按缺项处理。")
    lines += ["", f"边界: {BOUNDARY}"]
    return lines


def missing_items(r: dict) -> list:
    names = {num: zh for num, _key, zh, _en, _code, _kind in FI_QUESTION_ITEMS}
    names.update({FI_BMI_ITEM: "BMI（体重和身高）", 45: "糖化血红蛋白", 46: "血红蛋白（还需性别）", 47: "C反应蛋白", 48: "血肌酐"})
    return [f"第 {n} 项 {names[n]}" for n in range(1, FI_ITEMS_TOTAL + 1) if n not in r["scores"]]


def write_report(out_dir: Path, measurements: Path | None, age: float | None, sex: str | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = out_dir / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems = list(collected.problems)
    problems += code_problems(manifest, collected.values)
    if age is not None:
        problems += skillkit.check_scalar(manifest, "age", age)
    person_sex = parse_sex(sex)
    if sex and person_sex is None:
        problems.append(skillkit.Problem("sex", "性别", "unit", f"性别写的是“{sex}”，请写男或女，或者不填。"))
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, {spec["key"]: None for spec in manifest["outputs"]})
        return path
    r = assess(dict(collected.values), person_sex)
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(r, person_sex, age)) + "\n"), encoding="utf-8")
    c, fi, fp = r["cats"], r["fi"], r["fp"]
    fig6, fig7 = FIG6_FP_BETA["total"][c["total"]], FIG7_FI_BETA["total"][c["total"]]
    hr1, hr2 = SUPP1_FP_HR_ALL["total"][c["total"]], SUPP2_FI_HR_ALL["total"][c["total"]]
    skillkit.write_result(out_dir, manifest, {
        "total_pa_min_per_week": round(r["minutes"]["total"], 2),
        "total_pa_category": PA_CATEGORY_LABELS[c["total"]],
        "total_pa_meets_150": "是" if r["minutes"]["total"] >= PA_GUIDELINE_MIN - _EPS else "否",
        "hpa_category": PA_CATEGORY_LABELS[c["hpa"]],
        "mpa_category": PA_CATEGORY_LABELS[c["mpa"]],
        "lpa_category": PA_CATEGORY_LABELS[c["lpa"]],
        "fp_beta_total_pa_category": 0.0 if fig6 is None else fig6[0],
        "fi_beta_total_pa_category": 0.0 if fig7 is None else fig7[0],
        "hr_total_pa_category_fp_cohort": 1.0 if hr1 is None else hr1[0],
        "hr_total_pa_category_fi_cohort": 1.0 if hr2 is None else hr2[0],
        "bmi_kg_m2": None if r["bmi"] is None else round(r["bmi"], 2),
        "fi_items_answered": fi["answered"],
        "fi_deficit_sum": round(fi["sum"], 4),
        "frailty_index": None if fi["value"] is None else round(fi["value"], 4),
        "frailty_index_min": round(fi["min"], 4),
        "frailty_index_max": round(fi["max"], 4),
        "frailty_index_category": None if fi["category"] is None else FI_CATEGORY_ZH[fi["category"]],
        "fp_known_points": fp["points"],
        "fp_status": fp["status"],
    })
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path,
                        help="CSV item,value,unit：每周高/中/低强度活动分钟数（必填），衰弱指数问卷答案代码、体重身高、化验（可选）")
    parser.add_argument("--age", type=float)
    parser.add_argument("--sex")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements, args.age, args.sex)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
